extends SceneTree
## CHANGE-BRIEF.md rules R1-R6, checked against the real scene.
##
## The state is driven by synthesized key events through the real game loop,
## never by calling SpikeTrap's update directly, because a test that calls the
## update function stops caring what the frame rate is - which is the exact
## mistake Assignment 5 lists as having happened in the runs behind Chapter 6.
##
## Run at every pinned frame rate:
##   ./scripts/run-test.sh test_trap_warning.gd 30
##   ./scripts/run-test.sh test_trap_warning.gd 60
##   ./scripts/run-test.sh test_trap_warning.gd 144
##
## This test does NOT touch a shader or a material. It checks the game state
## the shader will later read. What it cannot show: anything about colour.

const MAIN := "res://game/main.tscn"
const WARN := 0.45  # SpikeTrap.WARN_SECONDS

var _checks := 0
var _failures := 0
var _fps := 60.0


## Samples the traps after every other _process in the frame.
class Sampler:
	extends Node
	var traps: Array = []
	var t := 0.0
	var log: Array = []

	func _ready() -> void:
		process_priority = 1000

	func _process(delta: float) -> void:
		t += delta
		var row := [t]
		for trap in traps:
			row.append(trap.warn_amount)
		log.append(row)


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	var line := "PASS  " if ok else "FAIL  "
	print(line, label, "" if detail == "" else "   [" + detail + "]")


func _near(a: float, b: float, tol: float) -> bool:
	return absf(a - b) <= tol


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


## Steps frames until `cond` returns true. Returns the game time it took, or
## -1.0 on timeout.
func _until(cond: Callable, limit := 6.0) -> float:
	var t := 0.0
	while t < limit:
		if cond.call():
			return t
		await process_frame
		t += root.get_process_delta_time()
	return -1.0


func _load_room() -> Array:
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame
	var traps := [
		main.get_node("Traps/SpikeTrap1"),
		main.get_node("Traps/SpikeTrap2"),
		main.get_node("Traps/SpikeTrap3"),
	]
	var sampler := Sampler.new()
	sampler.traps = traps
	root.add_child(sampler)
	await _wait(0.6)  # let the player fall and settle on the floor
	return [main, traps, sampler]


func _teardown(main: Node, sampler: Node) -> void:
	_key(KEY_D, false)
	_key(KEY_A, false)
	sampler.queue_free()
	main.queue_free()
	await process_frame


# ---------------------------------------------------------------- scenarios

