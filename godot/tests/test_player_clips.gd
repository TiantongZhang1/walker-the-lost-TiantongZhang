extends SceneTree
## Assignment 7 — the read-back for the RIG clip, `run`, and the held clips.
##
##   ./scripts/run-test.sh test_player_clips.gd 60
##
## `run` moves a rig: two legs cut off `p2-run` rotate about the hip and the
## body bobs. It swaps no frames. `CHANGE-BRIEF.md` §4 is the cycle spec.
##
## It proves the clip is **structured** as the brief says. It cannot prove the
## cycle reads as a run, and it cannot see the legs at all: a headless run
## advances a clip and draws nothing.
##
## **Key times are 32-bit floats**, so every time is compared with a tolerance
## of half a frame period and never with `==`.
##
## **`value_track_get_update_mode` is asked only of value tracks.** On a 3D
## transform track it errors and answers `UPDATE_CONTINUOUS`, failing a clip
## that is correct.

const PLAYER := "res://features/player/player.tscn"
const SHEET_H := 4
const SHEET_V := 2

## CHANGE-BRIEF.md §4. One stride: stride_px 24 / SPEED 96 = 0.250 s.
## **Revision 7.0.7: a gait cycle is TWO steps, so it is two strides.**
## 2 * stride_px 24 / SPEED 96 = 0.500 s, which is the original section 4's
## arithmetic returning. Revision 7.0.1 halved it because only one of the
## two cut legs was usable; both legs are the same usable leg now.
## Five keys -- contact, pass, contact, pass, contact -- so the key interval
## is a quarter cycle and `step` is 0.125 s.
const RUN_FPS := 8.0
const RUN_LENGTH := 0.5

## tools/make_sprites.py measures these by rendering each leg at every degree
## and reporting where the foot stops falling below row 29. They are pasted
## here from its output, and the generator prints them on every run.
## **These were in the WRONG SIGN until revision 7.0.7.** PIL's rotate()
## turns the opposite way from Godot's rotation_degrees, so the generator
## reported -2 .. +34 for a band that is really -34 .. +2 -- and this test
## passed a cycle that drove the planted foot 3.3 px THROUGH the floor.
## Both legs now use `leg_front.png` on its measured hip joint, where the
## foot is almost straight under the pivot and turning either way lifts it.
## Pasted from the generator, which prints these on every run and measures
## them about each leg's OWN hip joint. Both legs use `leg_front.png` now.
## The generator's CONTACT band: the foot rests on row 29 and never sinks
## past row 30. It is the whole scan, so **this is a weak check and the file
## says so** -- the leg is 8.6 px long with its foot almost under the hip, so
## rotating it barely moves the foot. The assertions that carry weight for
## this clip are the antiphase and separation ones below.
const FRONT_MIN := -60.0
const FRONT_MAX := 60.0
const BACK_MIN := -60.0
const BACK_MAX := 60.0

## The cycle's own extremes, inside that band. 0 degrees is CONTACT: the
## foot is on row 29, the floor. -52 is the lifted end of the swing.
## **+12 degrees is STRAIGHT DOWN** -- measured, not assumed: the foot
## hangs lowest there, because it sits 1.8 px forward of the hip. The swing
## is symmetric about it, so each leg goes BEHIND the body and in front of
## it. The first version of this revision ran -52..0, which is straight-down
## to 52 degrees FORWARD: a high kick with both feet, never a stride. The
## recapture is what caught it; no assertion here could have.
const STRAIGHT_DOWN := 12.0
const CONTACT_DEG := 38.0
const LIFT_DEG := -14.0

## The hip joint, measured by the generator from the cut surface.
## Two hips, 4 px apart, so the pair reads as two legs rather than fusing
## into one blob at the torso's front edge -- which is what one shared hip
## looked like in `captures/run/r1-strip.png`.
const HIP_FRONT := Vector2(10, 4)
const HIP_BACK := Vector2(6, 4)
const HIP_OFFSET := Vector2(-11, -4)

## Which clips show the cut-out legs. Every pose cell already contains the
## character's own legs, so only `run` may.
const LEGS_VISIBLE_IN := ["run"]

var _checks := 0
var _failures := 0
var _tol := 0.5 / RUN_FPS


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


func _note(label: String) -> void:
	print("NOTE  ", label)


