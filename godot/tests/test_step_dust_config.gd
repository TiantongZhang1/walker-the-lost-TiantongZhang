extends SceneTree
## Effect C's configuration read-back. Revision 6.0.4.
##
##   ./scripts/run-test.sh test_step_dust_config.gd 60
##
## Every expected value below is CHANGE-BRIEF.md revision 6.0.4 section C.3's,
## so this test fails in two directions: when the scene drifts from the brief,
## and when the brief is revised and the scene is not. Same contract as
## test_hit_burst_config.gd and test_dungeon_motes_config.gd, and the same
## reason -- section 0.2's silently-discarded property names.
##
## It also reads back the **stride length out of game/main.tscn**, because
## section C.3 puts that number in a scene file rather than in the driver and
## a default that quietly differs from the brief would be invisible.
##
## A headless run draws no particles. Nothing here says what the dust looks
## like, and nothing here can see whether `scale.x = -1` really mirrors the
## emission direction -- that is G3, and only the strip settles it.

const SCENE := "res://effects/step_dust.tscn"
const MAIN := "res://game/main.tscn"

## Section C.3, on the nodes.
const NODE_VALUES := {
	"Kick": {
		"amount": 4, "one_shot": true, "explosiveness": 1.0,
		"lifetime": 0.35, "preprocess": 0.0, "local_coords": false,
	},
	"Puff": {
		"amount": 3, "one_shot": true, "explosiveness": 0.6,
		"lifetime": 0.45, "preprocess": 0.0, "local_coords": false,
	},
}

## Section C.3, on the process materials. Only REAL property names.
const PROCESS_VALUES := {
	"Kick": {
		"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_SPHERE,
		"emission_sphere_radius": 3.0,
		"spread": 45.0,
		"initial_velocity_min": 25.0, "initial_velocity_max": 60.0,
		"gravity": Vector3(0, 900, 0),
		"damping_min": 20.0, "damping_max": 50.0,
		"scale_min": 0.8, "scale_max": 1.2,
	},
	"Puff": {
		"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_SPHERE,
		"emission_sphere_radius": 4.0,
		"spread": 40.0,
		"initial_velocity_min": 5.0, "initial_velocity_max": 18.0,
		"gravity": Vector3(0, -20, 0),
		"damping_min": 10.0, "damping_max": 20.0,
		"scale_min": 1.6, "scale_max": 2.8,
	},
}

const VISIBILITY_RECT := Rect2(-32, -32, 64, 48)
const STRIDE_PX := 24.0
const RATIO_STRIDE := 0.6
const RATIO_LANDING := 1.0

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
	print("\n-- the root, and the two emitters section C.2 names --")
	var packed := load(SCENE) as PackedScene
	_check("the scene loads", packed != null)
	if packed == null:
		return
	var root := packed.instantiate()
	_check("root is a Node2D", root is Node2D, root.get_class())
	_check("it has exactly two children", root.get_child_count() == 2,
		str(root.get_child_count()))
	for name in NODE_VALUES:
		var n := root.get_node_or_null(NodePath(name))
		_check("%s exists and is a GPUParticles2D" % name,
			n != null and n is GPUParticles2D,
			"<missing>" if n == null else n.get_class())
	root.free()


