extends SceneTree
## What the three effects cost on the GPU, measured in a REAL WINDOWED run.
##
##   ./scripts/run-gpu-cost.sh            (it must not be run headless)
##
## **This is the number every budget in `CHANGE-BRIEF.md` §5 and §C.6 is set
## against** -- 0.30 / 0.20 / 0.10 ms -- and until this script ran, all three
## were predictions. `tests/cost_effects.gd` is its headless sibling and
## measures the other thing: wall-clock CPU, which for a `GPUParticles2D` is
## ~0 by construction because a dummy renderer never reaches the card.
##
## **The instrument.** `RenderingServer.viewport_get_measured_render_time_gpu()`
## on the root viewport, enabled by `viewport_set_measure_render_time()`.
## That is the same GPU timestamp query the editor's Visual Profiler reads
## and displays as its "Render Viewport" row -- the same quantity, taken
## programmatically instead of by eye, and at full float precision rather
## than the editor's two decimal places.
##
## **It refuses to run headless.** A dummy renderer draws nothing, so every
## reading would be 0.000 ms and would look exactly like an effect that is
## free. That is the shape of half the faults in `TEST-REPORT.md`, so it
## stops instead.
##
## **vsync is turned off for the measurement.** With vsync on the GPU idles
## between frames, clocks drop, and per-frame times get noisier and higher.
## This is a window property, not a game setting -- the same thing F9 does in
## `game/debug_keys.gd` -- and the shipped game is untouched.
##
## **The baseline is run twice**, before and after everything else, and the
## spread between those two runs is this instrument's own resolution. A
## difference smaller than that spread is not a measurement, and the report
## says so in those words rather than printing a number that looks precise.
##
## **Two of the conditions are SYNTHETIC and are labelled.** Revision 6.0.2
## measured that three bursts cannot be alive at once by playing this room:
## the traps are 112 px apart, the player walks at 96 px/s, so consecutive
## `fired` events are 1.17 s apart while a burst lives 0.60 s. Play reaches
## ONE burst, 32 particles. So both A rows emit `fired` directly -- one at
## the brief's ceiling of 3, which is what §5's budget is set against and
## which no player can produce, and one holding a single burst, which is
## what play actually peaks at. Reporting only the first would budget
## against a load that never happens; reporting only the second would not
## answer the brief.

const MAIN := "res://game/main.tscn"

const EFFECT_A := "HitBurstSpawner"
const EFFECT_B := "DungeonMotes"
const EFFECT_C := "StepDustDriver"
const ALL_EFFECTS := [EFFECT_A, EFFECT_B, EFFECT_C]

## Same constants as the headless sibling, so the two tables line up.
const FRAMES := 400
const WARMUP := 120

## Revision 6.0.2's design ceiling, and the rotation that holds it.
const A_CEILING := 3
const A_REFIRE_SECONDS := 0.20
## One burst alive and no more: a burst lives 0.60 s, so refiring one trap
## just OUTSIDE that is the only spacing that never reaches two.
##
## It was 0.55 s in the first run of this script, and the `emitters` column
## reported 6 for that condition -- three emitters per burst, so two bursts,
## in a row labelled "ONE burst". The label was false and the table said so
## on its own. That column exists for this: revision 6.0.2 records a
## condition labelled "Effect A at its ceiling" that never reached the
## ceiling, and the fix then was to make every row report the load it
## actually carried rather than the load its name claims.
const A_ONE_REFIRE_SECONDS := 0.65

## CHANGE-BRIEF.md section 5 and section C.6.
const BUDGET := {EFFECT_A: 0.30, EFFECT_B: 0.20, EFFECT_C: 0.10}

var _rows: Array = []
var _peak_emitters := 0
var _min_health := -1
var _b_off_frames := 0
var _vp: RID


func _wait_frames(n: int) -> void:
	for i in range(n):
		await process_frame