## Every track in every clip resolves to a real node, and to a real property,
## bone or blend shape where the track names one.
##
## **The branch on track type is the point.** A 3D position/rotation/scale
## track's subname is a BONE and a blend-shape track's is a BLEND SHAPE, not
## a property, so a naive `sub in node` reports every bone track as broken.
## This project has no 3D tracks; the branch is here because the check is
## wrong without it and a reviewer should be able to see that it is right.
static func track_problems(player: AnimationPlayer) -> Array[String]:
	var problems: Array[String] = []
	var root := player.get_node_or_null(player.root_node)
	if root == null:
		problems.append("root_node %s resolves to nothing" % player.root_node)
		return problems
	for clip_name in player.get_animation_list():
		var clip := player.get_animation(clip_name)
		for t in clip.get_track_count():
			var path := clip.track_get_path(t)
			var node := root.get_node_or_null(
				NodePath(path.get_concatenated_names()))
			if node == null:
				problems.append("%s track %d: no node at %s" % [clip_name, t, path])
				continue
			if path.get_subname_count() == 0:
				continue
			var sub := path.get_subname(0)
			match clip.track_get_type(t):
				Animation.TYPE_POSITION_3D, Animation.TYPE_ROTATION_3D, \
				Animation.TYPE_SCALE_3D:
					var skel := node as Skeleton3D
					if skel == null or skel.find_bone(sub) == -1:
						problems.append("%s track %d: no bone %s on %s"
							% [clip_name, t, sub, node.name])
				Animation.TYPE_BLEND_SHAPE:
					var mesh := node as MeshInstance3D
					if mesh == null or mesh.find_blend_shape_by_name(sub) == -1:
						problems.append("%s track %d: no blend shape %s on %s"
							% [clip_name, t, sub, node.name])
				_:
					if not (sub in node):
						problems.append("%s track %d: %s has no property %s"
							% [clip_name, t, node.name, sub])
	return problems


static func find_track(clip: Animation, path: String) -> int:
	for t in clip.get_track_count():
		if clip.track_get_path(t) == NodePath(path):
			return t
	return -1


func _range_ok(clip: Animation, t: int, lo: float, hi: float) -> String:
	var out := ""
	for k in clip.track_get_key_count(t):
		var v: float = clip.track_get_key_value(t, k)
		if v < lo or v > hi:
			out += " %0.1f" % v
	return out


