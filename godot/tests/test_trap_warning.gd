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
const WARN := 0.40  # SpikeTrap.WARN_SECONDS, revision 5.0.3

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
	# The brief's tolerance is ONE frame period. The ramp is checked once per
	# _process, so the window ends on the first frame at or past WARN_SECONDS
	# and the overshoot is bounded by exactly that. The 1 ms is for the
	# non-uniform frames at 144 fps, not slack.
	_check("R2  window lasted %.3f s (want %.3f +- %.4f)" % [dur, WARN, frame],
		_near(dur, WARN, frame + 0.001), "one frame = %.4f s" % frame)
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

	# The detection zone is 48 px wide and takes 0.6 s to walk across, which is
	# longer than the window, so the player cannot leave by the far side in
	# time. Reverse out of the near edge instead - a few frames either way.
	_key(KEY_D, false)
	_key(KEY_A, true)
	var left := await _until(_is_clear_of.bind(t1), 1.0)
	var before_restart: float = t1.warn_amount
	var remaining_before: float = t1.warning_remaining()
	_check("    player reversed out of the detection zone mid-window", left >= 0.0,
		"warn_amount was %.3f" % before_restart)

	# Walk forward into it again.
	_key(KEY_A, false)
	_key(KEY_D, true)
	var back := await _until(_is_touching.bind(t1), 1.0)
	await process_frame
	_key(KEY_D, false)

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
		_near(dur, WARN, frame + 0.001), "measured %.4f s" % dur)
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


## DetectArea's width is derived from WARN_SECONDS, and the three zones must
## not overlap or R6 cannot fail. Both are asserted here, so changing the
## warning length without changing the shape is caught by the suite instead of
## by someone noticing the trap feels wrong.
func _scenario_geometry() -> void:
	print("
-- geometry: the derivation, and the zones --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var player: Node = main.get_node("Player")

	var half: float = _detect_half(traps[0])
	var want: float = player.SPEED * WARN - 5.0
	_check("    DetectArea half-width matches SPEED * WARN - player half",
		absf(half - want) <= 1.0,
		"shape says %.1f px, derivation says %.1f px" % [half, want])

	var zones: Array = []
	for trap in traps:
		var cx: float = trap.global_position.x
		var h: float = _detect_half(trap)
		zones.append([cx - h, cx + h])
	var clear := true
	for i in range(zones.size() - 1):
		if zones[i + 1][0] <= zones[i][1]:
			clear = false
	_check("R6  the three detection zones do not overlap", clear,
		"%.0f..%.0f  %.0f..%.0f  %.0f..%.0f" % [
			zones[0][0], zones[0][1], zones[1][0], zones[1][1],
			zones[2][0], zones[2][1]])
	await _teardown(main, sampler)


func _detect_half(trap: Node) -> float:
	var cs: CollisionShape2D = trap.get_node("DetectArea/CollisionShape2D")
	return (cs.shape as RectangleShape2D).size.x * 0.5


## The check this suite did not have, and should have. Revision 5.0.1's trap
## could never hit anyone: its 16 px trigger took 0.27 s to cross and its
## warning was 0.45 s, so the spikes always arrived after the player had gone.
## Sixteen checks passed anyway, because every one of them measured the timing
## of the warning and none asked whether the trap worked.
func _scenario_actually_hits() -> void:
	print("
-- F6: a player who keeps walking is hit --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var t1: SpikeTrap = traps[0]
	var player: Node = main.get_node("Player")
	var hp_before: int = player.health

	# Walk in and DO NOT stop or react.
	_key(KEY_D, true)
	await _until(_is_warning.bind(t1))
	var dx_at_warn: float = player.global_position.x - t1.global_position.x
	await _until(_is_firing.bind(t1))
	var dx_at_fire: float = player.global_position.x - t1.global_position.x
	await process_frame
	_key(KEY_D, false)

	_check("F6  player was still short of the trap when it warned",
		dx_at_warn < -20.0, "dx = %+.1f px" % dx_at_warn)
	_check("F6  player is over the trap when the spikes arrive",
		absf(dx_at_fire) < 13.0, "dx = %+.1f px (hurt box +-13)" % dx_at_fire)
	_check("F6  the trap actually took a life",
		player.health == hp_before - 1,
		"health %d -> %d" % [hp_before, player.health])
	await _teardown(main, sampler)


func _overlapping(trap: Node) -> bool:
	var area: Area2D = trap.get_node("DetectArea")
	return area.get_overlapping_bodies().size() > 0


## Standing on the trap itself, not merely noticed by it.
func _on_the_trap(trap: Node) -> bool:
	var area: Area2D = trap.get_node("HurtArea")
	return area.get_overlapping_bodies().size() > 0


# -------------------------------------------------------------------- entry

## The rate the engine is ACTUALLY running at.
##
## This used to read Engine.max_fps, which --fixed-fps does not set, so every
## run believed it was at 60 regardless. The tolerance was then 2x too tight
## at 30 fps and 3.6x too loose at 144 - strict enough to fail a correct
## result, and slack enough to pass a wrong one.
##
## --fixed-fps is consumed by the engine and never appears in
## OS.get_cmdline_args(), so scripts/run-test.sh passes it as TEST_FPS. That
## is cross-checked against the engine's own delta.
##
## The delta is sampled as a MODE over many frames, not from one or two. At
## --fixed-fps 144 the frames are not uniform: 1/144 s is 6944.44 us and Godot
## works in whole microseconds, so the delta alternates between 0.006944
## (144 fps) and 0.006667 (150 fps) with the occasional 0.008. A two-frame
## sample caught one of those outliers and reported 120 fps.
func _resolve_fps() -> void:
	var declared := float(OS.get_environment("TEST_FPS"))
	for i in 5:
		await process_frame
	var counts := {}
	for i in 40:
		await process_frame
		var key := "%.6f" % root.get_process_delta_time()
		counts[key] = counts.get(key, 0) + 1
	var best := ""
	var best_n := 0
	for k in counts:
		if counts[k] > best_n:
			best_n = counts[k]
			best = k
	var measured := 1.0 / float(best)

	_fps = declared if declared > 0.0 else measured
	print("test_trap_warning  —  TEST_FPS=%d, engine modal delta %s (%.1f fps, %d/40 frames)"
		% [int(declared), best, measured, best_n])
	print("                      one frame = %.4f s" % (1.0 / _fps))
	_check("    declared and measured frame rate agree",
		declared > 0.0 and absf(declared - measured) / declared < 0.01,
		"TEST_FPS=%.0f, modal delta implies %.1f" % [declared, measured])


func _init() -> void:
	await _resolve_fps()

	await _scenario_walk_in()
	await _scenario_retrigger()
	await _scenario_early_end()
	await _scenario_time_scale()
	await _scenario_actually_hits()
	await _scenario_geometry()

	print("\n%d checks, %d failures" % [_checks, _failures])
	print("Proves: the game state behind the effect. Proves nothing about colour —")
	print("a headless run draws nothing. The look is checked by hand in TEST-REPORT.md.")
	quit(1 if _failures > 0 else 0)
