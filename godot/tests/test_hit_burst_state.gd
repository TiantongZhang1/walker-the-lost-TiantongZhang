extends SceneTree
## Effect A's observable rules A1-A6, against the real game scene.
## Assignment 6, Step 3.
##
##   ./scripts/run-test.sh test_hit_burst_state.gd 60
##
## **This is the state half of the evidence split.** A headless run uses a
## dummy renderer: it draws no particles and runs no GPU particle process, so
## nothing below says anything about what the burst LOOKS like. It says that a
## burst exists, where it exists, whose child it is, how many of them there
## are, and when they stop existing. The look is `captures/hit_burst/` and the
## verdict on it is the author's, in `TUNING.md`.
##
## The walk is driven by synthesized key events through the real game loop, the
## same way `test_trap_warning.gd` drives it, so the count below is the count a
## player produces and not the count a test function produces.
##
## **One scenario here is synthetic and is labelled as such.** A3 needs two
## events 0.20 s apart and `CHANGE-BRIEF.md` revision 6.0.2 establishes that
## walking cannot produce them in this room; that scenario emits `fired`
## directly and says so in its own output.

const MAIN := "res://game/main.tscn"
const FLOOR_Y := 200.0            # CLAUDE.md, the floor line
const BURST_LIFETIME := 0.60      # CHANGE-BRIEF.md 1.3, Grit, the longest

var _checks := 0
var _failures := 0


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()


func _wait(seconds: float) -> void:
	var t := 0.0
	while t < seconds:
		await process_frame
		t += root.get_process_delta_time()


## Loads the real room. Returns [main, traps, spawner]. Does NOT wait for the
## player to settle -- `_scenario_scene_load` needs the first frame.
func _load_room() -> Array:
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame
	var traps := [
		main.get_node("Traps/SpikeTrap1"),
		main.get_node("Traps/SpikeTrap2"),
		main.get_node("Traps/SpikeTrap3"),
	]
	return [main, traps, main.get_node("HitBurstSpawner")]


func _teardown(main: Node) -> void:
	_key(KEY_D, false)
	_key(KEY_A, false)
	main.queue_free()
	await process_frame


## Every HitBurst instance in the tree, found by walking it rather than by
## asking the spawner. A1's "never otherwise" has to be able to fail even if
## the spawner's own bookkeeping is wrong.
func _bursts_in_tree(node: Node, found: Array) -> Array:
	for child in node.get_children():
		if child.has_method("fire") and child.has_method("lifetime"):
			found.append(child)
		_bursts_in_tree(child, found)
	return found


# ---------------------------------------------------------------- scenarios

