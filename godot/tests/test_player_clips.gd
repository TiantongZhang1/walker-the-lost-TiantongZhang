extends SceneTree
## Assignment 7 — the read-back for every clip in `animations/player.tres`.
##
##   ./scripts/run-test.sh test_player_clips.gd 60
##
## It reads the clips back off the loaded resource and holds them against
## `CHANGE-BRIEF.md` §4 and §6. It proves the clips are **structured** as the
## brief says. It cannot prove the motion reads: a headless run advances a
## clip and draws nothing.
##
## **Key times are 32-bit floats.** A `.tres` round trip loses the last
## digits, so every time is compared with a tolerance of half a frame period
## and never with `==`. That is predicted failure H4.
##
## **`value_track_get_update_mode` is asked only of value tracks.** On a 3D
## transform track it errors and answers `UPDATE_CONTINUOUS`, failing a clip
## that is correct — one of the mistakes Assignment 7 names.

const PLAYER := "res://features/player/player.tscn"
const SHEET_H := 6
const SHEET_V := 2

## CHANGE-BRIEF.md §4: six frames at 12 fps, two 24 px strides at SPEED 96.
const RUN_FPS := 12.0
const RUN_FRAMES := 6
const RUN_LENGTH := 0.5

var _checks := 0
var _failures := 0


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
## This project has no 3D tracks today; the branch is here because the check
## is wrong without it and a reviewer should be able to see that it is right.
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


func _frame_track(clip: Animation) -> int:
	for t in clip.get_track_count():
		if clip.track_get_path(t) == NodePath("Sprite2D:frame"):
			return t
	return -1


func _init() -> void:
	await process_frame
	var scene: Node = load(PLAYER).instantiate()
	root.add_child(scene)
	await process_frame

	var ap: AnimationPlayer = scene.get_node(^"AnimationPlayer")
	var sprite: Sprite2D = scene.get_node(^"Sprite2D")

	# --- the sheet the frame numbers mean something against ---------------
	_check("sprite is sliced %d x %d" % [SHEET_H, SHEET_V],
		sprite.hframes == SHEET_H and sprite.vframes == SHEET_V,
		"%d x %d" % [sprite.hframes, sprite.vframes])
	var cells := sprite.hframes * sprite.vframes
	_check("the sheet's texture is loaded", sprite.texture != null,
		"" if sprite.texture == null else str(sprite.texture.get_size()))

	# --- every track resolves --------------------------------------------
	var problems := track_problems(ap)
	_check("every track resolves to a real node and property",
		problems.is_empty(), "; ".join(problems))
	_note("clips: " + ", ".join(ap.get_animation_list()))

	# --- the two clocks: this is written, not defaulted -------------------
	_check("AnimationPlayer advances on the PHYSICS tick",
		ap.callback_mode_process
			== AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS,
		"callback_mode_process = %d (engine default is 1, idle)"
			% ap.callback_mode_process)

	# --- the cycle, CHANGE-BRIEF.md §4 ------------------------------------
	var run := ap.get_animation("run")
	var tol := 0.5 / RUN_FPS
	_check("run length is %.3f s" % RUN_LENGTH,
		absf(run.length - RUN_LENGTH) < tol, "%.6f" % run.length)
	_check("run step is one frame period at %d fps" % RUN_FPS,
		is_equal_approx(run.step, 1.0 / RUN_FPS), "%.7f" % run.step)
	_check("run loops (LOOP_LINEAR)", run.loop_mode == Animation.LOOP_LINEAR,
		str(run.loop_mode))

	var t := _frame_track(run)
	_check("run has a Sprite2D:frame track", t >= 0, str(t))
	_check("that track is a value track",
		run.track_get_type(t) == Animation.TYPE_VALUE, str(run.track_get_type(t)))
	# Only now, and only because it IS a value track.
	if run.track_get_type(t) == Animation.TYPE_VALUE:
		_check("run's frame track is UPDATE_DISCRETE",
			run.value_track_get_update_mode(t) == Animation.UPDATE_DISCRETE,
			str(run.value_track_get_update_mode(t)))

	_check("run has %d keys" % RUN_FRAMES,
		run.track_get_key_count(t) == RUN_FRAMES,
		str(run.track_get_key_count(t)))

	var ok_times := true
	var ok_cells := true
	var ok_range := true
	var seen: Array = []
	for k in run.track_get_key_count(t):
		var want := float(k) / RUN_FPS
		if absf(run.track_get_key_time(t, k) - want) >= tol:
			ok_times = false
		var v: int = run.track_get_key_value(t, k)
		seen.append(v)
		if v != k:
			ok_cells = false
		if v >= cells:
			ok_range = false
	_check("every key lands on its frame at %d fps" % RUN_FPS, ok_times,
		"tolerance %.5f s" % tol)
	_check("the keys are cells 0-5, in order", ok_cells, str(seen))
	_check("every frame key is inside the sheet (< %d)" % cells, ok_range,
		str(seen))

	# --- the seam, CHANGE-BRIEF.md §4's three rules -----------------------
	var first: int = run.track_get_key_value(t, 0)
	var last: int = run.track_get_key_value(t, run.track_get_key_count(t) - 1)
	_check("seam 1: no duplicate across the wrap (last != first)",
		last != first, "first %d, last %d" % [first, last])
	var last_time := run.track_get_key_time(t, run.track_get_key_count(t) - 1)
	var interval := 1.0 / RUN_FPS
	_check("seam 2: the gap from the last key to length is one interval",
		absf((run.length - last_time) - interval) < tol * 0.5,
		"gap %.6f, interval %.6f" % [run.length - last_time, interval])
	_note("seam 3 is the loop_mode check above")
	_note("whether the wrap READS as smooth is the human check; "
		+ "a headless run draws nothing")

	# --- the held clips the state machine needs ---------------------------
	for pair in [["idle", 6], ["rising", 7], ["falling", 8], ["dead", 9]]:
		var name: String = pair[0]
		var cell: int = pair[1]
		_check("%s exists" % name, ap.has_animation(name))
		if not ap.has_animation(name):
			continue
		var clip := ap.get_animation(name)
		var ct := _frame_track(clip)
		_check("%s holds cell %d" % [name, cell],
			ct >= 0 and clip.track_get_key_count(ct) == 1
				and int(clip.track_get_key_value(ct, 0)) == cell,
			"" if ct < 0 else str(clip.track_get_key_value(ct, 0)))
		if ct >= 0 and clip.track_get_type(ct) == Animation.TYPE_VALUE:
			_check("%s is discrete" % name,
				clip.value_track_get_update_mode(ct) == Animation.UPDATE_DISCRETE)
		_check("%s loop_mode is %s" % [name, "LOOP_NONE" if name == "dead"
				else "LOOP_LINEAR"],
			clip.loop_mode == (Animation.LOOP_NONE if name == "dead"
				else Animation.LOOP_LINEAR), str(clip.loop_mode))

	_check("a RESET clip exists", ap.has_animation("RESET"))

	scene.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	quit(0 if _failures == 0 else 1)