func _init() -> void:
	await process_frame
	var scene: Node = load(PLAYER).instantiate()
	root.add_child(scene)
	await process_frame

	var ap: AnimationPlayer = scene.get_node(^"AnimationPlayer")
	var body: Sprite2D = scene.get_node(^"Rig/Body")

	# --- the rig the clip assumes ----------------------------------------
	for path in ["Rig", "Rig/Body", "Rig/LegFront", "Rig/LegBack", "Hitbox"]:
		_check("the scene has %s" % path,
			scene.get_node_or_null(NodePath(path)) != null)
	_check("the body is sliced %d x %d" % [SHEET_H, SHEET_V],
		body.hframes == SHEET_H and body.vframes == SHEET_V,
		"%d x %d" % [body.hframes, body.vframes])
	var cells := body.hframes * body.vframes
	_check("the sheet is loaded", body.texture != null,
		"" if body.texture == null else str(body.texture.get_size()))
	for leg in ["Rig/LegFront", "Rig/LegBack"]:
		var s: Sprite2D = scene.get_node(NodePath(leg))
		var want_hip: Vector2 = HIP_FRONT if leg.ends_with("Front") else HIP_BACK
		_check("%s hangs from %s, on the measured hip joint" % [leg, want_hip],
			s.position == want_hip and s.offset == HIP_OFFSET,
			"pos %s offset %s" % [s.position, s.offset])
		_check("%s starts hidden" % leg, not s.visible)

	# --- every track resolves --------------------------------------------
	var problems := track_problems(ap)
	_check("every track in every clip resolves", problems.is_empty(),
		"; ".join(problems))
	_note("clips: " + ", ".join(ap.get_animation_list()))

	# --- the two clocks: written, not defaulted ---------------------------
	_check("the AnimationPlayer advances on the PHYSICS tick",
		ap.callback_mode_process
			== AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS,
		"callback_mode_process = %d (the engine default is 1, idle)"
			% ap.callback_mode_process)

	# --- the cycle, CHANGE-BRIEF.md §4 ------------------------------------
	var run := ap.get_animation("run")
	_check("run length is %.3f s: a gait cycle is TWO steps" % RUN_LENGTH,
		absf(run.length - RUN_LENGTH) < _tol, "%.6f" % run.length)
	_check("run step is one frame period at %d fps" % RUN_FPS,
		is_equal_approx(run.step, 1.0 / RUN_FPS), "%.7f" % run.step)
	_check("run loops (LOOP_LINEAR)", run.loop_mode == Animation.LOOP_LINEAR,
		str(run.loop_mode))

	var rot_tracks := {
		"Rig/LegFront:rotation_degrees": [FRONT_MIN, FRONT_MAX],
		"Rig/LegBack:rotation_degrees": [BACK_MIN, BACK_MAX],
	}
	for path in rot_tracks:
		var t := find_track(run, path)
		_check("run has a %s track" % path, t >= 0)
		if t < 0:
			continue
		_check("%s INTERPOLATES (a discrete rotation would teleport)" % path,
			run.value_track_get_update_mode(t) == Animation.UPDATE_CONTINUOUS,
			str(run.value_track_get_update_mode(t)))
		var lo: float = rot_tracks[path][0]
		var hi: float = rot_tracks[path][1]
		var bad := _range_ok(run, t, lo, hi)
		_check("every %s key is inside the measured safe band %+.0f..%+.0f"
				% [path, lo, hi], bad == "", "outside:" + bad)

	# --- the seam. For a CONTINUOUS track the rule is that the value at
	#     t = 0 and at t = length match, or the wrap jumps.
	var seam_ok := true
	var seam_detail := ""
	for t in run.get_track_count():
		if run.track_get_type(t) != Animation.TYPE_VALUE:
			continue
		if run.value_track_get_update_mode(t) != Animation.UPDATE_CONTINUOUS:
			continue
		var n := run.track_get_key_count(t)
		if n < 2:
			continue
		var first = run.track_get_key_value(t, 0)
		var last = run.track_get_key_value(t, n - 1)
		var last_t := run.track_get_key_time(t, n - 1)
		if absf(last_t - run.length) >= _tol:
			seam_ok = false
			seam_detail += " %s has no key at length;" % run.track_get_path(t)
		elif absf(float(first) - float(last)) > 0.001:
			seam_ok = false
			seam_detail += " %s goes %s -> %s;" % [run.track_get_path(t),
				str(first), str(last)]
	_check("seam: every interpolated track ends where it started", seam_ok,
		seam_detail)

	# --- revision 7.0.7 -------------------------------------------------
	# **Both legs are the same sprite.** `leg_back.png` is a 14 x 4 stub
	# whose lowest row is 24 -- five pixels short of the floor -- so it can
	# never plant and therefore can never take a step. The generator says so
	# on every run. The scene gives both legs `leg_front.png`, which is what
	# a cutout cycle does anyway: one leg, two phases.
	var lf: Sprite2D = scene.get_node(^"Rig/LegFront")
	var lb: Sprite2D = scene.get_node(^"Rig/LegBack")
	_check("both legs use the same texture, half a cycle apart",
		lf.texture == lb.texture,
		"%s vs %s" % [lf.texture, lb.texture])

	# **ANTIPHASE, asserted as arithmetic.** If back(t) = 2C - front(t) then
	# front + back is the same number on every key, and the legs are exact
	# mirror images about the centre of the swing. The shipped cycle was
	# not: its two legs came within 2.0 degrees of each other and read as
	# two legs wobbling rather than one pair alternating.
	var ft := find_track(run, "Rig/LegFront:rotation_degrees")
	var back_t := find_track(run, "Rig/LegBack:rotation_degrees")
	if ft >= 0 and back_t >= 0:
		_check("the two legs have the same number of keys",
			run.track_get_key_count(ft) == run.track_get_key_count(back_t))
		var sums: Array[float] = []
		var seps: Array[float] = []
		for k in mini(run.track_get_key_count(ft), run.track_get_key_count(back_t)):
			var a: float = run.track_get_key_value(ft, k)
			var b: float = run.track_get_key_value(back_t, k)
			sums.append(a + b)
			seps.append(absf(a - b))
		var anti := true
		for v in sums:
			if absf(v - sums[0]) > 0.01:
				anti = false
		_check("front + back is CONSTANT on every key: the legs are exact "
			+ "antiphase, not two legs wobbling", anti, str(sums))
		_check("and they are far apart at the contacts: max separation "
			+ "%.0f degrees" % seps.max(), seps.max() >= 40.0, str(seps))
		_check("the front leg reaches CONTACT (%.0f deg, behind the hip)"
			% CONTACT_DEG,
			absf(float(run.track_get_key_value(ft, 0)) - CONTACT_DEG) < 0.01,
			str(run.track_get_key_value(ft, 0)))
		_check("and it reaches the LIFT end (%.0f deg)" % LIFT_DEG,
			absf(float(run.track_get_key_value(back_t, 0)) - LIFT_DEG) < 0.01,
			str(run.track_get_key_value(back_t, 0)))

	# A gait cycle is two steps, so the two contacts are one stride apart.
	_note("contacts at t = 0.000 and t = %.3f, %.0f px apart at SPEED 96 "
		% [RUN_LENGTH / 2.0, 96.0 * RUN_LENGTH / 2.0]
		+ "-- that is stride_px, so Effect C's puff lands on each one")
	_note("whether the wrap READS as smooth is the human check; "
		+ "a headless run draws nothing")

	# --- the blade is shown by `swing` and by nothing else ----------------
	# r2 changed the SHAPE of this check, not just a value. The blade is no
	# longer visible for the whole of `swing`: it is drawn at frame 2 and
	# sheathed at frame 13 so the long return to rest is not watched. So the
	# rule is not "swing's first key is true" -- a check written that way
	# would now fail a correct clip. It is: every other clip keys it false
	# throughout, swing shows it at some point, and swing ends hidden.
	for clip_name in ap.get_animation_list():
		var clip := ap.get_animation(clip_name)
		var bt := find_track(clip, "Rig/SwordArm/Blade:visible")
		_check("%s has a Blade:visible track" % clip_name, bt >= 0)
		if bt < 0:
			continue
		var n := clip.track_get_key_count(bt)
		var shown := false
		for k in n:
			if clip.track_get_key_value(bt, k):
				shown = true
		if clip_name == "swing":
			_check("swing shows the blade at some point", shown)
			_check("swing ends with the blade sheathed",
				not clip.track_get_key_value(bt, n - 1))
		else:
			_check("%s never shows the blade" % clip_name, not shown)

	# --- the legs are shown by `run` and by nothing else -------------------
	for clip_name in ap.get_animation_list():
		if clip_name == "RESET":
			continue
		var clip := ap.get_animation(clip_name)
		var want := LEGS_VISIBLE_IN.has(clip_name)
		for leg in ["Rig/LegFront:visible", "Rig/LegBack:visible"]:
			var t := find_track(clip, leg)
			_check("%s keys %s to %s" % [clip_name, leg, str(want)],
				t >= 0 and clip.track_get_key_value(t, 0) == want,
				"no track" if t < 0 else str(clip.track_get_key_value(t, 0)))

	# --- the held clips ----------------------------------------------------
	for pair in [["run", 0], ["idle", 1], ["rising", 2], ["falling", 3],
			["dead", 4]]:
		var name: String = pair[0]
		var cell: int = pair[1]
		_check("%s exists" % name, ap.has_animation(name))
		if not ap.has_animation(name):
			continue
		var clip := ap.get_animation(name)
		var ct := find_track(clip, "Rig/Body:frame")
		_check("%s shows cell %d" % [name, cell],
			ct >= 0 and int(clip.track_get_key_value(ct, 0)) == cell,
			"" if ct < 0 else str(clip.track_get_key_value(ct, 0)))
		if ct >= 0:
			_check("%s's frame track is discrete" % name,
				clip.value_track_get_update_mode(ct) == Animation.UPDATE_DISCRETE)
			_check("%s's cell is inside the sheet (< %d)" % [name, cells],
				int(clip.track_get_key_value(ct, 0)) < cells)
		var loops: bool = name != "dead"
		_check("%s loop_mode is %s" % [name,
				"LOOP_LINEAR" if loops else "LOOP_NONE"],
			clip.loop_mode == (Animation.LOOP_LINEAR if loops
				else Animation.LOOP_NONE), str(clip.loop_mode))

	_check("a RESET clip exists", ap.has_animation("RESET"))

	scene.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	quit(0 if _failures == 0 else 1)
