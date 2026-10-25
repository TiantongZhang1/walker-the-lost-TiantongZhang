extends SceneTree
## The hint experiment's capture, for CHANGE-BRIEF.md section 7.
##
##   Godot_v4.7.2-stable_win64_console.exe --path godot \
##       --script res://tools/capture_hint.gd
##
## Needs a real window. A headless run uses a dummy renderer and would save a
## black frame that looks like a measurement.
##
## It loads scenes/hint_experiment.tscn, renders it, samples the middle of
## each band on each quad, and prints the six values beside what section 7
## predicted. It also asserts the rendering conditions the prediction depends
## on - Linear tonemap at exposure 1.0, no glow, fog or adjustments - because
## any of those silently rewrites the numbers, and a default-valued property
## is not written to the .tscn and so cannot be confirmed by reading it.

const SCENE := "res://scenes/hint_experiment.tscn"
const OUT_SUBDIR := "captures/a5/"

## Section 7's table. Left column is what the file stores.
const STORED := [64, 128, 192]
const PREDICT_WITH := [64, 128, 192]        # the sampler that decodes
const PREDICT_WITHOUT := [137, 188, 225]    # the one that does not

## Quad centres in world space, and the quad's width, from the scene.
const QUAD_WIDTH := 1.2
const QUAD_X := {"with": -0.7, "without": 0.7}

var _lines: PackedStringArray = []
var _bad := 0


func _say(line: String) -> void:
	print(line)
	_lines.append(line)


func _init() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("The hint capture needs a real window; headless draws nothing.")
		quit(1)
		return

	var scene := (load(SCENE) as PackedScene).instantiate()
	root.add_child(scene)
	var cam: Camera3D = scene.get_node("Camera3D")
	var env: Environment = (scene.get_node("WorldEnvironment") as WorldEnvironment).environment

	for i in 30:
		await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw

	var img := root.get_texture().get_image()
	var k := img.get_width() / root.get_visible_rect().size.x

	var dir := (ProjectSettings.globalize_path("res://") + "../" + OUT_SUBDIR).simplify_path()
	if not dir.ends_with("/"):
		dir += "/"
	DirAccess.make_dir_recursive_absolute(dir)
	img.save_png(dir + "hint_experiment.png")

	_say("=== hint experiment, CHANGE-BRIEF.md section 7 ===")
	_say("  when     : " + Time.get_datetime_string_from_system())
	_say("  renderer : " + RenderingServer.get_video_adapter_name())
	_say("  image    : %s, logical %s, x%d"
		% [img.get_size(), root.get_visible_rect().size, int(k)])
	_say("  file     : " + dir + "hint_experiment.png")

	_check_conditions(env)

	_say("")
	_say("  stored | with source_color      | without source_color")
	_say("         | measured  predicted    | measured  predicted")
	_say("  -------+------------------------+----------------------")
	for band in 3:
		var a := _sample(img, cam, k, QUAD_X["with"], band)
		var b := _sample(img, cam, k, QUAD_X["without"], band)
		_flag(a, PREDICT_WITH[band])
		_flag(b, PREDICT_WITHOUT[band])
		_say("  %6d |   %3d       %3d        |   %3d       %3d"
			% [STORED[band], a, PREDICT_WITH[band], b, PREDICT_WITHOUT[band]])

	_say("")
	if _bad == 0:
		_say("  All six exact. The source_color sampler returns the file's own")
		_say("  values; the other is brighter by one sRGB encode. 64 -> 137 is")
		_say("  the largest error, as section 7 said it would be.")
	else:
		_say("  %d of 6 off. Record the capture and find out why before" % _bad)
		_say("  explaining it - section 7 calls a mismatch a finding, not a bug.")
	_say("=== end ===")

	var f := FileAccess.open(dir + "HINT-REPORT.txt", FileAccess.WRITE)
	if f != null:
		f.store_string("\n".join(_lines) + "\n")
		f.close()
		print("  report written: ", dir + "HINT-REPORT.txt")
	quit(1 if _bad > 0 else 0)


## The prediction assumes a particular pipeline. Assert it rather than assume
## it: every one of these is a default value, so the .tscn does not record it
## and reading the file would prove nothing.
func _check_conditions(env: Environment) -> void:
	var want := {
		"tonemap_mode": [env.tonemap_mode, Environment.TONE_MAPPER_LINEAR],
		"tonemap_exposure": [env.tonemap_exposure, 1.0],
		"glow_enabled": [env.glow_enabled, false],
		"fog_enabled": [env.fog_enabled, false],
		"volumetric_fog_enabled": [env.volumetric_fog_enabled, false],
		"adjustment_enabled": [env.adjustment_enabled, false],
		"ssao_enabled": [env.ssao_enabled, false],
		"ambient_light_source": [env.ambient_light_source, Environment.AMBIENT_SOURCE_BG],
	}
	_say("")
	_say("  rendering conditions the prediction needs:")
	for key in want:
		var got: Variant = want[key][0]
		var need: Variant = want[key][1]
		var ok: bool = got == need
		if not ok:
			_bad += 1
		_say("    %-22s %-8s %s" % [key, str(got), "ok" if ok else "WANTED " + str(need)])


## World point at the middle of band `band` on the quad centred at `x`, turned
## into an image pixel through the camera rather than through an assumption
## about where things land on screen.
func _sample(img: Image, cam: Camera3D, k: float, x: float, band: int) -> int:
	var left := x - QUAD_WIDTH * 0.5
	var cx := left + QUAD_WIDTH * (float(band) + 0.5) / 3.0
	var p := cam.unproject_position(Vector3(cx, 0.0, 0.0)) * k
	var px := Vector2i(int(p.x), int(p.y))
	if px.x < 0 or px.y < 0 or px.x >= img.get_width() or px.y >= img.get_height():
		_bad += 1
		return -1
	return roundi(img.get_pixelv(px).r * 255.0)


func _flag(got: int, want: int) -> void:
	if got != want:
		_bad += 1
