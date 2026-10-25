extends SceneTree
## The two human checks part 3 still owes: the interface sweep, and one
## shader with two materials.
##
##   Godot_v4.7.2-stable_win64_console.exe --path godot \
##       --script res://tools/capture_materials.gd
##
## Needs a real window. It drives the two slimes in asset_showcase.tscn under
## the lighting CHANGE-BRIEF.md section 8 names, writes a PNG per step, and
## measures the mean colour of each slime out of the frame so "what changed"
## is a number and not an impression. Judging whether the result LOOKS right
## is still the author's; this only makes that judgement cheap to make.
##
## What it does, in order:
##   1. baseline      - both slimes as the materials ship
##   2. sweep         - each of the four uniforms at min, default and max on
##                      stone_flooded, one capture each
##   3. material edit - one value on ONE material; only that slime may move
##
## The fourth demonstration, editing a line of the SHADER so that BOTH move,
## needs a .gdshader edit and so belongs to the author.

const SCENE := "res://scenes/asset_showcase.tscn"
const OUT_SUBDIR := "captures/a5/materials/"
const DRY := "res://assets/materials/stone_dry.tres"
const FLOODED := "res://assets/materials/stone_flooded.tres"

## name -> [min, default-as-shipped-in-stone_flooded, max]. The defaults are
## read from the material at run time, not written here, so this table cannot
## drift away from the .tres.
const SWEEP := ["tint", "roughness_dry", "water_darkening", "water_roughness"]

var _lines: PackedStringArray = []
var _dir := ""
var _img_scale := 1.0
var _cam: Camera3D = null
var _rects := {}


func _say(line: String) -> void:
	print(line)
	_lines.append(line)


func _init() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("capture_materials needs a real window; headless draws nothing.")
		quit(1)
		return

	var scene := (load(SCENE) as PackedScene).instantiate()
	root.add_child(scene)
	_cam = scene.get_node("CameraMaterials")
	_cam.current = true

	var dry: ShaderMaterial = load(DRY)
	var flooded: ShaderMaterial = load(FLOODED)

	_dir = (ProjectSettings.globalize_path("res://") + "../" + OUT_SUBDIR).simplify_path()
	if not _dir.ends_with("/"):
		_dir += "/"
	DirAccess.make_dir_recursive_absolute(_dir)

	for i in 30:
		await process_frame

	_say("=== materials: interface sweep and the two-material check ===")
	_say("  when     : " + Time.get_datetime_string_from_system())
	_say("  renderer : " + RenderingServer.get_video_adapter_name())
	_say("  lighting : one DirectionalLight3D energy 1.0, ambient 0.25, SSAO off")
	_say("  files    : " + _dir)

	_measure_regions(scene)
	var base := await _shot("00-baseline")
	_say("")
	_say("  baseline   dry %s   flooded %s" % [_fmt(base[0]), _fmt(base[1])])

	# ---- 2. the interface sweep, on stone_flooded -------------------------
	_say("")
	_say("  -- interface sweep: each uniform at min / default / max --")
	_say("  Values are the mean colour of the FLOODED slime. The dry slime is")
	_say("  printed too: it must not move, because only one material changes.")
	_say("")
	for name in SWEEP:
		var shipped: Variant = flooded.get_shader_parameter(name)
		var lo: Variant = _low(name)
		var hi: Variant = _high(name)
		_say("  %s   (shipped %s)" % [name, _short(shipped)])
		for step in [["min", lo], ["default", shipped], ["max", hi]]:
			flooded.set_shader_parameter(name, step[1])
			var got := await _shot("sweep-%s-%s" % [name, step[0]])
			_say("    %-8s %-22s flooded %s    dry %s"
				% [step[0], _short(step[1]), _fmt(got[1]), _fmt(got[0])])
		flooded.set_shader_parameter(name, shipped)
		_say("")

	# ---- 3. one value, one material --------------------------------------
	_say("  -- one value on ONE material --")
	var before := await _shot("30-before-material-edit")
	flooded.set_shader_parameter(&"water_darkening", 0.0)
	var after := await _shot("31-after-material-edit")
	flooded.set_shader_parameter(&"water_darkening", 0.55)
	_say("    stone_flooded water_darkening 0.55 -> 0.00")
	_say("    flooded  %s -> %s   moved %d" % [_fmt(before[1]), _fmt(after[1]),
		_distance(before[1], after[1])])
	_say("    dry      %s -> %s   moved %d" % [_fmt(before[0]), _fmt(after[0]),
		_distance(before[0], after[0])])
	if _distance(before[0], after[0]) == 0 and _distance(before[1], after[1]) > 2:
		_say("    One material changed; only its object moved. Both still")
		_say("    reference the same Shader resource.")
	else:
		_say("    UNEXPECTED - the dry slime moved, or the flooded one did not.")

	_say("")
	_say("  Still the author's to judge, from the PNGs above: whether the")
	_say("  flooded stone reads as standing water, and whether any setting")
	_say("  in the sweep breaks the look rather than merely changing it.")
	_say("=== end ===")

	var f := FileAccess.open(_dir + "SWEEP-REPORT.txt", FileAccess.WRITE)
	if f != null:
		f.store_string("\n".join(_lines) + "\n")
		f.close()
		print("  report written: ", _dir + "SWEEP-REPORT.txt")
	quit(0)


