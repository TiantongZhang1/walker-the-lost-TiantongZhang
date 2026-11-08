extends SceneTree
## Capture driver for Assignment 6's film. Three takes, each recorded from the
## running game at 3840 x 2160 through Godot's Movie Maker.
##
##   WALKER_TAKE=p godot --path godot --script res://tests/capture_particles.gd \
##       --write-movie out/frame.png --fixed-fps 60 --disable-vsync
##
## Normally invoked through `scripts/render_takes.py`, which also supplies the
## 4K override Movie Maker needs.
##
## **take p - PLAYED.** The only input is held keys, parsed through the real
## input map. Nothing is teleported, no state is written, no effect is poked.
## The player walks east past all three traps, jumps, and walks back west. It
## is the take that shows Effect A on the game's own event, Effect C's trail in
## both facings and its landing puff, and Effect B's field behind all of it.
##
## **take r - SCRIPTED, and labelled as such everywhere it is shown.** It emits
## `fired` on the three traps directly, on a 0.20 s rotation, so that three
## bursts are alive at once. Revision 6.0.2 measured that this cannot be
## produced by playing the room: the traps are 1.17 s apart at walking speed
## and a burst lives 0.60 s. A4's ceiling is real and unreachable, and a film
## that showed this as play would be lying about it.
##
## **take c - CONDITION.** Effect B's three behaviours in one continuous shot:
## the field running, the tree paused (B3 - it freezes with the game), and the
## player killed by standing on a trap (B2 - `emitting` goes false and the
## motes already born finish their lives instead of vanishing).
##
## Every take asserts its own outcome and prints CAPTURE OK only if it holds.
## A completed render is not the claim; that line is.

const MAIN := "res://game/main.tscn"

var _log: Array[String] = []
var _t := 0.0
var _probe: Probe = null


func _init() -> void:
	var take := OS.get_environment("WALKER_TAKE")
	if take == "":
		take = "p"
	if not (take in ["p", "r", "c"]):
		push_error("capture_particles.gd knows takes p, r and c, not %s" % take)
		quit(2)
		return

	var main: Node = (load(MAIN) as PackedScene).instantiate()
	root.add_child(main)
	await process_frame

	_probe = Probe.new()
	_probe.main = main
	_probe.owner_driver = self
	root.add_child(_probe)
	await process_frame

	match take:
		"p":
			await _take_played()
		"r":
			await _take_rapid(main)
		"c":
			await _take_condition()

	_write_log(take)
	_verdict(take, main)


## ---------------------------------------------------------------- take p ---
## Held keys only. The legs come from the room's own geometry: the player
## starts at x 96 and the traps are at 208, 320 and 432, so four seconds at
## SPEED 96 px/s crosses all three.
func _take_played() -> void:
	await _hold(1.0)                      # fall to the floor; B is already full
	await _leg(KEY_D, 4.0)                # x 96 -> 480, three traps fire
	await _hold(0.9)                      # the trail stays where it was born
	_key(KEY_SPACE, true)
	await _hold(0.05)
	_key(KEY_SPACE, false)
	await _leg(KEY_D, 0.9)                # airborne: no strides, then a landing
	await _hold(0.8)
	# West far enough for the mirrored facing and one more trap, and no
	# further: five hits kill this player, and a take that ends with a corpse
	# cannot show Effect C's trail or Effect B still emitting.
	await _leg(KEY_A, 1.5)
	await _hold(1.4)


## ---------------------------------------------------------------- take r ---
## The ceiling, built on purpose. No input at all; `fired` is emitted straight
## at the spawner.
## Twenty rounds, because the beat that shows this has to be able to TALK over
## it. A two-second take under fourteen seconds of narration is twelve seconds
## of frozen frame, which `scripts/build_media_clips.py` pads in as a labelled
## hold and which reads as a still.
func _take_rapid(main: Node) -> void:
	await _hold(1.0)
	var traps: Array = main.get_node("Traps").get_children()
	for round_index in 20:
		for trap in traps:
			trap.fired.emit()
			await _hold(0.20)
	await _hold(2.0)