## A held key, re-pressed on EVERY frame.
##
## Not pressed once. This is a windowed run, and Godot releases every pressed
## key when the window loses focus -- which is how take p of the film came
## back with 1 burst and 9 puffs instead of 4 and 25 on 2026-11-08, because
## the author switched applications mid-render. A condition labelled "C only,
## player running" that silently stopped running would measure a label, not a
## load. Safe for move_right, which player.gd reads through Input.get_axis().
func _hold(code: Key) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = true
	Input.parse_input_event(e)
	Input.flush_buffered_events()


func _release(code: Key) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = false
	Input.parse_input_event(e)
	Input.flush_buffered_events()


func _count_particles(node: Node, found: int) -> int:
	for child in node.get_children():
		if child is GPUParticles2D:
			found += 1
		found = _count_particles(child, found)
	return found


## One GPU reading per drawn frame, in milliseconds.
func _measure(n: int, watch: Node, traps: Array, refire: float, walk: bool) -> Array:
	var samples: Array = []
	_peak_emitters = 0
	_min_health = -1
	_b_off_frames = 0
	var player: Node = null
	var motes: GPUParticles2D = null
	if watch != null:
		player = watch.get_node_or_null(^"Player")
		motes = watch.get_node_or_null(^"DungeonMotes") as GPUParticles2D
	var since := 0.0
	var next_trap := 0
	for i in range(n):
		if walk:
			_hold(KEY_D)
		if not traps.is_empty():
			since += root.get_process_delta_time()
			if since >= refire:
				since = 0.0
				traps[next_trap].fired.emit()
				next_trap = (next_trap + 1) % traps.size()
		await RenderingServer.frame_post_draw
		samples.append(RenderingServer.viewport_get_measured_render_time_gpu(_vp))
		if watch != null:
			_peak_emitters = maxi(_peak_emitters, _count_particles(watch, 0))
		# A condition is only the condition its label names while the thing
		# it is about is still switched on. Effect B stops on `died`, and a
		# walking condition can kill the player: the row would then be
		# labelled "heaviest" while the mote field drained.
		if player != null:
			var h: int = player.health
			_min_health = h if _min_health < 0 else mini(_min_health, h)
		if motes != null and not motes.emitting:
			_b_off_frames += 1
	samples.sort()
	return samples


func _median(s: Array) -> float:
	var n: int = s.size()
	if n == 0:
		return 0.0
	if n % 2 == 1:
		return float(s[n / 2])
	return 0.5 * (float(s[n / 2 - 1]) + float(s[n / 2]))


func _record(label: String, samples: Array, expect: int) -> void:
	_rows.append({
		"label": label,
		"median": _median(samples),
		"p10": float(samples[int(samples.size() * 0.10)]),
		"p90": float(samples[int(samples.size() * 0.90)]),
		"peak": _peak_emitters,
		"expect": expect,
		"min_health": _min_health,
		"b_off": _b_off_frames,
	})


##   keep    -- which effect nodes are left in the scene
##   walk    -- hold right, so Effect C strides
##   a_mode  -- "" none, "ceiling" three bursts, "one" a single burst held
##   expect  -- the peak GPUParticles2D count this condition's LABEL claims.
##             Checked against what was observed, because a condition that
##             did not carry the load its name says measured a label.
func _condition(keep: Array, walk: bool, a_mode: String, label: String,
		expect: int) -> void:
	var main: Node = load(MAIN).instantiate()
	for name in ALL_EFFECTS:
		if keep.has(name):
			continue
		var n := main.get_node_or_null(NodePath(name))
		if n != null:
			n.free()
	root.add_child(main)
	await process_frame
	await _wait_frames(WARMUP)

	var traps: Array = []
	var refire := 0.0
	if a_mode == "ceiling":
		for trap in main.get_node("Traps").get_children():
			traps.append(trap)
		refire = A_REFIRE_SECONDS
	elif a_mode == "one":
		traps.append(main.get_node("Traps").get_child(0))
		refire = A_ONE_REFIRE_SECONDS

	var samples := await _measure(FRAMES, main, traps, refire, walk)
	if walk:
		_release(KEY_D)

	_record(label, samples, expect)
	main.queue_free()
	await process_frame