func _low(name: String) -> Variant:
	return Color(0, 0, 0, 1) if name == "tint" else 0.0


func _high(name: String) -> Variant:
	return Color(1, 1, 1, 1) if name == "tint" else 1.0


func _short(v: Variant) -> String:
	if v is Color:
		var c := v as Color
		return "(%.2f, %.2f, %.2f)" % [c.r, c.g, c.b]
	return "%.2f" % float(v)


func _fmt(c: Vector3i) -> String:
	return "%3d,%3d,%3d" % [c.x, c.y, c.z]


func _distance(a: Vector3i, b: Vector3i) -> int:
	return maxi(absi(a.x - b.x), maxi(absi(a.y - b.y), absi(a.z - b.z)))


## Screen rectangle for each slime body, from its mesh AABB through the
## camera, shrunk to the middle so the floor and the background never enter
## the average.
func _measure_regions(scene: Node) -> void:
	for pair in [["dry", "Slime/Slime_Body"], ["flooded", "SlimeFlooded/Slime_Body"]]:
		var mi := scene.get_node_or_null(NodePath(pair[1])) as MeshInstance3D
		if mi == null:
			push_error("No mesh at " + pair[1])
			continue
		var aabb := mi.global_transform * mi.get_aabb()
		var lo := Vector2(1e9, 1e9)
		var hi := Vector2(-1e9, -1e9)
		for i in 8:
			var p := _cam.unproject_position(aabb.get_endpoint(i))
			lo = lo.min(p)
			hi = hi.max(p)
		var mid := (lo + hi) * 0.5
		var half := (hi - lo) * 0.22
		_rects[pair[0]] = Rect2(mid - half, half * 2.0)


func _shot(name: String) -> Array:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	_img_scale = img.get_width() / root.get_visible_rect().size.x
	img.save_png(_dir + name + ".png")
	return [_mean(img, _rects.get("dry")), _mean(img, _rects.get("flooded"))]


func _mean(img: Image, r: Variant) -> Vector3i:
	if r == null:
		return Vector3i(-1, -1, -1)
	var rect: Rect2 = r
	var x0 := int(rect.position.x * _img_scale)
	var y0 := int(rect.position.y * _img_scale)
	var x1 := int((rect.position.x + rect.size.x) * _img_scale)
	var y1 := int((rect.position.y + rect.size.y) * _img_scale)
	var sum := Vector3(0, 0, 0)
	var n := 0
	for y in range(maxi(y0, 0), mini(y1, img.get_height())):
		for x in range(maxi(x0, 0), mini(x1, img.get_width())):
			var c := img.get_pixel(x, y)
			sum += Vector3(c.r, c.g, c.b)
			n += 1
	if n == 0:
		return Vector3i(-1, -1, -1)
	sum /= float(n)
	return Vector3i(roundi(sum.x * 255.0), roundi(sum.y * 255.0), roundi(sum.z * 255.0))
