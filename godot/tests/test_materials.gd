extends SceneTree
## Assignment 5 part 3: the textured shader, its two materials, the hint
## experiment's two, the textures they bind and how they reach the mesh.
##
##   ./scripts/run-test.sh test_materials.gd 60
##
## Nothing here is about look. A headless run draws nothing, so this checks
## declared interfaces, resource wiring and import settings. The captures in
## captures/a5/ are what say anything about colour.
##
## THE ENGINE CANNOT SEE source_color ON A SAMPLER. Probed on 4.7.2: both
##
##     uniform sampler2D stone_albedo : source_color, filter_linear_mipmap;
##     uniform sampler2D wetness_mask : filter_linear_mipmap;
##
## come back from get_shader_uniform_list() as type 24, hint 17,
## hint_string "Texture2D" - identical. On a vec3 the same keyword is plainly
## visible (TYPE_COLOR with COLOR_NO_ALPHA instead of TYPE_VECTOR3), which is
## what makes the sampler case easy to assume away. So F4 is checked by
## reading the shader SOURCE, and the Step 3 mutation that deletes
## source_color from the colour sampler is caught there and nowhere else.
## _scenario_blind_spot asserts the blindness itself, so that a future rewrite
## that "simplifies" this back to a uniform-list check fails loudly.

const SURFACE := "res://shaders/dungeon_surface.gdshader"
const HINT := "res://shaders/hint_bands.gdshader"
const DRY := "res://assets/materials/stone_dry.tres"
const FLOODED := "res://assets/materials/stone_flooded.tres"
const HINT_WITH := "res://assets/materials/hint_with_source_color.tres"
const HINT_WITHOUT := "res://assets/materials/hint_without_source_color.tres"
const SHOWCASE := "res://scenes/asset_showcase.tscn"
const SLIME := "res://assets/models/slime.glb"

## CHANGE-BRIEF.md section 8's table, as the two materials must hold it.
const DRY_VALUES := {"water_darkening": 0.0, "water_roughness": 0.85}
const FLOODED_VALUES := {"water_darkening": 0.55, "water_roughness": 0.08}

## Section 8's import column, read with ConfigFile rather than matched as
## text: a flat key the importer ignores looks identical to a real one in a
## grep, and the assignment lists exactly that as a recorded mistake.
## compress/mode 0 = Lossless, 2 = VRAM Compressed.
## compress/normal_map 2 = Disabled.
const IMPORTS := {
	"res://assets/textures/stone_albedo.png.import": {
		"compress/mode": 2, "compress/normal_map": 2, "mipmaps/generate": true,
	},
	"res://assets/textures/wetness_mask.png.import": {
		"compress/mode": 0, "compress/normal_map": 2, "mipmaps/generate": true,
	},
	"res://assets/textures/hint_bands.png.import": {
		"compress/mode": 0, "compress/normal_map": 2, "mipmaps/generate": false,
	},
}

const HINT_BANDS := [64, 128, 192]

var _checks := 0
var _failures := 0


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


## The `uniform ... <name> ...;` declaration for `name`, from the source text.
## Everything about a sampler's hints has to come from here.
func _declaration(src: String, name: String) -> String:
	for raw in src.split("\n"):
		var line := raw.strip_edges()
		if line.begins_with("uniform ") and line.contains(name):
			# `warn_amount` must not match `warn_amount_2`; check the boundary.
			var at := line.find(name)
			var after := line.substr(at + name.length(), 1)
			if after == "" or not (after[0].is_valid_identifier() and after != " "):
				return line
	return ""


func _uniforms(path: String) -> Dictionary:
	var shader: Shader = load(path)
	var out := {}
	if shader == null:
		return out
	for e in shader.get_shader_uniform_list():
		out[String(e["name"])] = e
	return out


# -------------------------------------------- the textured shader, declared