## A1, the half that is easy to get wrong: three traps exist on load and none
## of them has fired, so there must be no burst anywhere.
func _scenario_scene_load() -> void:
	print("\n-- A1: nothing fires on scene load --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var spawner: Node = bits[2]

	_check("the spawner found its room and its traps", spawner != null)
	_check("A1  spawner reports 0 live bursts on the frame after _ready()",
		spawner.live_count() == 0, str(spawner.live_count()))
	var found: Array = _bursts_in_tree(main, [])
	_check("A1  and no burst exists anywhere in the tree", found.is_empty(),
		"%d found" % found.size())

	# Three traps really are present and really are armed, or the check above
	# passes for the wrong reason.
	var armed := 0
	for trap in bits[1]:
		if trap.state == SpikeTrap.State.ARMED:
			armed += 1
	_check("    all three traps are present and ARMED", armed == 3,
		"%d of 3" % armed)
	await _teardown(main)


## A1 fires on every event, A2 position, A5 parent, A4's observed ceiling.
## One walk left to right, through all three detection zones, with real input.
func _scenario_walk() -> void:
	print("\n-- A1/A2/A5/A4: one walk, three traps, real input --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var spawner: Node = bits[2]
	await _wait(0.6)  # let the player fall and settle on the floor

	var events: Array = []     # one row per `fired`, appended by the handler
	for trap in traps:
		trap.fired.connect(_on_fired.bind(trap, spawner, main, events))

	var max_live := 0
	var player: Node = main.get_node("Player")
	_key(KEY_D, true)
	var travelled := 0.0
	while travelled < 8.0 and player.global_position.x < 520.0:
		await process_frame
		travelled += root.get_process_delta_time()
		max_live = maxi(max_live, spawner.live_count())
	_key(KEY_D, false)

	_check("    the player walked past all three traps",
		player.global_position.x >= 460.0,
		"ended at x %.0f after %.2f s" % [player.global_position.x, travelled])
	_check("A1  one burst per `fired`, three traps, three bursts",
		events.size() == 3, "%d events" % events.size())

	var missing := 0
	for row in events:
		if not row["produced"]:
			missing += 1
	_check("A1  every event produced an instance in the same frame",
		missing == 0, "%d event(s) produced none" % missing)

	# A2 and A5 are read off the numbers the handler recorded AT THE EVENT,
	# never off a stored node reference. The first version of this scenario
	# kept the instance and measured it after the walk; by then all three had
	# freed themselves, a freed reference compares equal to null in GDScript,
	# and the loop skipped every row -- so A2 and A5 reported "worst 0.000 px"
	# and passed having measured nothing at all. Three green lines, zero
	# evidence. `missing` above is what turned it red.
	var worst_dx := 0.0
	var worst_dy := 0.0
	var wrong_parent := 0
	var measured := 0
	for row in events:
		if not row["produced"]:
			continue
		measured += 1
		worst_dx = maxf(worst_dx, row["dx"])
		worst_dy = maxf(worst_dy, row["dy"])
		if not row["parented_to_room"]:
			wrong_parent += 1
	_check("    three bursts were actually measured, not zero",
		measured == 3, "%d measured" % measured)
	_check("A2  every burst is at its trap's x, within 1 px",
		measured == 3 and worst_dx <= 1.0, "worst %.3f px" % worst_dx)
	_check("A2  and at the floor line y = %.0f, within 1 px" % FLOOR_Y,
		measured == 3 and worst_dy <= 1.0, "worst %.3f px" % worst_dy)
	_check("A5  every burst is parented to the room, not to the trap",
		measured == 3 and wrong_parent == 0,
		"%d parented elsewhere" % wrong_parent)

	# CHANGE-BRIEF.md revision 6.0.2. The ceiling of 3 is real and this walk
	# cannot reach it: the traps are 112 px apart and the player moves at
	# 96 px/s, so consecutive events are 1.17 s apart and a burst lives 0.60 s.
	# The assertion below would pass at any max from 0 to 3, so the OBSERVED
	# maximum is printed beside it -- a reader can then see that the walk
	# reached 1, which is the honest result, rather than reading a green line
	# as evidence that overlap was exercised. It was not; A3 does that.
	_check("A4  live count never exceeded the ceiling of 3", max_live <= 3,
		"observed maximum: %d" % max_live)
	_check("    and the walk reached 1, not 3, as revision 6.0.2 predicts",
		max_live == 1, "observed maximum: %d" % max_live)
	await _teardown(main)


## Connected after the spawner's own handler, so the instance it just made is
## already the last entry in `live_bursts()`.
##
## Everything A2 and A5 need is read here, while the instance is alive, and
## stored as plain numbers and booleans. Nothing in `events` is a node.
func _on_fired(trap: Node2D, spawner: Node, room: Node, events: Array) -> void:
	var live: Array = spawner.live_bursts()
	var burst: Node2D = null if live.is_empty() else live[live.size() - 1]
	events.append({
		"produced": burst != null,
		"dx": 0.0 if burst == null 			else absf(burst.global_position.x - trap.global_position.x),
		"dy": 0.0 if burst == null 			else absf(burst.global_position.y - FLOOR_Y),
		"parented_to_room": burst != null and burst.get_parent() == room,
		"count": live.size(),
	})


## A3. **Synthetic**: these two events cannot be produced by walking.
func _scenario_overlap() -> void:
	print("\n-- A3: two events 0.20 s apart  [SYNTHETIC - see revision 6.0.2] --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var spawner: Node = bits[2]
	await _wait(0.6)

	traps[0].fired.emit()
	await process_frame
	var first_live: Array = spawner.live_bursts()
	_check("    the first event produced one instance", first_live.size() == 1,
		str(first_live.size()))
	var first: Node = null if first_live.is_empty() else first_live[0]
	var first_id: int = 0 if first == null else first.get_instance_id()

	await _wait(0.20)
	traps[1].fired.emit()
	await process_frame

	var live: Array = spawner.live_bursts()
	_check("A3  both instances are alive; nothing was dropped",
		live.size() == 2, "%d alive" % live.size())
	_check("A3  the first instance is the same object it was",
		first != null and is_instance_valid(first)
			and first.get_instance_id() == first_id)

	# "The first one's particles were not reset" -- a design that reused one
	# node would show one instance whose clock had gone back to zero. Here the
	# older instance's clock is ahead of the younger one's by the gap.
	if live.size() == 2:
		var a: float = live[0].elapsed()
		var b: float = live[1].elapsed()
		_check("A3  the older instance was not restarted by the second event",
			a - b >= 0.15, "elapsed %.3f s vs %.3f s" % [a, b])
	await _teardown(main)


## A6. Nothing survives its own lifetime.
func _scenario_frees_itself() -> void:
	print("\n-- A6: every instance frees itself --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var spawner: Node = bits[2]
	await _wait(0.6)

	traps[0].fired.emit()
	await process_frame
	_check("    one instance alive right after the event",
		spawner.live_count() == 1, str(spawner.live_count()))
	if spawner.live_count() != 1:
		await _teardown(main)
		return

	var burst: Node = spawner.live_bursts()[0]
	_check("    its lifetime is read from the scene, not typed",
		is_equal_approx(burst.lifetime(), BURST_LIFETIME),
		"%.3f s" % burst.lifetime())

	# Half-way: still there. Without this the next check would pass for a
	# burst that was never created.
	await _wait(BURST_LIFETIME * 0.5)
	_check("    still alive half-way through its life",
		spawner.live_count() == 1, str(spawner.live_count()))

	var waited := BURST_LIFETIME * 0.5
	while waited < 0.70 and spawner.live_count() > 0:
		await process_frame
		waited += root.get_process_delta_time()
	_check("A6  count is back to 0 within 0.70 s of the event",
		spawner.live_count() == 0, "gone after %.3f s" % waited)
	var found: Array = _bursts_in_tree(main, [])
	_check("A6  and the node is out of the tree, not just off the list",
		found.is_empty(), "%d still in tree" % found.size())
	await _teardown(main)


func _init() -> void:
	await _scenario_scene_load()
	await _scenario_walk()
	await _scenario_overlap()
	await _scenario_frees_itself()
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: Effect A obeys A1-A6 as game state.")
	print("Proves nothing about what it looks like - that is captures/hit_burst/,")
	print("and the verdict on it is the author's, in TUNING.md.")
	quit(1 if _failures > 0 else 0)
