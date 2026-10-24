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

	var dir := (ProjectSettings.globalize_path("res://") + "../" + OUT_SUBDIR).simplify_path()
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

	print("\n=== controlled-value capture, trap 1 ===")
	print("  renderer : ", RenderingServer.get_video_adapter_name())
	print("  viewport : ", get_viewport().get_visible_rect().size)
	print("  pixel A  : sprite-local %s -> viewport %s" % [PIXEL_A, pa])
	print("  pixel B  : sprite-local %s -> viewport %s" % [PIXEL_B, pb])
	print("  files    : ", dir)

	var rows: Array = []
	for value in VALUES:
		driver.material.set_shader_parameter(&"warn_amount", value)
		# Two frames: the first carries the new uniform into the draw, the
		# second guarantees the texture being read back is that one.
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := dir + "warn_%s.png" % String.num(value, 1).replace(".", "_")
		var err := img.save_png(path)
		rows.append([value, _at(img, pa), _at(img, pb), err])

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
	print("\n  warn_amount | pixel | measured      | H1 predicted  | delta       | H2")
	print("  ------------+-------+---------------+---------------+-------------+--------------")
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
			print("  %11s | %5s | %3d, %3d, %3d | %3d, %3d, %3d | %+3d,%+3d,%+3d | %s"
				% [String.num(value, 1), pair[0],
				   got.x, got.y, got.z, want.x, want.y, want.z,
				   d.x, d.y, d.z, h2])
	print("\n  worst channel difference: %d" % worst)
	if worst == 0:
		print("  EXACT. H1 holds: the shader receives warn_color as written,")
		print("  and hint_range did not clamp the 2.0 written from code.")
	elif worst <= 2:
		print("  Within a step or two - acceptable, but say so and show the capture.")
	else:
		print("  MORE THAN A STEP OR TWO. The brief calls this a finding, not an")
		print("  error: record it with the capture and find out why before")
		print("  explaining it. Compare against H2 in the last column.")
	print("\n  Also do by hand, at the 1.0 capture: one OS screenshot of the same")
	print("  frame, sample the same pixel, and record which you trust and why.")
	print("=== end capture ===\n")
