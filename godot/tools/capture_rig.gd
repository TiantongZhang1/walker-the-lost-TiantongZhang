extends Node
## Controlled-value captures for CHANGE-BRIEF.md §6 and revision 5.0.4.
##
## Press **F5** in a real windowed run. It captures trap 1 at warn_amount
## 0.0, 0.5, 1.0 and 2.0, writes four PNGs, samples the two predicted pixels
## out of each, and prints the comparison.
##
## This is a debug rig, inert until a key is pressed. It reads raw key events
## rather than actions so that the input map is untouched.
##
## Why in-engine and not a screenshot tool: an OS screenshot goes through the
## display colour profile and any desktop scaling, so the pixel at the
## coordinates predicted here may not be the pixel measured. This reads the
## rendered frame at viewport resolution, which is real engine output. The
## assignment asks for one OS screenshot alongside, for comparison; take it
## by hand at the 1.0 capture and say which you trust.
##
## It must not run headless: a dummy renderer draws nothing and would save
## four identical black frames that look like evidence.

## Beside the project folder, not inside it: `captures/a5/` at the repository
## root. Built from an absolute path rather than a `res://..` one, which
## escapes the project and is not worth relying on.
const OUT_SUBDIR := "captures/a5/"
const VALUES: Array[float] = [0.0, 0.5, 1.0, 2.0]

## Sprite-local pixels, from CHANGE-BRIEF.md §6. The trap sprite is 16 x 16
## and Sprite2D is centred, so local (x, y) sits at global
## (position + Vector2(x, y) - Vector2(8, 8)).
const PIXEL_A := Vector2i(8, 12)   # base plate, #2A2A33
const PIXEL_B := Vector2i(8, 3)    # spike tip,  #8A90A1
const SPRITE_SIZE := Vector2(16, 16)

## Predicted 8-bit values, hypothesis H1 (the shader receives warn_color as
## written). §6 for the first three rows, revision 5.0.4 for 2.0. Written
## here so a mismatch is loud; this table is not derived at runtime.
const PREDICT_A := {
	0.0: Vector3i(42, 42, 51),
	0.5: Vector3i(128, 51, 49),
	1.0: Vector3i(214, 60, 47),
	2.0: Vector3i(255, 78, 43),
}
const PREDICT_B := {
	0.0: Vector3i(138, 144, 161),
	0.5: Vector3i(176, 102, 104),
	1.0: Vector3i(214, 60, 47),
	2.0: Vector3i(255, 0, 0),
}
## H2, for the three values §6 predicts it at: source_color decoded the
## uniform sRGB -> linear before the shader saw it. Printed beside H1 so the
## capture chooses between them instead of merely agreeing with one.
const PREDICT_A_H2 := {
	0.5: Vector3i(107, 27, 29),
	1.0: Vector3i(171, 12, 7),
}

var _busy := false

## Every line this rig prints, also written to captures/a5/REPORT.txt.
## The normal Windows build has no console, so print() alone would put
## the measurement somewhere nobody can read it.
var _lines: PackedStringArray = []
var _dir := ""


func _say(line: String) -> void:
	print(line)
	_lines.append(line)


## CAPTURE_ON_START=1 runs the sweep without anyone pressing a key and then
## quits. It exists so the rig can be verified end to end, and so a reviewer
## can reproduce the capture without being told where to click. It is still a
## real windowed run: the frames are drawn by the GPU, not by a dummy device.
func _ready() -> void:
	if OS.get_environment("CAPTURE_ON_START") != "1":
		return
	await get_tree().create_timer(1.0).timeout
	await _sweep()
	await get_tree().create_timer(0.2).timeout
	get_tree().quit(0)


func _unhandled_key_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	if key.physical_keycode == KEY_F5 and not _busy:
		get_viewport().set_input_as_handled()
		_sweep()