## R1, R2, R6: walk into trap 1 and measure the window.
func _scenario_walk_in() -> void:
	print("\n-- R1/R2/R6: walk into trap 1 --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var t1: SpikeTrap = traps[0]

	_check("R1  armed trap reads 0.0", is_zero_approx(t1.warn_amount))

	_key(KEY_D, true)
	var walked := await _until(_is_warning.bind(t1))
	_check("    player reached trap 1 by walking", walked >= 0.0,
		"%.2f s of travel" % walked)
	_key(KEY_D, false)

	_check("R1  first warning frame is 0.0", t1.warn_amount < 0.12,
		"warn_amount=%.4f" % t1.warn_amount)
	_check("R6  trap 2 unaffected", is_zero_approx(traps[1].warn_amount))
	_check("R6  trap 3 unaffected", is_zero_approx(traps[2].warn_amount))

	var first_row := sampler.log.size()
	var dur := await _until(_is_firing.bind(t1))
	var peak := _peak_since(sampler, first_row, 1)

	var frame := 1.0 / _fps
	_check("R2  window lasted %.3f s (want %.3f +- %.4f)" % [dur, WARN, frame],
		_near(dur, WARN, frame * 1.5), "one frame = %.4f s" % frame)
	_check("R1  reaches 1.0 at FIRING", _near(t1.warn_amount, 1.0, 0.001),
		"warn_amount=%.4f" % t1.warn_amount)
	_check("    ramp peaked just under 1.0 before firing", peak <= 1.0 and peak > 0.80,
		"peak=%.4f" % peak)
	await _teardown(main, sampler)


## R3: a second entry mid-window restarts it.
func _scenario_retrigger() -> void:
	print("\n-- R3: retrigger restarts the window --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var t1: SpikeTrap = traps[0]

	_key(KEY_D, true)
	await _until(_is_warning.bind(t1))

	# Keep walking: the player crosses the trigger and leaves it.
	var left := await _until(_is_clear_of.bind(t1), 1.0)
	var before_restart: float = t1.warn_amount
	var remaining_before: float = t1.warning_remaining()
	_check("    player walked out of the trigger mid-window", left >= 0.0,
		"warn_amount was %.3f" % before_restart)

	# Turn around and walk back in.
	_key(KEY_D, false)
	_key(KEY_A, true)
	var back := await _until(_is_touching.bind(t1), 1.0)
	await process_frame
	_key(KEY_A, false)

	_check("R3  re-entry reset warn_amount toward 0", t1.warn_amount < before_restart,
		"%.3f -> %.3f" % [before_restart, t1.warn_amount])
	_check("R3  the window was restarted, not extended",
		t1.warning_remaining() > remaining_before,
		"remaining %.3f -> %.3f" % [remaining_before, t1.warning_remaining()])
	_check("    re-entry happened inside the window", back >= 0.0)
	await _teardown(main, sampler)


## R5: the state ending early snaps the uniform to 0 with no fade.
func _scenario_early_end() -> void:
	print("\n-- R5: disarm mid-window --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var t1: SpikeTrap = traps[0]

	_key(KEY_D, true)
	await _until(_is_warning.bind(t1))
	_key(KEY_D, false)
	await _wait(0.20)
	var mid: float = t1.warn_amount
	_check("    ramp was part-way up before disarm", mid > 0.2 and mid < 1.0,
		"warn_amount=%.3f" % mid)

	t1.disarm()
	_check("R5  snaps to 0.0 in the same frame", is_zero_approx(t1.warn_amount))
	await process_frame
	_check("R5  still 0.0 on the next frame, no fade",
		is_zero_approx(t1.warn_amount), "warn_amount=%.4f" % t1.warn_amount)
	await _teardown(main, sampler)


## R4: the duration is the same game time under Engine.time_scale.
func _scenario_time_scale() -> void:
	print("\n-- R4: Engine.time_scale = 0.5 --")
	Engine.time_scale = 0.5
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var t1: SpikeTrap = traps[0]

	_key(KEY_D, true)
	await _until(_is_warning.bind(t1), 12.0)
	_key(KEY_D, false)
	var dur := await _until(_is_firing.bind(t1), 12.0)
	var frame := 1.0 / _fps
	_check("R4  window is still %.3f s of GAME time at time_scale 0.5" % WARN,
		_near(dur, WARN, frame * 1.5), "measured %.4f s" % dur)
	Engine.time_scale = 1.0
	await _teardown(main, sampler)


func _is_warning(trap: Node) -> bool:
	return trap.state == SpikeTrap.State.WARNING


func _is_firing(trap: Node) -> bool:
	return trap.state == SpikeTrap.State.FIRING


func _is_touching(trap: Node) -> bool:
	return _overlapping(trap)


## Still inside the warning window, but the player has left the trigger.
func _is_clear_of(trap: Node) -> bool:
	return trap.warning_remaining() >= 0.0 and not _overlapping(trap)


## Highest warn_amount for `column` in the sampler log from `from_row` on.
func _peak_since(sampler: Sampler, from_row: int, column: int) -> float:
	var peak := 0.0
	for i in range(from_row, sampler.log.size()):
		peak = maxf(peak, sampler.log[i][column])
	return peak


func _overlapping(trap: Node) -> bool:
	var area: Area2D = trap.get_node("TriggerArea")
	return area.get_overlapping_bodies().size() > 0


# -------------------------------------------------------------------- entry

func _init() -> void:
	_fps = float(Engine.max_fps) if Engine.max_fps > 0 else 60.0
	print("test_trap_warning  —  pinned at %d fps, one frame = %.4f s"
		% [int(_fps), 1.0 / _fps])

	await _scenario_walk_in()
	await _scenario_retrigger()
	await _scenario_early_end()
	await _scenario_time_scale()

	print("\n%d checks, %d failures" % [_checks, _failures])
	print("Proves: the game state behind the effect. Proves nothing about colour —")
	print("a headless run draws nothing. The look is checked by hand in TEST-REPORT.md.")
	quit(1 if _failures > 0 else 0)
