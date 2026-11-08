extends SceneTree
## What the three effects cost, measured headless. Assignment 6, Step 7.
##
##   ./scripts/run-test.sh cost_effects.gd 60 300
##
## **This script exists to test a prediction, not to produce a budget.**
## `CHANGE-BRIEF.md` §5 and revision 6.0.4 §C.6 predict that every one of
## these effects reads **≈ 0 ms over the control**, and predict it *by
## construction*: a `GPUParticles2D`'s process step is a shader on the
## graphics card, a headless run uses a dummy renderer, and a measurement
## that never reaches the card has nothing of the card to measure. What is
## left is the node's own bookkeeping.
##
## A difference near zero is the prediction holding. **A difference that is
## clearly not zero means the script is wrong or the prediction is**, and §5
## says so in those words.
##
## **The cases are the ones the assignment names**: an empty scene; the game
## scene with the effects off; **Effect A at the most bursts the brief says
## can be alive at once**; **Effect B in its heaviest state**; Effect C the
## same; and all three together.
##
## **Effect A's case is synthetic and is labelled.** Revision 6.0.2 measured
## that three bursts cannot be alive at once by playing this room — the traps
## are 1.17 s apart at walking speed and a burst lives 0.60 s, so play reaches
## one. Holding three alive means emitting `fired` directly, on a 0.20 s
## rotation. That is the brief's ceiling, which is what §5's budget is set
## against, and it is not a thing a player produces.
##
## **The number that decides whether a budget is met is not in this file.**
## That is GPU time from the Visual Profiler, read by the author on hardware.
## §4's evidence split puts that row under HUMAN.

const MAIN := "res://game/main.tscn"

## The presentation nodes in `main.tscn`, by name.
const EFFECT_A := "HitBurstSpawner"
const EFFECT_B := "DungeonMotes"
const EFFECT_C := "StepDustDriver"
const ALL_EFFECTS := [EFFECT_A, EFFECT_B, EFFECT_C]

## Frames per condition after the warm-up, and the warm-up itself. The warm-up
## lets the player fall to the floor and Effect B's field turn over.
const FRAMES := 400
const WARMUP := 120

## Revision 6.0.2's ceiling, and the rotation that holds it.
const A_CEILING := 3
const A_REFIRE_SECONDS := 0.20

var _rows: Array = []
var _peak_emitters := 0
var _instances_seen := {}


func _wait_frames(n: int) -> void:
	for i in range(n):
		await process_frame


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()


## Microseconds of wall clock per frame, plus what was in the tree while it
## was measured. A timing row without that is unreadable: a condition
## labelled "Effect A at its ceiling" that never reached three bursts
## measured a label, not a load.
func _measure(n: int, watch: Node, traps: Array) -> Array:
	var samples: Array = []
	_peak_emitters = 0
	_instances_seen = {}
	var since_refire := 0.0
	var next_trap := 0
	for i in range(n):
		# Hold Effect A at its ceiling by rotating the three traps.
		if not traps.is_empty():
			since_refire += root.get_process_delta_time()
			if since_refire >= A_REFIRE_SECONDS:
				since_refire = 0.0
				traps[next_trap].fired.emit()
				next_trap = (next_trap + 1) % traps.size()
		var t0 := Time.get_ticks_usec()
		await process_frame
		samples.append(Time.get_ticks_usec() - t0)
		if watch != null:
			_peak_emitters = maxi(_peak_emitters, _count_particles(watch, 0))
			_count_instances(watch)
	samples.sort()
	return samples


## Distinct effect instances that have existed during this condition. The
## drivers spawn and free a scene per event, and THAT -- not the particle
## process, which never runs headless -- is what a non-zero difference here
## would be made of.
func _count_instances(node: Node) -> void:
	for child in node.get_children():
		if child.has_method("fire") and child.has_method("lifetime"):
			_instances_seen[child.get_instance_id()] = true


func _count_particles(node: Node, found: int) -> int:
	for child in node.get_children():
		if child is GPUParticles2D:
			found += 1
		found = _count_particles(child, found)
	return found


func _median(sorted_samples: Array) -> float:
	var n: int = sorted_samples.size()
	if n == 0:
		return 0.0
	if n % 2 == 1:
		return float(sorted_samples[n / 2])
	return 0.5 * (float(sorted_samples[n / 2 - 1]) + float(sorted_samples[n / 2]))


func _mean(samples: Array) -> float:
	if samples.is_empty():
		return 0.0
	var total := 0.0
	for s in samples:
		total += float(s)
	return total / float(samples.size())


