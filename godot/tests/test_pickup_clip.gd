extends SceneTree
## Assignment 8's FIRST animation-set item, read back out of the scene.
##
##   ./scripts/run-test.sh test_pickup_clip.gd 60
##
## The assignment's item 1 is **"movement with no rig and no frames: a
## pickup, door, platform or UI element ... an AnimationPlayer clip keying
## position, rotation or scale"**. Three of those words carry the weight and
## each gets an assertion here:
##
##   **no frames** -- no track names `frame`, `frames`, `sprite_frames`,
##                    `animation` or `hframes`, and the sprite's hframes and
##                    vframes are both 1. A sheet cell is not a simple
##                    animation.
##   **no rig**    -- exactly ONE node is animated, and it has no animated
##                    ancestor or descendant. A pivot carrying a child is a
##                    rig, however small.
##   **position,   -- every track's subname is one of those three. A clip
##   rotation or      that modulated a colour or faded an alpha would be an
##   scale**          effect, not movement.
##
## Plus the cycle rule, which the assignment applies to item 3 and which this
## clip also obeys: `loop_mode` is linear and the value at t = 0 equals the
## value at t = length. **The rotation seam is compared modulo 360**, because
## 0 and 360 are the same POSE and different numbers, and a seam check that
## could not say so would force the clip to end where it started and never
## turn at all.
##
## A headless run advances this clip and reads its structure. It says nothing
## about whether a floating key reads as a floating key.

const MAIN := "res://game/main.tscn"
const KEY_PATH := ^"FloatingKey"
const CLIP := "hover"

## The three subnames the assignment allows for a simple animation.
const MOVEMENT := ["position", "rotation", "rotation_degrees", "scale"]
## Anything whose presence would make this a sheet rather than a movement.
const FRAMEY := ["frame", "frames", "sprite_frames", "animation", "hframes",
	"vframes", "texture"]

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


func _init() -> void:
	await process_frame
	var main: Node = (load(MAIN) as PackedScene).instantiate()
	root.add_child(main)
	await process_frame

	var key: Node2D = main.get_node_or_null(KEY_PATH)
	_check("the room instances FloatingKey", key != null)
	if key == null:
		_finish()
		return

	var ap: AnimationPlayer = key.get_node_or_null(^"KeyAnim")
	_check("it carries its own AnimationPlayer, KeyAnim", ap != null)
	if ap == null:
		_finish()
		return

	_check("which has a `%s` clip" % CLIP, ap.has_animation(CLIP))
	_check("and a RESET clip holding the default pose",
		ap.has_animation("RESET"))
	if not ap.has_animation(CLIP):
		_finish()
		return
	var clip := ap.get_animation(CLIP)

	# --- it plays without being told to -----------------------------------
	_check("it autoplays: nothing in the game has to start it",
		ap.autoplay == CLIP, ap.autoplay)
	_check("on the PHYSICS tick, like everything else animated here",
		ap.callback_mode_process
			== AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS,
		"callback_mode_process = %d" % ap.callback_mode_process)
	_note("physics is not required for a decorative loop -- nothing reads it."
		+ " It is set so that this project has ONE answer to 'which tick does"
		+ " an animation advance on', which is the question A7 measured")

	# --- NO FRAMES ---------------------------------------------------------
	var framey: Array[String] = []
	for t in clip.get_track_count():
		var sub := clip.track_get_path(t).get_concatenated_subnames()
		if FRAMEY.has(String(sub)):
			framey.append(String(sub))
	_check("NO FRAMES: no track names a frame, a sheet or a texture",
		framey.is_empty(), ", ".join(framey))
	var spr: Sprite2D = key.get_node_or_null(^"Sprite2D")
	_check("the sprite is a plain Sprite2D, not an AnimatedSprite2D",
		spr != null)
	if spr != null:
		_check("with hframes = vframes = 1: it is one picture",
			spr.hframes == 1 and spr.vframes == 1,
			"%d x %d" % [spr.hframes, spr.vframes])

	# --- NO RIG ------------------------------------------------------------
	var animated := {}
	for t in clip.get_track_count():
		animated[clip.track_get_path(t).get_concatenated_names()] = true
	_check("NO RIG: exactly one node is animated",
		animated.size() == 1, ", ".join(animated.keys()))
	# A rig is a chain: a pivot whose child inherits its transform. One node
	# with no animated relative cannot be one, and that is cheaper to assert
	# than to describe.
	var nested := false
	for a in animated:
		for b in animated:
			if a != b and String(b).begins_with(String(a) + "/"):
				nested = true
	_check("and no animated node is inside another: no pivot chain",
		not nested)

	# --- POSITION, ROTATION OR SCALE ---------------------------------------
	var other: Array[String] = []
	for t in clip.get_track_count():
		var sub := String(clip.track_get_path(t).get_concatenated_subnames())
		var head := sub.split(":")[0]
		if not MOVEMENT.has(head):
			other.append(sub)
	_check("every track keys position, rotation or scale -- nothing else",
		other.is_empty(), ", ".join(other))
	_note("tracks: " + ", ".join(animated.keys()) + " -> "
		+ str(clip.get_track_count()) + " track(s)")

	# --- the cycle rule ----------------------------------------------------
	_check("loop_mode is LOOP_LINEAR",
		clip.loop_mode == Animation.LOOP_LINEAR,
		"loop_mode = %d" % clip.loop_mode)
	_check("length is 2.400 s", absf(clip.length - 2.4) < 0.0005,
		"%.4f" % clip.length)

	for t in clip.get_track_count():
		var path := String(clip.track_get_path(t))
		var n := clip.track_get_key_count(t)
		if n < 2:
			_check("%s has at least two keys to have a seam" % path, false,
				"%d key(s)" % n)
			continue
		var t0 := clip.track_get_key_time(t, 0)
		var tn := clip.track_get_key_time(t, n - 1)
		_check("%s's first key is at 0 and its last at `length`" % path,
			absf(t0) < 0.0005 and absf(tn - clip.length) < 0.0005,
			"%.4f .. %.4f against length %.4f" % [t0, tn, clip.length])
		var v0 = clip.track_get_key_value(t, 0)
		var vn = clip.track_get_key_value(t, n - 1)
		if path.ends_with("rotation_degrees"):
			# **Modulo 360.** 0 and 360 are one pose and two numbers, and a
			# key that turns the whole way round is the only way a single
			# sprite can rotate continuously across a loop.
			var d: float = fposmod(float(vn) - float(v0), 360.0)
			_check("%s's seam closes MODULO 360 (a full turn)" % path,
				d < 0.0005 or absf(d - 360.0) < 0.0005,
				"%.1f -> %.1f, difference %.4f deg" % [float(v0), float(vn), d])
			_check("and it actually turns, so the seam is not trivial",
				absf(float(vn) - float(v0)) > 1.0,
				"%.1f deg of travel" % absf(float(vn) - float(v0)))
		else:
			_check("%s's seam closes: t=0 equals t=length" % path,
				is_equal_approx(float(v0), float(vn)),
				"%.4f -> %.4f" % [float(v0), float(vn)])
			var span := 0.0
			for k in n:
				span = maxf(span, absf(float(clip.track_get_key_value(t, k))
					- float(v0)))
			_check("and it actually moves, so the seam is not trivial",
				span > 0.5, "%.2f px of travel" % span)

	main.queue_free()
	await process_frame
	_finish()


func _finish() -> void:
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("Structure only. Whether a floating key READS as a floating key is")
	print("the author's, in play -- CHANGE-BRIEF.md section 9.")
	quit(0 if _failures == 0 else 1)