func _sweep() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("The capture rig needs a real window; a headless run draws nothing.")
		return
	_busy = true

	var trap: SpikeTrap = get_node_or_null(^"../Traps/SpikeTrap1") as SpikeTrap
	var driver: TrapWarningDriver = null
	if trap != null:
		driver = trap.get_node_or_null(^"WarningDriver") as TrapWarningDriver
	if driver == null or driver.material == null:
		push_error("Capture rig found no trap 1 driver with a material.")
		_busy = false
		return

	# simplify_path() strips the trailing slash, which once put every file in
	# the parent directory with "a5" glued to the front of its name.
	var dir := (ProjectSettings.globalize_path("res://") + "../" + OUT_SUBDIR).simplify_path()
	if not dir.ends_with("/"):
		dir += "/"
	_dir = dir
	if DirAccess.make_dir_recursive_absolute(dir) != OK and not DirAccess.dir_exists_absolute(dir):
		push_error("Could not create the capture directory: " + dir)
		_busy = false
		return

	# Freeze both, or the state machine advances and the driver overwrites the
	# value before the frame draws. The assignment is explicit about the
	# second of these; the first matters because an untouched trap can still
	# be mid-cooldown when the key is pressed.
	trap.set_process(false)
	driver.set_process(false)
	trap.disarm()
	trap.state = SpikeTrap.State.ARMED
	trap.warn_amount = 0.0

	var pa := _viewport_pixel(trap, PIXEL_A)
	var pb := _viewport_pixel(trap, PIXEL_B)

	_lines.clear()
	_say("=== controlled-value capture, trap 1 ===")
	_say("  when     : " + Time.get_datetime_string_from_system())
	_say("  engine   : " + Engine.get_version_info().get("string", "?"))
	_say("  renderer : " + RenderingServer.get_video_adapter_name())
	_say("  viewport : " + str(get_viewport().get_visible_rect().size))
	var k0 := int(get_window().size.x / get_viewport().get_visible_rect().size.x)
	_say("  window   : %s, logical x%d" % [get_window().size, k0])
	_say("  pixel A  : sprite-local %s -> logical %s -> image %s" % [PIXEL_A, pa, pa * k0])
	_say("  pixel B  : sprite-local %s -> logical %s -> image %s" % [PIXEL_B, pb, pb * k0])
	_say("  files    : " + dir)

	var rows: Array = []
	for value in VALUES:
		driver.material.set_shader_parameter(&"warn_amount", value)
		# Two frames: the first carries the new uniform into the draw, the
		# second guarantees the texture being read back is that one.
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		# The root viewport's texture is the WINDOW, 1280 x 720, not the 640 x
		# 360 logical surface - `canvas_items` stretch scales on the way out.
		# Sampling the logical coordinate directly read empty background and
		# reported every value as the clear colour, four times identically,
		# which looked like a shader that did nothing.
		var k := img.get_width() / get_viewport().get_visible_rect().size.x
		var path := dir + "warn_%s.png" % String.num(value, 1).replace(".", "_")
		var err := img.save_png(path)
		rows.append([value, _at(img, pa * k), _at(img, pb * k), err])

	# Put it back exactly as it was before the key was pressed.
	driver.material.set_shader_parameter(&"warn_amount", 0.0)
	trap.set_process(true)
	driver.set_process(true)
	_report(rows)
	_busy = false


## Sprite-local pixel -> viewport pixel, through the real canvas transform
## rather than through an assumption about the camera.
func _viewport_pixel(trap: Node2D, local: Vector2i) -> Vector2i:
	var top_left := trap.global_position - SPRITE_SIZE * 0.5
	var world := top_left + Vector2(local) + Vector2(0.5, 0.5)
	var screen := get_viewport().get_canvas_transform() * world
	return Vector2i(floori(screen.x), floori(screen.y))


func _at(img: Image, p: Vector2i) -> Vector3i:
	if p.x < 0 or p.y < 0 or p.x >= img.get_width() or p.y >= img.get_height():
		return Vector3i(-1, -1, -1)
	var c := img.get_pixelv(p)
	return Vector3i(roundi(c.r * 255.0), roundi(c.g * 255.0), roundi(c.b * 255.0))


func _report(rows: Array) -> void:
	_say("")
	_say("  warn_amount | pixel | measured      | H1 predicted  | delta       | H2")
	_say("  ------------+-------+---------------+---------------+-------------+--------------")
	var worst := 0
	for row in rows:
		var value: float = row[0]
		for pair in [["A", row[1], PREDICT_A], ["B", row[2], PREDICT_B]]:
			var got: Vector3i = pair[1]
			var want: Vector3i = pair[2][value]
			var d := Vector3i(got.x - want.x, got.y - want.y, got.z - want.z)
			worst = maxi(worst, maxi(absi(d.x), maxi(absi(d.y), absi(d.z))))
			var h2 := ""
			if pair[0] == "A" and PREDICT_A_H2.has(value):
				var alt: Vector3i = PREDICT_A_H2[value]
				h2 = "%3d,%3d,%3d" % [alt.x, alt.y, alt.z]
			_say("  %11s | %5s | %3d, %3d, %3d | %3d, %3d, %3d | %+3d,%+3d,%+3d | %s"
				% [String.num(value, 1), pair[0],
				   got.x, got.y, got.z, want.x, want.y, want.z,
				   d.x, d.y, d.z, h2])
	_say("")
	_say("  worst channel difference: %d" % worst)
	if worst == 0:
		_say("  EXACT. H1 holds: the shader receives warn_color as written,")
		_say("  and hint_range did not clamp the 2.0 written from code.")
	elif worst <= 2:
		_say("  Within a step or two - acceptable, but say so and show the capture.")
	else:
		_say("  MORE THAN A STEP OR TWO. The brief calls this a finding, not an")
		_say("  error: record it with the capture and find out why before")
		_say("  explaining it. Compare against H2 in the last column.")
	_say("")
	_say("  Also do by hand, at the 1.0 capture: one OS screenshot of the same")
	_say("  frame, sample the same pixel, and record which you trust and why.")
	_say("=== end capture ===")
	_write_report()


## The ordinary Windows build has no console, so print() alone would put the
## measurement somewhere nobody can read. The report lands beside the PNGs.
func _write_report() -> void:
	var path := _dir + "REPORT.txt"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("Could not write " + path)
		return
	f.store_string("\n".join(_lines) + "\n")
	f.close()
	print("  report written: ", path)