func _record(label: String, samples: Array) -> void:
	_rows.append({
		"label": label,
		"median": _median(samples),
		"mean": _mean(samples),
		"p90": float(samples[int(samples.size() * 0.9)]),
		"peak": _peak_emitters,
		"instances": _instances_seen.size(),
	})


## §5 asks for an empty-scene control, because "near zero" is only meaningful
## against something.
func _condition_empty() -> void:
	var holder := Node2D.new()
	root.add_child(holder)
	await _wait_frames(WARMUP)
	var samples := await _measure(FRAMES, null, [])
	_record("empty scene (control)", samples)
	holder.queue_free()
	await process_frame


## The room with a chosen subset of the effects present.
##   keep       -- the effect nodes left in the scene
##   walk       -- hold right, so Effect C strides and the traps fire in play
##   hold_a_max -- emit `fired` on a rotation, holding Effect A at its ceiling
func _condition_room(keep: Array, walk: bool, hold_a_max: bool,
		label: String) -> void:
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
	if hold_a_max:
		for trap in main.get_node("Traps").get_children():
			traps.append(trap)
	if walk:
		_key(KEY_D, true)
	var samples := await _measure(FRAMES, main, traps)
	if walk:
		_key(KEY_D, false)

	_record(label, samples)
	main.queue_free()
	await process_frame


func _init() -> void:
	print("Headless CPU cost. %d frames per condition after %d warm-up frames."
		% [FRAMES, WARMUP])
	print("Wall clock per frame, microseconds. A headless run draws nothing.")
	print("The baseline is run TWICE so the script can state its own noise")
	print("floor before it reports any difference.\n")

	await _condition_empty()
	await _condition_room([], false, false, "room, all effects REMOVED (1)")
	await _condition_room([EFFECT_A], false, true,
		"A only, held at its ceiling of %d" % A_CEILING)
	await _condition_room([EFFECT_B], false, false, "B only, steady state")
	await _condition_room([EFFECT_C], true, false, "C only, player running")
	await _condition_room(ALL_EFFECTS, true, true, "all three, heaviest")
	await _condition_room([], false, false, "room, all effects REMOVED (2)")

	print("%-40s %10s %10s %10s %8s %10s"
		% ["condition", "median us", "mean us", "p90 us", "peak em", "instances"])
	for row in _rows:
		print("%-40s %10.1f %10.1f %10.1f %8d %10d"
			% [row["label"], row["median"], row["mean"], row["p90"],
			row["peak"], row["instances"]])

	var off1: float = _rows[1]["median"]
	var off2: float = _rows[6]["median"]
	var baseline := 0.5 * (off1 + off2)
	# Two runs of a condition that did not change is this instrument's
	# resolution. Reporting a difference smaller than it as if it were a
	# measurement is the failure this whole report keeps recording.
	var noise := absf(off1 - off2)

	print("\nBaseline (effects removed, mean of two runs): %.1f us" % baseline)
	print("Spread between those two runs -- the resolution: %.1f us" % noise)
	print("\n%-40s %12s %12s" % ["effect", "over baseline", "vs noise"])
	var worst := 0.0
	for i in [2, 3, 4, 5]:
		var d: float = _rows[i]["median"] - baseline
		worst = maxf(worst, absf(d))
		print("%-40s %+10.1f us %12s"
			% [_rows[i]["label"], d,
			"below" if absf(d) <= noise else "ABOVE"])

	var small: bool = worst < 100.0
	print("\nPrediction (CHANGE-BRIEF.md 5, C.6): approximately 0 ms over the")
	print("control for every effect. %s"
		% ("HOLDS." if small else "DOES NOT HOLD - see section 5."))
	if worst <= noise:
		print("Every difference is smaller than the instrument's own spread.")
		print("The honest reading is \"below this instrument's resolution\",")
		print("not any of the microsecond figures above.")
	if not small:
		print("  Section 5: a difference here means the script is wrong or")
		print("  the prediction is. Do not report it as a GPU cost.")

	print("\nWhat this does NOT measure: GPU time, which is the price every")
	print("budget in section 5 and C.6 is set against -- 0.30 / 0.20 / 0.10 ms.")
	print("That is the Visual Profiler, read on hardware by the author, and")
	print("section 4 puts it under HUMAN for exactly this reason.")
	print("\nEffect A's row is SYNTHETIC: revision 6.0.2 measured that three")
	print("bursts cannot be alive at once by playing this room. Holding the")
	print("ceiling means emitting `fired` directly, every %.2f s." % A_REFIRE_SECONDS)
	quit(0 if small else 1)