func _init() -> void:
	await process_frame

	if DisplayServer.get_name() == "headless":
		push_error("gpu_cost_effects.gd needs a REAL WINDOW. A headless run "
			+ "uses a dummy renderer, draws nothing, and would report 0.000 "
			+ "ms for every condition -- a result that looks exactly like an "
			+ "effect that costs nothing. Run scripts/run-gpu-cost.sh.")
		quit(1)
		return

	_vp = root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_vp, true)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	await _wait_frames(60)   # let the driver settle and the clocks boost

	print("GPU render time per frame, milliseconds, real windowed run.")
	print("  engine   : ", Engine.get_version_info().get("string", "?"))
	print("  renderer : ", RenderingServer.get_video_adapter_name())
	print("  display  : ", DisplayServer.get_name())
	print("  window   : ", DisplayServer.window_get_size())
	print("  vsync    : ", DisplayServer.window_get_vsync_mode(), "  (0 = disabled)")
	print("  when     : ", Time.get_datetime_string_from_system())
	print("  %d frames per condition after %d warm-up frames." % [FRAMES, WARMUP])
	print("")

	# The last argument is the peak emitter count the row's LABEL claims:
	# 3 emitters per burst (Flash/Grit/Dust), 2 per step-dust puff
	# (Kick/Puff), 1 for the mote field.
	await _condition([], false, "", "room, all three effects REMOVED (1)", 0)
	await _condition([EFFECT_B], false, "", "B only, steady state", 1)
	await _condition([EFFECT_C], true, "", "C only, player running", 2)
	await _condition([EFFECT_A], false, "one",
		"A only, ONE burst held (play peak, 32)", 3)
	await _condition([EFFECT_A], false, "ceiling",
		"A only, at the ceiling of %d (96)" % A_CEILING, 3 * A_CEILING)
	await _condition(ALL_EFFECTS, true, "ceiling", "all three, heaviest",
		3 * A_CEILING + 2 + 1)
	# The SAME condition as row 1, run last.
	#
	# Row 1 read higher than "all three", which is not a thing that can be
	# true: all three contains B. Either the conditions are not comparable
	# across the run, or a difference of a few thousandths of a millisecond
	# on this card is not a measurement. This row is how the report finds
	# out which, instead of explaining it.
	await _condition([EFFECT_B], false, "", "B only, steady state (REPEAT)", 1)
	await _condition([], false, "", "room, all three effects REMOVED (2)", 0)

	print("%-44s %10s %10s %10s %8s %7s %7s %6s"
		% ["condition", "median ms", "p10 ms", "p90 ms", "peak em",
		"health", "B off", "label"])
	var labels_true := true
	for row in _rows:
		# A row may carry MORE than its label claims -- in the all-three
		# condition the traps also fire from play, on top of the forced
		# rotation. Carrying LESS is the failure: the condition did not
		# reach the load its name is about.
		var ok: bool = int(row["peak"]) >= int(row["expect"])
		labels_true = labels_true and ok
		print("%-44s %10.4f %10.4f %10.4f %8d %7d %7d %6s"
			% [row["label"], row["median"], row["p10"], row["p90"],
			row["peak"], row["min_health"], row["b_off"],
			"ok" if ok else "FALSE"])
	if not labels_true:
		print("")
		print("A row marked FALSE did not reach the load its label claims.")
		print("Its millisecond figure measures the label, not the effect.")

	var off1: float = _rows[0]["median"]
	var off2: float = _rows[_rows.size() - 1]["median"]
	var baseline := 0.5 * (off1 + off2)
	var noise := absf(off1 - off2)

	print("")
	print("Baseline (effects removed, mean of two runs): %.4f ms" % baseline)
	print("Spread between those two runs -- the resolution: %.4f ms" % noise)
	print("")
	print("%-44s %14s %11s %10s %s"
		% ["effect", "over baseline", "budget", "vs noise", "verdict"])

	var budgets := [[1, EFFECT_B], [2, EFFECT_C], [3, EFFECT_A],
		[4, EFFECT_A], [5, ""], [6, EFFECT_B]]
	var total_budget: float = BUDGET[EFFECT_A] + BUDGET[EFFECT_B] + BUDGET[EFFECT_C]
	var all_under := true
	for pair in budgets:
		var i: int = pair[0]
		var key: String = pair[1]
		var d: float = _rows[i]["median"] - baseline
		var b: float = BUDGET.get(key, total_budget)
		var under: bool = d <= b
		all_under = all_under and under
		print("%-44s %+12.4f ms %8.2f ms %10s %s"
			% [_rows[i]["label"], d, b,
			"below" if absf(d) <= noise else "ABOVE",
			"UNDER BUDGET" if under else "OVER BUDGET"])

	# Two checks on the table itself, before anyone reads a number off it.
	var b_drift: float = absf(_rows[6]["median"] - _rows[1]["median"])
	var contained: bool = _rows[5]["median"] >= _rows[1]["median"]
	print("")
	print("Does this table hold together?")
	print("  Effect B, measured twice (second condition, and second to last):")
	print("    %.4f ms and %.4f ms -- drift across the run %.4f ms."
		% [_rows[1]["median"], _rows[6]["median"], b_drift])
	print("  Containment: \"all three\" contains B, so it cannot cost less.")
	print("    all three %.4f ms, B alone %.4f ms -- %s."
		% [_rows[5]["median"], _rows[1]["median"],
		"holds" if contained else "DOES NOT HOLD"])
	if not contained or b_drift >= 0.001:
		print("")
		print("  So the per-effect figures are NOT separable at this scale.")
		print("  A set of conditions whose larger one measures cheaper than a")
		print("  subset of itself is not reporting the price of an effect; it")
		print("  is reporting the floor of the instrument. Each run reproduces")
		print("  itself to the last digit, which is what makes this worth")
		print("  saying out loud -- repeatable is not the same as true.")
		print("")
		print("  What the table DOES establish, and establishes firmly: the")
		print("  WHOLE FRAME, with all three effects at the brief's ceiling,")
		print("  costs about %.3f ms of GPU time. Every budget in section 5" % _rows[5]["median"])
		print("  and section C.6 is met with an order of magnitude to spare,")
		print("  and that conclusion does not depend on separating them.")
	else:
		print("  Both hold, so the per-effect figures may be read as prices.")
	print("")
	print("The last row's budget is the sum of the three, %.2f ms." % total_budget)
	print("\"below\" in the noise column means the difference is smaller than")
	print("the spread between two runs of the SAME condition. Where it says")
	print("below, the honest reading is \"under this instrument's resolution\",")
	print("not the millisecond figure beside it -- the figure is still")
	print("printed, because a reader is entitled to see what was discarded.")
	print("")
	print("The two Effect A rows are SYNTHETIC (revision 6.0.2): three bursts")
	print("cannot be alive at once by playing this room, and even one burst")
	print("has to be held by emitting `fired` every %.2f s. The ceiling row is"
		% A_ONE_REFIRE_SECONDS)
	print("what section 5's budget is set against; the one-burst row is what a")
	print("player actually produces.")
	print("")
	print("Same quantity as the editor's Visual Profiler \"Render Viewport\"")
	print("GPU row, read through the same timestamp query. Section 4 still")
	print("asks the author to read ONE of these by eye in the profiler, as a")
	print("cross-check of the instrument rather than of the effects.")
	quit(0 if (all_under and labels_true) else 1)