## ---------------------------------------------------------------- take c ---
func _take_condition() -> void:
	await _hold(1.2)                      # the field, running
	paused = true
	await _hold(1.3)                      # B3: frozen with the game
	paused = false
	await _hold(0.6)
	# Five hits kill this player, and a trap only re-arms on a fresh
	# DetectArea ENTRY -- `spike_trap.gd:125`, rule R3 -- so standing on one
	# does nothing after the first strike. Death has to be walked into, which
	# is what these legs are: east over two traps, west over the same two,
	# east over one more.
	await _leg(KEY_D, 2.6)                # traps 1 and 2
	await _hold(0.6)
	await _leg(KEY_A, 1.9)                # traps 2 and 1 again
	await _hold(0.6)
	await _leg(KEY_D, 1.1)                # trap 1 again
	await _hold(0.6)
	await _leg(KEY_A, 1.1)                # trap 1 once more: the fifth hit
	# B2 in full. A mote lives 8.0 s and the colour ramp holds it at full
	# alpha for 70 % of that, so the field does not begin to thin until about
	# two seconds after the births stop and reaches zero at exactly eight.
	# A three-second tail showed a field that looked unchanged, which is
	# true and useless.
	await _hold(8.6)


## A held key, re-pressed on every single frame.
##
## **Not `_key(code, true)` once.** Godot releases every pressed key when the
## window loses focus, and a 4K Movie Maker take needs a real window for
## several minutes. Click anything else on the desktop during a take written
## that way and the player simply stops walking: the frames keep being
## written, they look perfectly normal, and the only symptom is that the take
## asserts fewer strides than it should. It happened once, on 2026-11-08 --
## take p came back with 1 burst and 9 puffs instead of 4 and 25. Re-pressing
## the key every frame makes the take immune to the focus it does not need.
##
## Safe for `move_left`/`move_right`, which `player.gd` reads through
## `Input.get_axis()`. It would NOT be safe for `jump`, which is read with
## `is_action_just_pressed`, so the jump stays a single press.
func _leg(code: Key, seconds: float) -> void:
	var left := seconds
	while left > 0.0:
		_key(code, true)
		await process_frame
		var d := root.get_process_delta_time()
		left -= d
		_t += d
	_key(code, false)


func _hold(seconds: float) -> void:
	var left := seconds
	while left > 0.0:
		await process_frame
		var d := root.get_process_delta_time()
		left -= d
		_t += d


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()


## Samples once per frame after everything else: the two effect drivers run at
## the default priority and this at 2000, so a count read here is the count
## after this frame's spawns.
class Probe:
	extends Node
	var main: Node = null
	var owner_driver: SceneTree = null

	var fired := [false, false, false]
	var fire_events := 0
	var peak_bursts := 0
	var peak_dust := 0
	var dust_ids := {}
	var burst_ids := {}
	var motes_stopped_at := -1.0
	var faced_left := false
	var faced_right := false
	var paused_frames := 0
	var paused_moved := 0.0
	var rows := 0

	var _spawner: Node = null
	var _steps: Node = null
	var _motes: GPUParticles2D = null
	var _player: Node2D = null
	var _traps: Array = []
	var _paused_ref_x := INF

	func _ready() -> void:
		process_priority = 2000
		# So that a paused tree is still observable from here. It reads and
		# records; it writes nothing, which is why running while paused is
		# safe rather than a way of cheating the pause.
		process_mode = Node.PROCESS_MODE_ALWAYS
		_spawner = main.get_node("HitBurstSpawner")
		_steps = main.get_node("StepDustDriver")
		_motes = main.get_node("DungeonMotes")
		_player = main.get_node("Player")
		_traps = main.get_node("Traps").get_children()
		for trap in _traps:
			trap.fired.connect(_on_fired.bind(trap))

	func _on_fired(trap: Node) -> void:
		fire_events += 1
		var index := _traps.find(trap)
		if index >= 0:
			fired[index] = true

	func _process(_delta: float) -> void:
		rows += 1
		var bursts: int = _spawner.call(&"live_count")
		var dust: int = _steps.call(&"live_count")
		peak_bursts = maxi(peak_bursts, bursts)
		peak_dust = maxi(peak_dust, dust)
		for b in _spawner.call(&"live_bursts"):
			burst_ids[b.get_instance_id()] = true
		for d in _steps.call(&"live_dust"):
			dust_ids[d.get_instance_id()] = true
			if d.scale.x < 0.0:
				faced_left = true
			else:
				faced_right = true
		if not _motes.emitting and motes_stopped_at < 0.0:
			motes_stopped_at = owner_driver.elapsed()
		if owner_driver.tree_is_paused():
			paused_frames += 1
			if _paused_ref_x == INF:
				_paused_ref_x = _player.global_position.x
			paused_moved = maxf(paused_moved,
				absf(_player.global_position.x - _paused_ref_x))
		owner_driver.record(_player.global_position.x, bursts, dust,
			_motes.emitting, _player.health)


