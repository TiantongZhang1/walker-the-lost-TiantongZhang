extends SceneTree
## Effect B's configuration read-back. Assignment 6, Step 4.
##
##   ./scripts/run-test.sh test_dungeon_motes_config.gd 60
##
## Every expected value below is CHANGE-BRIEF.md section 2.3's, so this test
## fails in two directions: when the scene drifts from the brief, and when the
## brief is revised and the scene is not. Same contract as
## test_hit_burst_config.gd.
##
## **Why a read-back test exists at all.** Section 0.2: on this build
## `ParticleProcessMaterial` HAS `initial_velocity`, `scale` and `damping` as
## Vector2 properties with usage 12 (EDITOR | INTERNAL) that are never written
## to a scene file, so a .tscn naming one loads without complaint, stores
## nothing, and runs at the default.
##
## **Effect B added a third variant of that trap, found while building it.**
## On a LIVE material whose `emission_shape` is still Point,
## `get_property_list()` reports `emission_box_extents` with usage **0** --
## Godot hides the shape-specific properties of every inactive shape. So a
## check that decides whether a property is real by reading an instance's
## property list gets a different answer depending on an unrelated property's
## value. `ClassDB.class_get_property_list()` reports it as usage 6 either way.
## Everything below therefore reads the value with `get()` and compares it,
## which is immune to both.
##
## A headless run draws no particles. This proves the effect is CONFIGURED as
## the brief says, and B1 -- the one thing `preprocess` exists for -- cannot be
## proved here at all. That is frame 10 of the motes strip, and F4 says so.

const SCENE := "res://effects/dungeon_motes.tscn"
const BURST := "res://effects/hit_burst.tscn"

## Section 2.3, on the node.
const NODE_VALUES := {
	"amount": 60,
	"one_shot": false,
	"explosiveness": 0.0,
	"lifetime": 8.0,
	"preprocess": 8.0,
	"local_coords": false,
	"emitting": true,
}

## Section 2.3, on the process material. Only REAL property names.
const PROCESS_VALUES := {
	"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_BOX,
	"emission_shape_offset": Vector3(320, 100, 0),
	"emission_box_extents": Vector3(320, 100, 1),
	"spread": 25.0,
	"initial_velocity_min": 2.0,
	"initial_velocity_max": 6.0,
	"gravity": Vector3(0, 2, 0),
	"damping_min": 0.0,
	"damping_max": 0.0,
	"scale_min": 1.0,
	"scale_max": 2.0,
}

## Section 2.3: the air volume, set and checked, not generated.
const VISIBILITY_RECT := Rect2(0, 0, 640, 200)
## Section 2.2: warm pale #c89a5a.
const MOTE_COLOUR := Color(0.784314, 0.603922, 0.352941)
## Section 2.2: alpha 0 -> 0.35 -> 0.35 -> 0.
const PEAK_ALPHA := 0.35

var _checks := 0
var _failures := 0


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


func _same(got: Variant, want: Variant) -> bool:
	if got is float and want is float:
		return is_equal_approx(got, want)
	if got is Vector3 and want is Vector3:
		return (got as Vector3).is_equal_approx(want)
	return got == want


func _scenario_root() -> void:
	print("\n-- the root: one emitter, because the effect has one job --")
	var packed := load(SCENE) as PackedScene
	_check("the scene loads", packed != null)
	if packed == null:
		return
	var root := packed.instantiate()
	_check("root is a GPUParticles2D", root is GPUParticles2D, root.get_class())
	_check("section 2.2: it is ONE emitter, no children",
		root.get_child_count() == 0, str(root.get_child_count()))
	_check("B3  process_mode is INHERIT, so a paused game is a frozen field",
		root.process_mode == Node.PROCESS_MODE_INHERIT,
		str(root.process_mode))
	root.free()


func _scenario_node_settings() -> void:
	print("\n-- node settings, against CHANGE-BRIEF.md section 2.3 --")
	var n := (load(SCENE) as PackedScene).instantiate() as GPUParticles2D
	for key in NODE_VALUES:
		var want: Variant = NODE_VALUES[key]
		var got: Variant = n.get(key)
		_check("%s == %s" % [key, str(want)], _same(got, want), str(got))
	_check("visibility_rect is the brief's, set not generated",
		n.visibility_rect.is_equal_approx(VISIBILITY_RECT),
		str(n.visibility_rect))
	# Section 2.4 B2 reads `emitting`; a scene that shipped with it off would
	# make every B2 check pass for the wrong reason.
	_check("    it is emitting from the scene, not from a script",
		n.emitting)
	n.free()