func _scenario_node_settings() -> void:
	print("\n-- node settings, against revision 6.0.4 section C.3 --")
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
	print("\n-- process material, against revision 6.0.4 section C.3 --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in PROCESS_VALUES:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		if n == null:
			continue
		var pm := n.process_material as ParticleProcessMaterial
		_check("%s has a ParticleProcessMaterial" % name, pm != null)
		if pm == null:
			continue
		_check("%s particle_flag_disable_z" % name, pm.particle_flag_disable_z)
		for key in PROCESS_VALUES[name]:
			var want: Variant = PROCESS_VALUES[name][key]
			var got: Variant = pm.get(key)
			_check("%s.%s == %s" % [name, key, str(want)],
				_same(got, want), str(got))

	# Section C.2: Kick owns the direction, and the direction is the whole
	# reason the instance has to be mirrored when the player runs left.
	var kick := root.get_node_or_null(^"Kick") as GPUParticles2D
	var kpm := kick.process_material as ParticleProcessMaterial
	var want_dir := Vector3(-0.35, -1.0, 0.0).normalized()
	_check("Kick throws back and up, as section C.3",
		kpm.direction.normalized().is_equal_approx(want_dir),
		str(kpm.direction))
	# Written to six decimals in the scene file, so the length lands within
	# about 5e-7 of 1.0 rather than exactly on it. is_equal_approx's tolerance
	# is 1e-6 relative, which this clears; the first version of this check
	# used a direction that was out by 4e-5 and the check caught it.
	_check("    and it is stored normalised",
		is_equal_approx(kpm.direction.length(), 1.0),
		"length %.7f" % kpm.direction.length())
	var puff := root.get_node_or_null(^"Puff") as GPUParticles2D
	var ppm := puff.process_material as ParticleProcessMaterial
	_check("Puff goes straight up, so it has no facing to get wrong",
		ppm.direction.normalized().is_equal_approx(Vector3(0, -1, 0)),
		str(ppm.direction))
	root.free()


func _scenario_ramps_and_curves() -> void:
	print("\n-- the change over life section C.2 requires --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in ["Kick", "Puff"]:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		var pm := n.process_material as ParticleProcessMaterial
		var ramp := pm.color_ramp as GradientTexture1D
		_check("%s has a colour ramp" % name,
			ramp != null and ramp.gradient != null)
		if ramp == null or ramp.gradient == null:
			continue
		var g := ramp.gradient
		_check("%s fades to alpha 0" % name,
			is_zero_approx(g.get_color(g.get_point_count() - 1).a))
	# Section C.2: the specks darken toward the floor's colour, the puff grows.
	var kpm := (root.get_node(^"Kick") as GPUParticles2D).process_material \
		as ParticleProcessMaterial
	var kg := (kpm.color_ramp as GradientTexture1D).gradient
	var first: Color = kg.get_color(0)
	var last: Color = kg.get_color(kg.get_point_count() - 1)
	var moved := absf(first.r - last.r) + absf(first.g - last.g) \
		+ absf(first.b - last.b)
	_check("Kick darkens as well as fading", moved > 0.01,
		"rgb delta %.3f" % moved)
	_check("Kick has no scale curve (section C.3 says flat 1.0)",
		kpm.scale_curve == null)
	var ppm := (root.get_node(^"Puff") as GPUParticles2D).process_material \
		as ParticleProcessMaterial
	_check("Puff has a scale curve, so it grows as it thins",
		ppm.scale_curve != null
			and (ppm.scale_curve as CurveTexture).curve != null)
	root.free()


func _scenario_draw() -> void:
	print("\n-- draw: this is dirt, so neither emitter is additive --")
	var root := (load(SCENE) as PackedScene).instantiate()
	for name in ["Kick", "Puff"]:
		var n := root.get_node_or_null(NodePath(name)) as GPUParticles2D
		_check("%s is not additive" % name, n.material == null,
			"<set>" if n.material != null else "null")
		_check("%s does not pin a seed" % name, not n.use_fixed_seed)
	root.free()


## Section C.3 puts the stride length in a scene file. A default in the driver
## that quietly differs from the brief would never be seen.
func _scenario_stride_lives_in_the_scene() -> void:
	print("\n-- the one number that is design, read out of main.tscn --")
	var main := (load(MAIN) as PackedScene).instantiate()
	var driver := main.get_node_or_null(^"StepDustDriver")
	_check("StepDustDriver is a node in main.tscn", driver != null)
	if driver != null:
		_check("main.tscn sets stride_px to the brief's %.0f px" % STRIDE_PX,
			is_equal_approx(driver.stride_px, STRIDE_PX),
			"%.2f" % driver.stride_px)
		_check("    and it points at the room, not the player, for parenting",
			driver.room_path == NodePath(".."), str(driver.room_path))
	main.free()


## Section C.3's amount_ratio, the feature neither of the first two used.
func _scenario_amount_ratio() -> void:
	print("\n-- amount_ratio: the feature A and B did not need --")
	# In the tree, and a frame later. `instantiate()` alone does not run
	# `_ready()`, and adding a child during a SceneTree's `_init()` does not
	# run it either -- the callback lands on the next frame. `step_dust.gd`
	# reads its lifetime back from the scene in `_ready()`, so both versions
	# of this scenario before this one measured 0.000. That was the test
	# being wrong about the engine twice, not the scene being wrong, and it
	# is the reason the check is written as "equals 0.45" rather than
	# "greater than zero" -- the loose form would have passed the first time
	# and hidden both.
	var dust := (load(SCENE) as PackedScene).instantiate() as Node2D
	root.add_child(dust)
	await process_frame
	dust.call(&"fire", RATIO_STRIDE)
	_check("a stride fires at amount_ratio %.1f" % RATIO_STRIDE,
		is_equal_approx(dust.call(&"amount_ratio"), RATIO_STRIDE),
		str(dust.call(&"amount_ratio")))
	dust.call(&"fire", RATIO_LANDING)
	_check("a landing fires at amount_ratio %.1f" % RATIO_LANDING,
		is_equal_approx(dust.call(&"amount_ratio"), RATIO_LANDING),
		str(dust.call(&"amount_ratio")))
	_check("    the lifetime is read from the scene, not typed",
		is_equal_approx(dust.call(&"lifetime"), 0.45),
		"%.3f" % dust.call(&"lifetime"))
	dust.queue_free()
	await process_frame


func _init() -> void:
	_scenario_root()
	_scenario_node_settings()
	_scenario_process_settings()
	_scenario_ramps_and_curves()
	_scenario_draw()
	_scenario_stride_lives_in_the_scene()
	# The only scenario here that needs a frame, so the only one awaited.
	# Without the `await` it still RUNS -- and its three PASS lines print
	# after the summary and after quit(), so the totals are short by three
	# and nothing says so. Found by the count dropping from 63 to 60.
	await _scenario_amount_ratio()
	print("\n%d checks, %d failure%s"
		% [_checks, _failures, "" if _failures == 1 else "s"])
	print("Proves: Effect C is configured as CHANGE-BRIEF.md revision 6.0.4 says.")
	print("Proves nothing about what it looks like, and nothing about G3 -")
	print("whether scale.x = -1 mirrors the throw. That is the strip.")
	quit(1 if _failures > 0 else 0)
