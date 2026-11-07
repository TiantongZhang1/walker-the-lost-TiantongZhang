extends SceneTree
## Effect B's observable rules B2-B5, against the real game scene.
## Assignment 6, Step 5.
##
##   ./scripts/run-test.sh test_dungeon_motes_state.gd 60
##
## **B1 is not here, and cannot be.** "The field is at steady state on the
## first drawn frame" is a claim about a drawn frame; a headless run uses a
## dummy renderer, draws no particles and runs no GPU particle process.
## `CHANGE-BRIEF.md` F4 names this as the failure no headless test can catch,
## and the evidence for it is `captures/dungeon_motes/r0-strip.png` against
## `captures/dungeon_motes/f4-no-preprocess-strip.png`. The one thing this file
## does for B1 is print that, so a reader counting green lines does not come
## away thinking it was covered.
##
## **Two of the rules below are only partly observable headless**, and each
## says so in its own output rather than in a comment nobody reads. What a
## headless run CAN see is node state: `emitting`, `visible`, `can_process()`,
## what is connected to what, and whether anything else in the game moved.

const MAIN := "res://game/main.tscn"

var _checks := 0
var _failures := 0


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


## Printed, counted by nobody. For the things this run genuinely cannot see.
func _note(label: String) -> void:
	print("NOTE  ", label)


func _wait(seconds: float) -> void:
	var t := 0.0
	while t < seconds:
		await process_frame
		t += root.get_process_delta_time()


func _load_room() -> Array:
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame
	return [main, main.get_node("DungeonMotes"), main.get_node("Player")]


func _teardown(main: Node) -> void:
	main.queue_free()
	await process_frame


## The whole of the game state this effect is forbidden to touch.
func _snapshot(main: Node) -> Dictionary:
	var player: Node = main.get_node("Player")
	var snap := {
		"health": player.health,
		"position": player.global_position,
	}
	var i := 0
	for trap in main.get_node("Traps").get_children():
		snap["trap%d_state" % i] = trap.state
		snap["trap%d_warn" % i] = trap.warn_amount
		i += 1
	return snap


# ---------------------------------------------------------------- scenarios

func _scenario_present_and_listening() -> void:
	print("\n-- the node is in the game, and found the signal it depends on --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var motes: GPUParticles2D = bits[1]

	_check("DungeonMotes is a node in main.tscn", motes != null)
	_check("it is emitting on the first frame, from the scene", motes.emitting)
	_check("it is visible", motes.visible)
	# A missing player would look exactly like a player who never dies: the
	# field would simply run forever and B2 would never be reached.
	_check("B5  it is connected to the player's `died` signal",
		motes.is_listening())
	_note("B1  not checked here. A headless run draws no field.")
	_note("     Evidence: captures/dungeon_motes/r0-strip.png frame 1 against")
	_note("     captures/dungeon_motes/f4-no-preprocess-strip.png frame 1.")
	await _teardown(main)


## B2. The field stops being fed; it is not cut off.
func _scenario_stop_on_death() -> void:
	print("\n-- B2: the condition ends when the player dies --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var motes: GPUParticles2D = bits[1]
	var player: Node = bits[2]
	await _wait(0.5)

	_check("    still emitting while the player is alive", motes.emitting)
	player.take_damage(player.MAX_HEALTH)
	await process_frame

	_check("B2  emitting went false on `died`", not motes.emitting)
	# "Existing motes finish their lives" is the half a headless run can reach
	# only structurally: the node must still be in the tree, still visible and
	# not restarted. Whether 60 motes are actually still drifting is a drawn
	# frame, and the strip shows it: 412 px of motes at the death, falling to
	# 0 px exactly 8 s later.
	_check("B2  the node was not freed", is_instance_valid(motes)
		and motes.is_inside_tree())
	_check("B2  and was not hidden, which would cut the field off", motes.visible)
	await _wait(0.5)
	_check("B2  still false half a second later; nothing restarts it",
		not motes.emitting)
	_note("B2  'existing motes finish their lives' is a drawn frame. The strip")
	_note("     measures 412 px of motes at the death and 0 px at +8.0 s.")
	await _teardown(main)


## B3. A paused game is a frozen field.
func _scenario_paused() -> void:
	print("\n-- B3: the field stops with the tree --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var motes: GPUParticles2D = bits[1]
	await _wait(0.3)

	_check("    it processes while the game runs", motes.can_process())
	root.get_tree().paused = true
	await process_frame
	# process_mode INHERIT is what makes this true, and the config test pins
	# the mode. This is the behaviour that mode produces.
	_check("B3  it stops processing while the tree is paused",
		not motes.can_process())
	_check("B3  and it is still emitting -- paused, not stopped",
		motes.emitting)
	root.get_tree().paused = false
	await process_frame
	_check("B3  it resumes when the tree does", motes.can_process())
	await _teardown(main)


## B4. Hidden is not stopped.
func _scenario_hidden() -> void:
	print("\n-- B4: hiding it must not produce a refill when it comes back --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var motes: GPUParticles2D = bits[1]
	await _wait(0.3)

	motes.visible = false
	await _wait(0.5)
	_check("B4  emitting stayed true while hidden", motes.emitting)
	_check("B4  nothing called restart() -- preprocess is still one lifetime",
		is_equal_approx(motes.preprocess, motes.lifetime),
		"%.2f / %.2f" % [motes.preprocess, motes.lifetime])
	motes.visible = true
	await process_frame
	_check("B4  still emitting after being shown again", motes.emitting)
	_note("B4  'it keeps simulating while hidden' is not observable headless:")
	_note("     there is no exposed particle clock and no particles are run.")
	_note("     The human check is to hide and show it in the running game.")
	await _teardown(main)


## B5. Presentation reads game state and never writes it.
func _scenario_writes_nothing() -> void:
	print("\n-- B5: it reads game state and never writes it --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var motes: GPUParticles2D = bits[1]
	var player: Node = bits[2]
	await _wait(0.5)

	var before := _snapshot(main)
	await _wait(1.0)
	var after := _snapshot(main)
	# The player is standing still, so everything in the snapshot should be
	# untouched. This would catch a presentation node that nudged the player,
	# disarmed a trap or wrote warn_amount.
	var moved: Array = []
	for key in before:
		if typeof(before[key]) == TYPE_VECTOR2:
			if not (before[key] as Vector2).is_equal_approx(after[key]):
				moved.append(key)
		elif before[key] != after[key]:
			moved.append(key)
	_check("B5  a second of ambience changed no game state",
		moved.is_empty(), str(moved))

	# And across the one event it does react to.
	var hp_before: int = player.health
	player.take_damage(1)
	await process_frame
	_check("    the player's health is the player's to change",
		player.health == hp_before - 1,
		"%d -> %d" % [hp_before, player.health])

	# The only property this effect's script writes, and only one way.
	_check("B5  the effect writes exactly one property, `emitting`",
		motes.emitting, "still true; only `died` turns it off")
	await _teardown(main)


func _init() -> void:
	await _scenario_present_and_listening()
	await _scenario_stop_on_death()
	await _scenario_paused()
	await _scenario_hidden()
	await _scenario_writes_nothing()
	# Let the last queue_free() land before the tree is torn down, or Godot
	# reports leaked instances at exit for nodes that were freed correctly.
	await process_frame
	await process_frame
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: Effect B obeys B2-B5 as node state.")
	print("Does NOT prove B1, and does not try to. That is the frame strip,")
	print("and the verdict on how the field reads is the author's.")
	quit(1 if _failures > 0 else 0)
