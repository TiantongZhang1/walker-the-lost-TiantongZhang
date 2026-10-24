extends SceneTree
## The driver, and the hand-written shader's declared interface.
##
## test_trap_warning.gd checks the game state. This checks the step after it:
## that the number SpikeTrap computed actually arrives in the shader, in the
## same frame, on this trap's own material and no other.
##
##   ./scripts/run-test.sh test_trap_shader_driver.gd 30
##   ./scripts/run-test.sh test_trap_shader_driver.gd 60
##   ./scripts/run-test.sh test_trap_shader_driver.gd 144
##
## What it cannot show: colour. A headless run uses a dummy renderer and draws
## nothing, so every claim here is about a declared interface and about
## floats. The predicted pixels in CHANGE-BRIEF.md section 6 are a human check
## against a real capture, and TEST-REPORT.md keeps them outstanding until
## someone has taken one.

const MAIN := "res://game/main.tscn"
const SHADER_PATH := "res://shaders/trap_warning.gdshader"
const WARN := 0.40  # SpikeTrap.WARN_SECONDS, revision 5.0.3
const UNIFORM := &"warn_amount"

## CHANGE-BRIEF.md section 2. The six decimals matter: section 6 computes
## 214, 60, 47 from them, and 0.84 would not land there.
const WARN_COLOR_SOURCE := "vec3(0.839216, 0.235294, 0.184314)"

var _checks := 0
var _failures := 0
var _fps := 60.0


## Records state and uniform side by side, once per frame, after every other
## _process in that frame: SpikeTrap is priority 0, TrapWarningDriver 100,
## this 1000. A row where the two differ is a frame in which the screen showed
## something the game had already moved on from.
class Sampler:
	extends Node
	var traps: Array = []
	var rows: Array = []

	func _ready() -> void:
		process_priority = 1000

	func _process(_delta: float) -> void:
		var row: Array = []
		for trap in traps:
			var driver: TrapWarningDriver = trap.get_node("WarningDriver")
			var got: Variant = null
			if driver.material != null:
				got = driver.material.get_shader_parameter(UNIFORM)
			row.append([trap.warn_amount, got])
		rows.append(row)


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


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


func _until(cond: Callable, limit := 6.0) -> float:
	var t := 0.0
	while t < limit:
		if cond.call():
			return t
		await process_frame
		t += root.get_process_delta_time()
	return -1.0


# -------------------------------------------------------- the frame rate

## --fixed-fps is consumed by the engine and never reaches the script, so
## run-test.sh exports the declared rate and the engine's own modal delta is
## the cross-check. CHANGE-BRIEF.md revision 5.0.3 says why a two-frame sample
## is not enough at 144.
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
	for key in counts:
		if counts[key] > best_n:
			best = key
			best_n = counts[key]
	var modal := 1.0 / float(best)
	if declared > 0.0 and absf(modal - declared) / declared > 0.01:
		_check("    declared fps agrees with the engine modal delta", false,
			"TEST_FPS=%.0f, measured %.1f" % [declared, modal])
	_fps = declared if declared > 0.0 else modal
	print("  frame rate: %.0f fps declared, modal delta %s s (%d/40 frames)"
		% [_fps, best, best_n])


# --------------------------------------------------------------- the room

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


# ------------------------------------------------------------- the shader

## Everything the engine will tell a headless run about the hand-written
## shader. Defaults are not among those things, so they are read from the
## source text instead, and said to be read from it.
func _scenario_interface() -> void:
	print("\n-- the shader's declared interface --")
	var shader: Shader = load(SHADER_PATH)
	_check("    the shader loads", shader != null)
	if shader == null:
		return

	_check("    shader_type is canvas_item",
		shader.get_mode() == Shader.MODE_CANVAS_ITEM,
		"mode=%d" % shader.get_mode())

	var by_name := {}
	for entry in shader.get_shader_uniform_list():
		by_name[String(entry["name"])] = entry

	_check("    declares warn_amount", by_name.has("warn_amount"))
	_check("    declares warn_color", by_name.has("warn_color"))
	if not (by_name.has("warn_amount") and by_name.has("warn_color")):
		return

	var amt: Dictionary = by_name["warn_amount"]
	var col: Dictionary = by_name["warn_color"]

	_check("    warn_amount is a float", int(amt["type"]) == TYPE_FLOAT,
		"type=%d" % int(amt["type"]))
	# hint_range survives into the engine's own description of the uniform,
	# so the Inspector slider is not the only evidence that it is there.
	_check("    warn_amount carries hint_range(0.0, 1.0)",
		int(amt["hint"]) == PROPERTY_HINT_RANGE
			and String(amt["hint_string"]).begins_with("0.0,1.0"),
		"hint=%d %s" % [int(amt["hint"]), amt["hint_string"]])

	# source_color on a vec3 is reported as TYPE_COLOR with COLOR_NO_ALPHA.
	# A plain vec3 comes back as TYPE_VECTOR3, so this one entry is the
	# engine-side fingerprint of the hint.
	_check("    warn_color is a source_color vec3",
		int(col["type"]) == TYPE_COLOR
			and int(col["hint"]) == PROPERTY_HINT_COLOR_NO_ALPHA,
		"type=%d hint=%d" % [int(col["type"]), int(col["hint"])])

	var samplers := 0
	for key in by_name:
		if int(by_name[key]["type"]) == TYPE_OBJECT:
			samplers += 1
	_check("    no sampler uniforms, as the brief specifies", samplers == 0,
		"%d sampler(s)" % samplers)

	# Defaults. The engine does not report them, so this reads the file.
	var src := FileAccess.get_file_as_string(SHADER_PATH)
	_check("    source: warn_amount defaults to 0.0", src.contains("= 0.0;"))
	_check("    source: warn_color default is the specified six decimals",
		src.contains(WARN_COLOR_SOURCE), WARN_COLOR_SOURCE)
	_check("    source: the colour line is the one the brief specifies",
		src.contains("mix(COLOR.rgb, warn_color, warn_amount)"))