func _scenario_surface_interface() -> void:
	print("\n-- dungeon_surface.gdshader, as declared --")
	var shader: Shader = load(SURFACE)
	_check("    the shader loads", shader != null)
	if shader == null:
		return
	_check("    shader_type is spatial",
		shader.get_mode() == Shader.MODE_SPATIAL, "mode=%d" % shader.get_mode())

	var u := _uniforms(SURFACE)
	for name in ["stone_albedo", "wetness_mask", "tint", "roughness_dry",
			"water_darkening", "water_roughness"]:
		_check("    declares %s" % name, u.has(name))
	if u.size() < 6:
		return

	_check("    both textures are sampler uniforms",
		int(u["stone_albedo"]["type"]) == TYPE_OBJECT
			and int(u["wetness_mask"]["type"]) == TYPE_OBJECT)
	# source_color IS visible on a vec3 - this is the contrast that makes the
	# sampler blind spot below worth asserting.
	_check("    tint is a source_color vec3 (TYPE_COLOR, COLOR_NO_ALPHA)",
		int(u["tint"]["type"]) == TYPE_COLOR
			and int(u["tint"]["hint"]) == PROPERTY_HINT_COLOR_NO_ALPHA,
		"type=%d hint=%d" % [int(u["tint"]["type"]), int(u["tint"]["hint"])])

	var ranged := 0
	for name in ["roughness_dry", "water_darkening", "water_roughness"]:
		if int(u[name]["hint"]) == PROPERTY_HINT_RANGE \
				and String(u[name]["hint_string"]).begins_with("0.0,1.0"):
			ranged += 1
	_check("    all three floats carry hint_range(0.0, 1.0)", ranged == 3,
		"%d of 3" % ranged)

	var src := FileAccess.get_file_as_string(SURFACE)
	_check("    at least two group_uniforms groups",
		src.contains("group_uniforms surface") and src.contains("group_uniforms water"))

	# F4, and the only place it can be caught.
	var albedo_line := _declaration(src, "stone_albedo")
	var mask_line := _declaration(src, "wetness_mask")
	_check("F4  the COLOUR sampler declares source_color",
		albedo_line.contains("source_color"), albedo_line)
	_check("F4  the DATA sampler does NOT declare source_color",
		mask_line != "" and not mask_line.contains("source_color"), mask_line)
	_check("    both samplers set a filter explicitly",
		albedo_line.contains("filter_") and mask_line.contains("filter_"))


## The assertion this suite would be wrong without. If a later version decides
## the uniform list is good enough for F4, this fails and says why.
func _scenario_blind_spot() -> void:
	print("\n-- the engine cannot see source_color on a sampler --")
	var u := _uniforms(SURFACE)
	if not (u.has("stone_albedo") and u.has("wetness_mask")):
		return
	var a: Dictionary = u["stone_albedo"]
	var b: Dictionary = u["wetness_mask"]
	var same := int(a["type"]) == int(b["type"]) \
		and int(a["hint"]) == int(b["hint"]) \
		and String(a["hint_string"]) == String(b["hint_string"])
	_check("    the two samplers are INDISTINGUISHABLE to get_shader_uniform_list",
		same, "type=%d hint=%d %s for both"
			% [int(a["type"]), int(a["hint"]), a["hint_string"]])
	_check("    therefore F4 is checked by reading the source, above", true)


# ------------------------------------------------- the hint experiment

func _scenario_hint_shader() -> void:
	print("\n-- hint_bands.gdshader --")
	var shader: Shader = load(HINT)
	_check("    the shader loads", shader != null)
	if shader == null:
		return
	_check("    shader_type is spatial",
		shader.get_mode() == Shader.MODE_SPATIAL)

	var src := FileAccess.get_file_as_string(HINT)
	# Without this the light scales ALBEDO and section 7's numbers mean nothing.
	_check("    render_mode unshaded", src.contains("render_mode unshaded"))

	var u := _uniforms(HINT)
	_check("    declares both samplers and the bool",
		u.has("bands_srgb") and u.has("bands_data") and u.has("use_source_color"))
	if u.has("use_source_color"):
		_check("    use_source_color is a bool",
			int(u["use_source_color"]["type"]) == TYPE_BOOL)

	var srgb_line := _declaration(src, "bands_srgb")
	var data_line := _declaration(src, "bands_data")
	_check("    bands_srgb declares source_color", srgb_line.contains("source_color"))
	_check("    bands_data does NOT", data_line != "" and not data_line.contains("source_color"))
	_check("    both are filter_nearest - a 3-texel image must not be blended",
		srgb_line.contains("filter_nearest") and data_line.contains("filter_nearest"))


# ---------------------------------------------------------- the materials

func _scenario_two_materials() -> void:
	print("\n-- one shader, two materials --")
	var dry: ShaderMaterial = load(DRY)
	var flooded: ShaderMaterial = load(FLOODED)
	_check("    both materials load", dry != null and flooded != null)
	if dry == null or flooded == null:
		return

	_check("    both reference the SAME Shader object",
		dry.shader == flooded.shader and dry.shader != null,
		"" if dry.shader == null else dry.shader.resource_path)

	var differ: Array = []
	for name in ["tint", "roughness_dry", "water_darkening", "water_roughness",
			"stone_albedo", "wetness_mask"]:
		if str(dry.get_shader_parameter(name)) != str(flooded.get_shader_parameter(name)):
			differ.append(name)
	differ.sort()
	_check("    they differ in exactly tint, water_darkening, water_roughness",
		differ == ["tint", "water_darkening", "water_roughness"], str(differ))

	for pair in [["stone_dry", dry, DRY_VALUES], ["stone_flooded", flooded, FLOODED_VALUES]]:
		var mat: ShaderMaterial = pair[1]
		var want: Dictionary = pair[2]
		var ok := true
		var seen: Array = []
		for key in want:
			var got: float = float(mat.get_shader_parameter(key))
			seen.append("%s=%.2f" % [key, got])
			if not is_equal_approx(got, float(want[key])):
				ok = false
		_check("    %s matches section 8" % pair[0], ok, ", ".join(seen))
		_check("    %s binds both textures" % pair[0],
			mat.get_shader_parameter(&"stone_albedo") != null
				and mat.get_shader_parameter(&"wetness_mask") != null)