func _scenario_process_settings() -> void:
	print("\n-- process material, against CHANGE-BRIEF.md section 2.3 --")
	var n := (load(SCENE) as PackedScene).instantiate() as GPUParticles2D
	var pm := n.process_material as ParticleProcessMaterial
	_check("it has a ParticleProcessMaterial", pm != null)
	if pm == null:
		n.free()
		return
	_check("particle_flag_disable_z", pm.particle_flag_disable_z)
	for key in PROCESS_VALUES:
		var want: Variant = PROCESS_VALUES[key]
		var got: Variant = pm.get(key)
		_check("%s == %s" % [key, str(want)], _same(got, want), str(got))

	# Section 2.3's direction is given as (-0.4, 1.0) "normalised". Both halves
	# are checked: that it points where the brief says, and that it is a unit
	# vector -- an un-normalised direction still works and still drifts down
	# and left, so nothing would look wrong.
	var want_dir := Vector3(-0.4, 1.0, 0.0).normalized()
	var got_dir: Vector3 = pm.direction
	_check("direction points down and slightly left, as section 2.3",
		got_dir.normalized().is_equal_approx(want_dir), str(got_dir))
	_check("    and it is stored normalised",
		is_equal_approx(got_dir.length(), 1.0), "length %.6f" % got_dir.length())
	n.free()


func _scenario_ramp() -> void:
	print("\n-- the colour ramp: alpha in, alpha out, no popping --")
	var n := (load(SCENE) as PackedScene).instantiate() as GPUParticles2D
	var pm := n.process_material as ParticleProcessMaterial
	var ramp := pm.color_ramp as GradientTexture1D if pm != null else null
	_check("there is a colour ramp",
		ramp != null and ramp.gradient != null)
	if ramp == null or ramp.gradient == null:
		n.free()
		return
	var g := ramp.gradient
	_check("section 2.2: four points, so it fades in AND out",
		g.get_point_count() == 4, str(g.get_point_count()))
	if g.get_point_count() == 4:
		var a: Color = g.get_color(0)
		var b: Color = g.get_color(1)
		var c: Color = g.get_color(2)
		var d: Color = g.get_color(3)
		_check("B: born invisible", is_zero_approx(a.a), "%.3f" % a.a)
		_check("B: reaches %.2f and holds it" % PEAK_ALPHA,
			is_equal_approx(b.a, PEAK_ALPHA) and is_equal_approx(c.a, PEAK_ALPHA),
			"%.3f .. %.3f" % [b.a, c.a])
		_check("B: dies invisible", is_zero_approx(d.a), "%.3f" % d.a)
		# Unlike Effect A, section 2.2 asks for alpha-only change here: the hue
		# must NOT drift, or lit motes would change colour as they age.
		var hue_moved := 0.0
		for col in [a, b, c, d]:
			hue_moved = maxf(hue_moved, absf(col.r - MOTE_COLOUR.r)
				+ absf(col.g - MOTE_COLOUR.g) + absf(col.b - MOTE_COLOUR.b))
		_check("the colour stays #c89a5a throughout; only alpha moves",
			hue_moved < 0.01, "worst rgb delta %.4f" % hue_moved)
	n.free()


func _scenario_draw() -> void:
	print("\n-- draw: NOT additive --")
	var n := (load(SCENE) as PackedScene).instantiate() as GPUParticles2D
	# Section 2.3: additive motes would bloom inside a torch pool. The default
	# (no CanvasItemMaterial) is Mix.
	_check("no CanvasItemMaterial, so the blend mode is Mix",
		n.material == null,
		"<set>" if n.material != null else "null")
	_check("the effect scene does not pin a seed", not n.use_fixed_seed)
	n.free()


## Section 2.1 names `preprocess` as the feature Effect A does not use. That is
## a claim about TWO scenes, so it is checked against both.
func _scenario_distinguishing_feature() -> void:
	print("\n-- the feature Effect A does not use --")
	var motes := (load(SCENE) as PackedScene).instantiate() as GPUParticles2D
	_check("B  preprocess is 8.0, one full lifetime",
		is_equal_approx(motes.preprocess, motes.lifetime)
			and is_equal_approx(motes.preprocess, 8.0),
		"preprocess %.2f, lifetime %.2f" % [motes.preprocess, motes.lifetime])
	motes.free()

	var burst := (load(BURST) as PackedScene).instantiate()
	var all_zero := true
	for child in burst.get_children():
		if child is GPUParticles2D and not is_zero_approx(
				(child as GPUParticles2D).preprocess):
			all_zero = false
	_check("A  all three of Effect A's emitters are at preprocess 0.0",
		all_zero)
	# And the other way round: A uses Point and Sphere, B uses Box.
	var shapes: Array = []
	for child in burst.get_children():
		if child is GPUParticles2D:
			var pm := (child as GPUParticles2D).process_material \
				as ParticleProcessMaterial
			if pm != null:
				shapes.append(pm.emission_shape)
	_check("A  and none of them uses a Box emission shape",
		not shapes.has(ParticleProcessMaterial.EMISSION_SHAPE_BOX),
		str(shapes))
	burst.free()


func _init() -> void:
	_scenario_root()
	_scenario_node_settings()
	_scenario_process_settings()
	_scenario_ramp()
	_scenario_draw()
	_scenario_distinguishing_feature()
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: Effect B is configured as CHANGE-BRIEF.md section 2.3 says.")
	print("Proves nothing about what it looks like, and nothing about B1 -")
	print("a headless run draws no field. That is frame 10 of the motes strip.")
	quit(1 if _failures > 0 else 0)