# ------------------------------------------------------------- the driver

## F1/R6. A sub-resource inside a PackedScene is shared by every instance of
## that scene, so without the duplicate() in _ready() the three traps would
## hold one material and warn together. This asserts the three are distinct
## objects before anything has had a chance to warn.
func _scenario_per_instance() -> void:
	print("\n-- F1/R6: one material per trap --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]

	var ids := []
	var all_declared := true
	for trap in traps:
		var driver: TrapWarningDriver = trap.get_node("WarningDriver")
		_check("    trap has a driver holding a material", driver.material != null)
		if driver.material != null:
			ids.append(driver.material.get_instance_id())
		all_declared = all_declared and driver.uniform_declared

	# F5: set_shader_parameter on a name the shader does not declare writes
	# nowhere and reports nothing, so the driver asks the shader at startup.
	_check("F5  every driver found its uniform declared", all_declared)

	var distinct := {}
	for id in ids:
		distinct[id] = true
	_check("F1  the three materials are three different objects",
		distinct.size() == 3, "%d distinct of %d" % [distinct.size(), ids.size()])

	var shown: ShaderMaterial = traps[0].get_node("Sprite2D").material
	_check("    the sprite shows the per-instance copy, not the scene's",
		shown != null and ids.size() > 0 and shown.get_instance_id() == ids[0])
	await _teardown(main, sampler)


## The uniform tracks the state, in the same frame, across a whole real
## trigger driven by synthesized input.
func _scenario_tracks_state() -> void:
	print("\n-- the uniform follows the state, frame by frame --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var traps: Array = bits[1]
	var sampler: Sampler = bits[2]
	var t1: SpikeTrap = traps[0]

	var first_row := sampler.rows.size()
	_key(KEY_D, true)
	var walked := await _until(_is_warning.bind(t1))
	_check("    the player reached trap 1 by walking", walked >= 0.0,
		"%.2f s of travel" % walked)

	var dur := await _until(_uniform_full.bind(t1), 6.0)
	_key(KEY_D, false)
	var frame := 1.0 / _fps
	# Measured through the UNIFORM rather than through the state: this is the
	# number the screen would have been showing.
	_check("R2  the uniform took %.3f s to reach 1.0 (want %.3f +- %.4f)"
			% [dur, WARN, frame],
		_near(dur, WARN, frame + 0.001), "one frame = %.4f s" % frame)

	# Let the strike finish and the trap re-arm.
	await _until(_is_armed.bind(t1), 6.0)
	await process_frame

	var worst := 0.0
	var worst_row := -1
	var compared := 0
	var peak_other := 0.0
	for i in range(first_row, sampler.rows.size()):
		var row: Array = sampler.rows[i]
		for column in 3:
			var pair: Array = row[column]
			if pair[1] == null:
				continue
			compared += 1
			var gap: float = absf(float(pair[0]) - float(pair[1]))
			if gap > worst:
				worst = gap
				worst_row = i
			if column > 0:
				peak_other = maxf(peak_other, float(pair[1]))

	_check("    enough frames were compared to mean something", compared > 60,
		"%d state/uniform pairs over %d frames"
			% [compared, sampler.rows.size() - first_row])
	_check("    the uniform never differed from the state in any frame",
		worst == 0.0, "worst gap %.9f at row %d" % [worst, worst_row])
	_check("R6  traps 2 and 3 never lit while trap 1 warned",
		peak_other == 0.0, "their peak uniform was %.6f" % peak_other)
	_check("    the uniform is back at 0.0 once the trap re-arms",
		is_zero_approx(_uniform_of(t1)), "%.6f" % _uniform_of(t1))

	# Boundaries: the driver animates warn_amount and nothing else.
	var col: Variant = _driver_of(t1).material.get_shader_parameter(&"warn_color")
	var want := Color(0.839216, 0.235294, 0.184314, 1.0)
	_check("    the driver left warn_color alone through the whole cycle",
		col != null and (col as Color).is_equal_approx(want), str(col))
	await _teardown(main, sampler)


func _driver_of(trap: Node) -> TrapWarningDriver:
	return trap.get_node("WarningDriver")


func _uniform_of(trap: Node) -> float:
	var m: ShaderMaterial = _driver_of(trap).material
	if m == null:
		return -1.0
	var v: Variant = m.get_shader_parameter(UNIFORM)
	return -1.0 if v == null else float(v)


func _uniform_full(trap: Node) -> bool:
	return _uniform_of(trap) >= 1.0


func _is_warning(trap: Node) -> bool:
	return trap.state == SpikeTrap.State.WARNING


func _is_armed(trap: Node) -> bool:
	return trap.state == SpikeTrap.State.ARMED


# ------------------------------------------------------------------ main

func _init() -> void:
	await _resolve_fps()
	await _scenario_interface()
	await _scenario_per_instance()
	await _scenario_tracks_state()
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: the declared interface, and that the state reaches the")
	print("uniform unchanged, on this trap's own material. Proves nothing")
	print("about colour - a headless run draws nothing.")
	quit(1 if _failures > 0 else 0)
