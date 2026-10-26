extends SceneTree
## Capture driver for Assignment 5's film. One take, recorded as real motion.
##
##   WALKER_TAKE=w godot --path godot --script res://tests/capture_shader.gd \
##       --write-movie out/frame.png --fixed-fps 60 --disable-vsync
##
## Normally invoked through `scripts/render_takes.py`, which also supplies the
## 4K override Movie Maker needs.
##
## take w - the warning, three times over
##   The player walks east at a constant 96 px/s through all three traps. Each
##   one notices them, ramps warn_amount 0 -> 1 across WARN_SECONDS, fires, and
##   retracts. Nothing is teleported and no state is written: the only input is
##   a held key, parsed through the real input map, and every number below is
##   read back out of the running game.
##
## What the take has to prove, and asserts for itself:
##   - each trap reached FIRING, so the warning is followed by a strike
##   - the player lost health, so the warning could be failed
##   - while one trap was warning, the other two read exactly 0.0 - R6, in
##     motion, rather than as a headless assertion
##
## A completed render is not the claim. The CAPTURE OK line is, and it is only
## printed when all three hold.

const MAIN := "res://game/main.tscn"
const SETTLE_S := 1.0
## Walk, stop, walk, stop. The pauses are not padding: at a constant 96 px/s
## the player crosses all three detection zones in under four seconds, and a
## result beat then has one second of footage under twenty seconds of
## narration. Stopping between traps lets each cycle finish on screen and
## gives the film something to hold on. The player still only ever walks -
## the pauses are the key being released, nothing is slowed or retimed.
const LEGS: Array[float] = [1.45, 1.30, 1.30]
const PAUSE_S := 1.9
const TAIL_S := 1.0

var _log: Array[String] = []
var _t := 0.0


func _init() -> void:
	var take := OS.get_environment("WALKER_TAKE")
	if take == "":
		take = "w"
	if take != "w":
		push_error("capture_shader.gd knows only take w, not %s" % take)
		quit(2)
		return

	var main: Node = (load(MAIN) as PackedScene).instantiate()
	root.add_child(main)
	await process_frame
	var traps: Array[SpikeTrap] = [
		main.get_node("Traps/SpikeTrap1"),
		main.get_node("Traps/SpikeTrap2"),
		main.get_node("Traps/SpikeTrap3"),
	]
	var player: Node2D = main.get_node("Player")
	var hp_before: int = player.health

	# Highest of anything, so the sample is taken after the state machines and
	# after the material drivers have written this frame's uniforms.
	var probe := Probe.new()
	probe.traps = traps
	probe.player = player
	probe.owner_driver = self
	root.add_child(probe)

	await _hold(SETTLE_S)
	for leg in LEGS:
		_key(KEY_D, true)
		await _hold(leg)
		_key(KEY_D, false)
		await _hold(PAUSE_S)
	await _hold(TAIL_S)

	_write_log()
	_verdict(probe, hp_before, player)


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


## Samples after every other _process in the frame: SpikeTrap is 0, the
## material driver 100, this 2000.
class Probe:
	extends Node
	var traps: Array[SpikeTrap] = []
	var player: Node2D = null
	var owner_driver: SceneTree = null
	var fired := [false, false, false]
	var r6_violations := 0
	var peak_other := 0.0
	var rows := 0

	func _ready() -> void:
		process_priority = 2000

	func _process(_delta: float) -> void:
		rows += 1
		var amounts: Array[float] = []
		for i in 3:
			amounts.append(traps[i].warn_amount)
			if traps[i].state == SpikeTrap.State.FIRING:
				fired[i] = true
		# R6, frame by frame: at most one trap may be lit at a time, and the
		# two that are not the player's business must read exactly 0.0.
		var lit := 0
		for a in amounts:
			if a > 0.0:
				lit += 1
		if lit > 1:
			r6_violations += 1
		for i in 3:
			if amounts[i] > 0.0 and lit == 1:
				continue
			peak_other = maxf(peak_other, amounts[i] if lit > 1 else 0.0)
		owner_driver.record(amounts)


func record(amounts: Array[float]) -> void:
	var probe_player: Node2D = root.get_node_or_null("Main/Player")
	var x := 0.0 if probe_player == null else probe_player.global_position.x
	_log.append(JSON.stringify({
		"t": snappedf(_t, 0.0001),
		"player_x": snappedf(x, 0.01),
		"warn": [snappedf(amounts[0], 0.0001), snappedf(amounts[1], 0.0001),
			snappedf(amounts[2], 0.0001)],
	}))


func _write_log() -> void:
	var dir := OS.get_environment("WALKER_LOG_DIR")
	if dir == "":
		return
	DirAccess.make_dir_recursive_absolute(dir)
	# The name the rest of the chain looks for: encode_captures.py and
	# coverage both expect take-<letter>-inputs.jsonl beside the frames.
	var path := dir.path_join("take-w-inputs.jsonl")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("could not write the take log to " + dir)
		return
	f.store_string("\n".join(_log) + "\n")
	f.close()
	print("  log: %s  (%d frames)" % [path, _log.size()])


func _verdict(probe: Probe, hp_before: int, player: Node2D) -> void:
	var all_fired: bool = probe.fired[0] and probe.fired[1] and probe.fired[2]
	var hp_after: int = player.health
	var lost := hp_before - hp_after
	print("  frames sampled     : %d" % probe.rows)
	print("  traps that fired   : %s" % str(probe.fired))
	print("  health             : %d -> %d" % [hp_before, hp_after])
	print("  frames with >1 trap lit : %d" % probe.r6_violations)
	var ok := all_fired and lost > 0 and probe.r6_violations == 0
	if ok:
		print("CAPTURE OK  take w: three warnings, %d hit(s), R6 held every frame" % lost)
		quit(0)
	else:
		print("CAPTURE FAILED  take w")
		quit(1)
