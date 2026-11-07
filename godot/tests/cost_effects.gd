extends SceneTree
## What the three effects cost, measured headless. Assignment 6, Step 7.
##
##   ./scripts/run-test.sh cost_effects.gd 60 300
##
## **This script exists to test a prediction, not to produce a budget.**
## `CHANGE-BRIEF.md` §5 and revision 6.0.4 §C.6 predict that every one of
## these effects reads **≈ 0 ms over the control** here, and they predict it
## *by construction*: a `GPUParticles2D`'s process step is a shader on the
## graphics card, a headless run uses a dummy renderer, and a measurement
## that never reaches the card has nothing of the card to measure. What is
## left is the node's own bookkeeping.
##
## So a difference near zero is the prediction holding. **A difference that
## is clearly not zero means the script is wrong or the prediction is**, and
## §5 says so in those words — it would rather be caught than vague.
##
## **The number that decides whether the budget is met is not in this file.**
## That is GPU time from the Visual Profiler, read by the author on hardware,
## at the heaviest state the game reaches. §4's evidence split puts that row
## under HUMAN, and nothing headless can move it.
##
## **Why FPS is not used as the instrument either.** §7: with vsync on, the
## frame rate reads the display's refresh rate with the effects off and the
## same with them on, because vsync holds it there until a frame actually
## misses. 96 particles will not make a 5080 miss. FPS is the wrong
## instrument twice over.

const MAIN := "res://game/main.tscn"

## The presentation nodes, by name in `main.tscn`. Removing all of them is
## the "effects off" condition.
const EFFECT_NODES := ["HitBurstSpawner", "DungeonMotes", "StepDustDriver"]

## Frames per condition, after the warm-up. At 60 fps this is ten seconds of
## game time per condition, which is long enough for the player to walk into
## all three traps and for the mote field to turn over several times.
const FRAMES := 600
const WARMUP := 120

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
## labelled "all three effects live" that never reached more than one
## emitter measured a label, not a load.
func _measure(n: int, watch: Node) -> Array:
	var samples: Array = []
	_peak_emitters = 0
	_instances_seen = {}
	for i in range(n):
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


## The empty-scene control. §5 asks for one, because "near zero" is only
## meaningful against something.
func _condition_empty() -> void:
	var holder := Node2D.new()
	root.add_child(holder)
	await _wait_frames(WARMUP)
	var samples := await _measure(FRAMES, null)
	_record("empty scene (control)", samples)
	holder.queue_free()
	await process_frame


## The room, with or without its presentation nodes, with the player walking
## into all three traps so every effect that can fire does.
func _condition_room(with_effects: bool, label: String) -> void:
	var main: Node = load(MAIN).instantiate()
	if not with_effects:
		for name in EFFECT_NODES:
			var n := main.get_node_or_null(NodePath(name))
			if n != null:
				n.free()
	root.add_child(main)
	await process_frame
	await _wait_frames(WARMUP)   # fall to the floor, settle, fill the field

	# Walk right for the whole measurement. The player crosses all three
	# detection zones, so Effect A fires three times; Effect C fires every
	# 24 px throughout; Effect B is running from frame one either way.
	_key(KEY_D, true)
	var samples := await _measure(FRAMES, main)
	_key(KEY_D, false)

	_record(label, samples)
	main.queue_free()
	await process_frame


## Live `GPUParticles2D` nodes in the tree, as a sanity figure beside the
## timing: a condition that reports "effects on" and counts one emitter is
## not measuring what its label says.
func _count_particles(node: Node, found: int) -> int:
	for child in node.get_children():
		if child is GPUParticles2D:
			found += 1
		found = _count_particles(child, found)
	return found


func _record(label: String, samples: Array) -> void:
	_rows.append({
		"label": label,
		"median": _median(samples),
		"mean": _mean(samples),
		"p90": float(samples[int(samples.size() * 0.9)]),
		"peak": _peak_emitters,
		"instances": _instances_seen.size(),
	})


func _init() -> void:
	print("Headless CPU cost, %d frames per condition after %d warm-up frames."
		% [FRAMES, WARMUP])
	print("Wall clock per frame, microseconds. A headless run draws nothing.")
	print("Each room condition is run TWICE, interleaved, so the script can")
	print("measure its own noise before it reports a difference.")
	print("")

	await _condition_empty()
	await _condition_room(false, "room, effects REMOVED (run 1)")
	await _condition_room(true,  "room, all three effects live (run 1)")
	await _condition_room(false, "room, effects REMOVED (run 2)")
	await _condition_room(true,  "room, all three effects live (run 2)")

	print("%-38s %10s %10s %10s %8s %10s"
		% ["condition", "median us", "mean us", "p90 us", "peak em", "instances"])
	for row in _rows:
		print("%-38s %10.1f %10.1f %10.1f %8d %10d"
			% [row["label"], row["median"], row["mean"], row["p90"],
			row["peak"], row["instances"]])

	var off1: float = _rows[1]["median"]
	var on1: float = _rows[2]["median"]
	var off2: float = _rows[3]["median"]
	var on2: float = _rows[4]["median"]
	var delta := 0.5 * (on1 + on2) - 0.5 * (off1 + off2)
	# The spread between two runs of a condition that did not change is this
	# instrument's resolution. Reporting a difference smaller than it as if
	# it were a measurement is the thing this whole report keeps warning
	# about, in a new costume.
	var noise := maxf(absf(off1 - off2), absf(on1 - on2))

	print("")
	print("Effects on minus effects off: %+.1f us per frame (%+.4f ms)."
		% [delta, delta / 1000.0])
	print("Spread between two runs of an UNCHANGED condition: %.1f us."
		% noise)

	var below_noise: bool = absf(delta) <= noise
	var small: bool = absf(delta) < 100.0
	if below_noise:
		print("The difference is SMALLER THAN THE NOISE. The honest reading is")
		print("not \"%+.4f ms\" but \"below this instrument's resolution\"."
			% (delta / 1000.0))
	else:
		print("The difference is larger than the noise. It is node bookkeeping")
		print("-- %d effect instances were created and freed during the run --"
			% int(_rows[2]["instances"]))
		print("and NOT the particle process, which never runs headless.")

	print("Prediction (CHANGE-BRIEF.md 5, C.6): approximately 0 ms over the")
	print("control. %s"
		% ("HOLDS." if small else "DOES NOT HOLD - see section 5."))
	if not small:
		print("  Section 5: a difference here means the script is wrong or the")
		print("  prediction is. Do not report it as a GPU cost.")

	print("")
	print("What this does NOT measure: GPU time, which is the price every")
	print("budget in section 5 and C.6 is actually set against. That is the")
	print("Visual Profiler, read on hardware by the author, and section 4")
	print("puts it under HUMAN for exactly this reason.")
	quit(0 if small else 1)