func elapsed() -> float:
	return _t


func tree_is_paused() -> bool:
	return paused


func record(x: float, bursts: int, dust: int, motes: bool, health: int) -> void:
	_log.append(JSON.stringify({
		"t": snappedf(_t, 0.0001),
		"player_x": snappedf(x, 0.01),
		"bursts": bursts,
		"dust": dust,
		"motes_emitting": motes,
		"health": health,
	}))


func _write_log(take: String) -> void:
	var dir := OS.get_environment("WALKER_LOG_DIR")
	if dir == "":
		return
	DirAccess.make_dir_recursive_absolute(dir)
	var path := dir.path_join("take-%s-inputs.jsonl" % take)
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("could not write the take log to " + dir)
		return
	f.store_string("\n".join(_log) + "\n")
	f.close()
	print("  log: %s  (%d frames)" % [path, _log.size()])


func _verdict(take: String, main: Node) -> void:
	var player: Node2D = main.get_node("Player")
	var motes: GPUParticles2D = main.get_node("DungeonMotes")
	print("  frames sampled      : %d" % _probe.rows)
	print("  fired events        : %d  %s" % [_probe.fire_events, str(_probe.fired)])
	print("  bursts: peak %d, distinct %d" % [_probe.peak_bursts, _probe.burst_ids.size()])
	print("  step dust: peak %d, distinct %d" % [_probe.peak_dust, _probe.dust_ids.size()])
	print("  facings seen        : right %s  left %s"
		% [_probe.faced_right, _probe.faced_left])
	print("  health              : %d" % player.health)
	print("  motes emitting      : %s" % motes.emitting)
	print("  paused frames       : %d, player moved %.4f px"
		% [_probe.paused_frames, _probe.paused_moved])
	var ok := false
	var why := ""
	match take:
		"p":
			# Played: every trap fired on its own, both facings happened, and
			# the trail is many puffs rather than one.
			ok = _probe.fired[0] and _probe.fired[1] and _probe.fired[2] \
				and _probe.burst_ids.size() >= 3 \
				and _probe.dust_ids.size() >= 12 \
				and _probe.faced_right and _probe.faced_left \
				and motes.emitting
			why = "three traps fired in play, %d bursts, %d puffs, both facings" \
				% [_probe.burst_ids.size(), _probe.dust_ids.size()]
		"r":
			# The ceiling: three alive at the same moment.
			ok = _probe.peak_bursts >= 3 and _probe.burst_ids.size() >= 6
			why = "peak %d bursts alive at once, %d in all (SCRIPTED)" \
				% [_probe.peak_bursts, _probe.burst_ids.size()]
		"c":
			ok = _probe.paused_frames > 30 and _probe.paused_moved < 0.001 \
				and player.health == 0 and not motes.emitting
			why = "paused %d frames with the player at rest, player died, motes off" \
				% _probe.paused_frames
	if ok:
		print("CAPTURE OK  take %s: %s" % [take, why])
		quit(0)
	else:
		print("CAPTURE FAILED  take %s: %s" % [take, why])
		quit(1)
