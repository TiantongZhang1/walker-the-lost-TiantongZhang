extends SceneTree
## Effect A's configuration read-back. Assignment 6, Step 2.
##
##   ./scripts/run-test.sh test_hit_burst_config.gd 60
##
## Every expected value below is CHANGE-BRIEF.md section 1.3's, so this test
## fails in two directions: when the scene drifts from the brief, and when
## the brief is revised and the scene is not. A kept tuning change updates
## both in the same commit, which is the loop working as designed.
##
## **Why a read-back test exists at all.** CHANGE-BRIEF.md section 0.2 is the
## answer, and it was measured on this build rather than taken from the
## assignment's summary. ParticleProcessMaterial HAS `initial_velocity`,
## `scale` and `damping` -- as Vector2 properties with usage 12,
## EDITOR | INTERNAL, which are never written to a scene file. So a .tscn
## that says
##
##     initial_velocity = 120.0
##
## loads without a word of complaint, stores nothing, and runs the effect at
## the default. Nothing errors, the state tests pass, and it looks wrong.
## `scale_random` is the other kind: it does not exist at all, and set() is a
## no-op. This test reads the REAL property back and is the only thing in the
## repository that can tell either apart from a correct scene.
##
## A headless run draws no particles. This proves the effect is CONFIGURED as
## the brief says. It proves nothing about what it looks like; that is the
## frame strip's job, and the verdict is the author's.

const SCENE := "res://effects/hit_burst.tscn"

## CHANGE-BRIEF.md section 1.3, verbatim. Node path -> node properties.
const NODE_VALUES := {
	"Flash": {
		"amount": 4, "one_shot": true, "explosiveness": 1.0,
		"lifetime": 0.12, "preprocess": 0.0, "local_coords": false,
	},
	"Grit": {
		"amount": 20, "one_shot": true, "explosiveness": 0.85,
		"lifetime": 0.6, "preprocess": 0.0, "local_coords": false,
	},
	"Dust": {
		"amount": 8, "one_shot": true, "explosiveness": 0.4,
		"lifetime": 0.45, "preprocess": 0.0, "local_coords": false,
	},
}

## Section 1.3 again, for the process material of each emitter. Only REAL
## property names appear here -- see the header.
const PROCESS_VALUES := {
	"Flash": {
		"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_POINT,
		"spread": 55.0,
		"initial_velocity_min": 20.0, "initial_velocity_max": 50.0,
		"gravity": Vector3(0, 0, 0),
		"damping_min": 0.0, "damping_max": 0.0,
		"scale_min": 5.0, "scale_max": 7.0,   # r1, 2026-11-07
	},
	"Grit": {
		"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_SPHERE,
		"emission_sphere_radius": 6.0,
		"spread": 70.0,
		"initial_velocity_min": 70.0, "initial_velocity_max": 160.0,
		"gravity": Vector3(0, 900, 0),
		"damping_min": 40.0, "damping_max": 90.0,
		"scale_min": 0.8, "scale_max": 1.4,
	},
	"Dust": {
		"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_SPHERE,
		"emission_sphere_radius": 4.0,
		"spread": 35.0,
		"initial_velocity_min": 10.0, "initial_velocity_max": 40.0,
		"gravity": Vector3(0, -30, 0),
		"damping_min": 10.0, "damping_max": 20.0,
		"scale_min": 2.0, "scale_max": 3.5,
	},
}

## Section 1.3: set and checked, not generated.
const VISIBILITY_RECT := Rect2(-48, -64, 96, 96)

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
	print("\n-- the root, and the three emitters the brief names --")
	var packed := load(SCENE) as PackedScene
	_check("the scene loads", packed != null)
	if packed == null:
		return
	var root := packed.instantiate()
	_check("root is a Node2D", root is Node2D,
		root.get_class())
	_check("it has exactly three children", root.get_child_count() == 3,
		str(root.get_child_count()))
	for name in NODE_VALUES:
		var n := root.get_node_or_null(NodePath(name))
		_check("%s exists and is a GPUParticles2D" % name,
			n != null and n is GPUParticles2D,
			"<missing>" if n == null else n.get_class())
	root.free()