func _scenario_hint_materials() -> void:
	print("\n-- the hint pair: same file, same shader, one bool apart --")
	var a: ShaderMaterial = load(HINT_WITH)
	var b: ShaderMaterial = load(HINT_WITHOUT)
	_check("    both load", a != null and b != null)
	if a == null or b == null:
		return
	_check("    same Shader object", a.shader == b.shader and a.shader != null)
	_check("    the bool differs, true then false",
		a.get_shader_parameter(&"use_source_color") == true
			and b.get_shader_parameter(&"use_source_color") == false)

	var paths := []
	for mat in [a, b]:
		for slot in ["bands_srgb", "bands_data"]:
			var tex: Texture2D = mat.get_shader_parameter(slot)
			paths.append("" if tex == null else tex.resource_path)
	var unique := {}
	for p in paths:
		unique[p] = true
	_check("    all four sampler slots hold the SAME file",
		unique.size() == 1 and not unique.has(""), ", ".join(unique.keys()))


# ------------------------------------------------- textures and importing

func _scenario_import_settings() -> void:
	print("\n-- import settings, parsed with ConfigFile --")
	for path in IMPORTS:
		var cfg := ConfigFile.new()
		var err := cfg.load(path)
		if err != OK:
			_check("    %s loads" % path.get_file(), false, "error %d" % err)
			continue
		var want: Dictionary = IMPORTS[path]
		var wrong: Array = []
		var seen: Array = []
		for key in want:
			# A missing key is not the same as a key set to the right value:
			# the importer would use its own default and the .import would
			# never say so, which is the whole reason these are set explicitly.
			if not cfg.has_section_key("params", key):
				wrong.append("%s ABSENT" % key)
				continue
			var got: Variant = cfg.get_value("params", key)
			seen.append("%s=%s" % [key, got])
			if got != want[key]:
				wrong.append("%s=%s wanted %s" % [key, got, want[key]])
		_check("    %s" % path.get_file(), wrong.is_empty(),
			", ".join(wrong) if not wrong.is_empty() else ", ".join(seen))


## The prediction in section 7 is about the numbers in the FILE. Read them
## back rather than trusting the script that wrote them.
func _scenario_texture_data() -> void:
	print("\n-- what hint_bands.png actually stores --")
	var img := Image.load_from_file(
		ProjectSettings.globalize_path("res://assets/textures/hint_bands.png"))
	_check("    the file loads", img != null)
	if img == null:
		return
	_check("    it is 3 x 1", img.get_width() == 3 and img.get_height() == 1,
		str(img.get_size()))
	var got: Array = []
	var ok := true
	for i in mini(3, img.get_width()):
		var v := roundi(img.get_pixel(i, 0).r * 255.0)
		got.append(v)
		if v != HINT_BANDS[i]:
			ok = false
	_check("    texels are 64, 128, 192 as section 7 predicts from", ok, str(got))


# ------------------------------------------------------------ the wiring

func _scenario_wiring() -> void:
	print("\n-- how the material reaches the mesh --")
	var imp := FileAccess.get_file_as_string("res://assets/models/slime.glb.import")
	_check("    slime.glb.import sets use_external on A3_SlimeBody",
		imp.contains('"A3_SlimeBody"') and imp.contains('"use_external/enabled": true'))
	_check("    it points at stone_dry.tres",
		imp.contains("res://assets/materials/stone_dry.tres"))

	# The assertion that matters: not what the .import says, but what came out.
	var model := (load(SLIME) as PackedScene).instantiate()
	var body := model.get_node_or_null(^"Slime_Body") as MeshInstance3D
	_check("    the imported model has a Slime_Body mesh", body != null)
	if body != null and body.mesh != null:
		var m := body.mesh.surface_get_material(0)
		_check("    its surface material IS stone_dry.tres, after import",
			m != null and m.resource_path == DRY,
			"<null>" if m == null else m.resource_path)
	model.free()

	var scene := (load(SHOWCASE) as PackedScene).instantiate()
	var flooded := scene.get_node_or_null(^"SlimeFlooded")
	_check("    the showcase holds a second slime", flooded != null)
	if flooded != null:
		var fb := flooded.get_node_or_null(^"Slime_Body") as MeshInstance3D
		var ov: Material = null if fb == null else fb.get_surface_override_material(0)
		_check("    its body is overridden with stone_flooded.tres",
			ov != null and ov.resource_path == FLOODED,
			"<null>" if ov == null else ov.resource_path)
	scene.free()


func _init() -> void:
	_scenario_surface_interface()
	_scenario_blind_spot()
	_scenario_hint_shader()
	_scenario_two_materials()
	_scenario_hint_materials()
	_scenario_import_settings()
	_scenario_texture_data()
	_scenario_wiring()
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: declared interfaces, resource wiring and import settings.")
	print("Proves nothing about look - see captures/a5/ for that.")
	quit(1 if _failures > 0 else 0)