func _scenario_node_settings() -> void:
	print("\n-- node settings, against CHANGE-BRIEF.md section 1.3 --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in NODE_VALUES:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		if n == null:
			continue
		for key in NODE_VALUES[name]:
			var want: Variant = NODE_VALUES[name][key]
			var got: Variant = n.get(key)
			_check("%s.%s == %s" % [name, key, str(want)],
				_same(got, want), str(got))
		_check("%s.visibility_rect is the brief's, set not generated" % name,
			n.visibility_rect.is_equal_approx(VISIBILITY_RECT),
			str(n.visibility_rect))
	root.free()


func _scenario_process_settings() -> void:
	print("\n-- process material, against CHANGE-BRIEF.md section 1.3 --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in PROCESS_VALUES:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		if n == null:
			continue
		var pm := n.process_material as ParticleProcessMaterial
		_check("%s has a ParticleProcessMaterial" % name, pm != null)
		if pm == null:
			continue
		# 2D particles must not drift in Z. The assignment names a missing
		# Disable Z as one of the chapter's predicted failures.
		_check("%s particle_flag_disable_z" % name,
			pm.particle_flag_disable_z)
		for key in PROCESS_VALUES[name]:
			var want: Variant = PROCESS_VALUES[name][key]
			var got: Variant = pm.get(key)
			_check("%s.%s == %s" % [name, key, str(want)],
				_same(got, want), str(got))
	root.free()


func _scenario_ramps_and_curves() -> void:
	print("\n-- the change over life the brief requires --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in ["Flash", "Grit", "Dust"]:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		if n == null:
			continue
		var pm := n.process_material as ParticleProcessMaterial
		if pm == null:
			continue
		var ramp := pm.color_ramp as GradientTexture1D
		_check("%s has a colour ramp" % name, ramp != null and ramp.gradient != null)
		if ramp != null and ramp.gradient != null:
			var g := ramp.gradient
			var first: Color = g.get_color(0)
			var last: Color = g.get_color(g.get_point_count() - 1)
			_check("%s fades to alpha 0" % name, is_zero_approx(last.a),
				str(last.a))
			# Section 1.2: alpha alone is not enough. Flash and Grit must
			# change hue or value too; Dust is allowed to be alpha-only
			# because its scale_curve carries the change instead.
			if name != "Dust":
				var moved := absf(first.r - last.r) + absf(first.g - last.g) \
					+ absf(first.b - last.b)
				_check("%s changes more than alpha" % name, moved > 0.01,
					"rgb delta %.3f" % moved)
	# Flash and Dust carry a scale curve; Grit is flat by the brief.
	for name in ["Flash", "Dust"]:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		var pm := n.process_material as ParticleProcessMaterial if n != null else null
		if pm == null:
			continue
		_check("%s has a scale curve" % name,
			pm.scale_curve != null and (pm.scale_curve as CurveTexture).curve != null)
	var grit := root.get_node_or_null(^"Grit") as GPUParticles2D
	if grit != null:
		var gpm := grit.process_material as ParticleProcessMaterial
		_check("Grit has no scale curve (the brief says flat 1.0)",
			gpm != null and gpm.scale_curve == null,
			"<set>" if gpm != null and gpm.scale_curve != null else "null")
	root.free()


func _scenario_draw() -> void:
	print("\n-- draw: the blend mode the brief puts on Flash alone --")
	var root := (load(SCENE) as PackedScene).instantiate()
	var flash := root.get_node_or_null(^"Flash") as GPUParticles2D
	var fm := flash.material as CanvasItemMaterial if flash != null else null
	_check("Flash has a CanvasItemMaterial", fm != null)
	if fm != null:
		_check("Flash blends additively",
			fm.blend_mode == CanvasItemMaterial.BLEND_MODE_ADD,
			str(fm.blend_mode))
	for name in ["Grit", "Dust"]:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		_check("%s does NOT blend additively (it is matter, not light)" % name,
			n != null and n.material == null,
			"<set>" if n != null and n.material != null else "null")
	root.free()


func _scenario_no_fixed_seed() -> void:
	print("\n-- the effect scene must NOT pin a seed --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in ["Flash", "Grit", "Dust"]:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		if n == null:
			continue
		# Section 1.5: the PREVIEW pins use_fixed_seed on its own instance so
		# before-and-after strips are comparable. Pinning it here would make
		# every burst in the game identical, which is the one thing section
		# 1.2's variation paragraph exists to prevent.
		_check("%s.use_fixed_seed is off" % name, not n.use_fixed_seed)
	root.free()


func _init() -> void:
	_scenario_root()
	_scenario_node_settings()
	_scenario_process_settings()
	_scenario_ramps_and_curves()
	_scenario_draw()
	_scenario_no_fixed_seed()
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: Effect A is configured as CHANGE-BRIEF.md section 1.3 says.")
	print("Proves nothing about what it looks like - that is the frame strip,")
	print("and the verdict on it is the author's.")
	quit(1 if _failures > 0 else 0)
