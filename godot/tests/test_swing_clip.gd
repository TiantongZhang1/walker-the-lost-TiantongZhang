extends SceneTree
## Assignment 7 — the read-back for the rig clip, `swing`.
##
##   ./scripts/run-test.sh test_swing_clip.gd 60
##
## `CHANGE-BRIEF.md` §6 is the phase table; these are the assertions that the
## keys came from it. One assertion per phase boundary, by name, so a failure
## says which phase moved.
##
## It proves the clip is **structured** as the table says. It cannot prove the
## swing feels committed, and it cannot see the blade at all: a headless run
## advances the clip and draws nothing. The strip and the author's verdict in
## play are §9's HUMAN rows.

const PLAYER := "res://features/player/player.tscn"
const Clips := preload("res://tests/test_player_clips.gd")

## CHANGE-BRIEF.md §6, in frames at 30 fps.
const FPS := 30.0
const LENGTH := 0.6
const F_ACTIVE_OPENS := 6      # 0.200 s
const F_ACTIVE_CLOSES := 10    # 0.333 s
const F_END := 18              # 0.600 s
const CELL_BRACED := 10
const CELL_IDLE := 6

var _checks := 0
var _failures := 0
var _tol := 0.5 / FPS


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


func _note(label: String) -> void:
	print("NOTE  ", label)


func _track(clip: Animation, path: String) -> int:
	for t in clip.get_track_count():
		if clip.track_get_path(t) == NodePath(path):
			return t
	return -1


## Frame -> seconds, through the table's own frame rate.
func _at(frame: int) -> float:
	return float(frame) / FPS


## Assert a key exists at a phase boundary, with the value the table gives.
func _key_at(clip: Animation, t: int, frame: int, want) -> void:
	var target := _at(frame)
	var found := -1
	for k in clip.track_get_key_count(t):
		if absf(clip.track_get_key_time(t, k) - target) < _tol:
			found = k
			break
	var path := str(clip.track_get_path(t))
	_check("%s has a key on frame %d (%.4f s)" % [path, frame, target],
		found >= 0, "keys at " + str(_times(clip, t)))
	if found < 0:
		return
	var got = clip.track_get_key_value(t, found)
	_check("%s on frame %d is %s" % [path, frame, str(want)],
		typeof(got) == typeof(want) and is_same(got, want)
			or (got is float and want is float
				and absf(got - want) < 0.001),
		str(got))


func _times(clip: Animation, t: int) -> Array:
	var out: Array = []
	for k in clip.track_get_key_count(t):
		out.append("%.4f" % clip.track_get_key_time(t, k))
	return out


func _init() -> void:
	await process_frame
	var scene: Node = load(PLAYER).instantiate()
	root.add_child(scene)
	await process_frame

	var ap: AnimationPlayer = scene.get_node(^"AnimationPlayer")
	var sprite: Sprite2D = scene.get_node(^"Sprite2D")
	var cells := sprite.hframes * sprite.vframes

	# --- the rig exists and is shaped the way the clip assumes ------------
	for path in ["SwordArm", "SwordArm/Blade", "SwordArm/Hitbox",
			"SwordArm/Hitbox/CollisionShape2D"]:
		_check("the rig has %s" % path,
			scene.get_node_or_null(NodePath(path)) != null)
	var hitbox: Area2D = scene.get_node(^"SwordArm/Hitbox")
	_check("the hitbox is on layer 6, PlayerAttack",
		hitbox.collision_layer == 32, "layer bits %d" % hitbox.collision_layer)
	_check("it masks layer 3, Enemy", hitbox.collision_mask == 4,
		"mask bits %d" % hitbox.collision_mask)
	_check("it starts NOT monitoring", not hitbox.monitoring)
	_note("this room has no enemy, so the window opens on nothing. "
		+ "CHANGE-BRIEF.md section 11 says so rather than hiding it.")

	# --- every track resolves, branched on track type ---------------------
	var problems := Clips.track_problems(ap)
	_check("every track in every clip resolves", problems.is_empty(),
		"; ".join(problems))

	# --- the clip's own shape ---------------------------------------------
	_check("swing exists", ap.has_animation("swing"))
	var sw := ap.get_animation("swing")
	_check("swing does NOT loop (LOOP_NONE)",
		sw.loop_mode == Animation.LOOP_NONE, str(sw.loop_mode))
	_check("swing length is %.3f s, frame %d at %d fps"
			% [LENGTH, F_END, FPS],
		absf(sw.length - LENGTH) < _tol, "%.6f" % sw.length)
	_check("swing step is one frame period at %d fps" % FPS,
		is_equal_approx(sw.step, 1.0 / FPS), "%.7f" % sw.step)
	_check("swing has four tracks", sw.get_track_count() == 4,
		str(sw.get_track_count()))

	# --- the rotation track, key by key, against the table ----------------
	var rot := _track(sw, "SwordArm:rotation_degrees")
	_check("there is a SwordArm:rotation_degrees track", rot >= 0)
	if rot >= 0:
		_key_at(sw, rot, 0, 20.0)
		_key_at(sw, rot, F_ACTIVE_OPENS, -80.0)
		_key_at(sw, rot, F_ACTIVE_CLOSES, 85.0)
		_key_at(sw, rot, 12, 75.0)
		_key_at(sw, rot, F_END, 20.0)
		_check("the rotation track interpolates (it is not discrete)",
			sw.value_track_get_update_mode(rot) == Animation.UPDATE_CONTINUOUS,
			str(sw.value_track_get_update_mode(rot)))
		_check("rest and end agree, so a second swing starts where the first "
			+ "left off",
			is_equal_approx(sw.track_get_key_value(rot, 0),
				sw.track_get_key_value(rot, sw.track_get_key_count(rot) - 1)))

	# --- THE gameplay fact: the active window -----------------------------
	var mon := _track(sw, "SwordArm/Hitbox:monitoring")
	_check("there is a Hitbox:monitoring track", mon >= 0)
	if mon >= 0:
		_check("monitoring is UPDATE_DISCRETE — there is nothing between "
			+ "true and false",
			sw.value_track_get_update_mode(mon) == Animation.UPDATE_DISCRETE,
			str(sw.value_track_get_update_mode(mon)))
		_key_at(sw, mon, 0, false)
		_key_at(sw, mon, F_ACTIVE_OPENS, true)
		_key_at(sw, mon, F_ACTIVE_CLOSES, false)
		_check("the active window is %d frames, %.4f s"
				% [F_ACTIVE_CLOSES - F_ACTIVE_OPENS,
					_at(F_ACTIVE_CLOSES) - _at(F_ACTIVE_OPENS)],
			sw.track_get_key_count(mon) == 3, str(sw.track_get_key_count(mon)))
		_note("0.1333 s against the trap's FIRE_SECONDS of 0.18 — narrower "
			+ "on purpose, so the player cannot trade with a trap")

	# --- the blade, and the body cell under it ----------------------------
	var vis := _track(sw, "SwordArm/Blade:visible")
	_check("there is a Blade:visible track", vis >= 0)
	if vis >= 0:
		_check("visible is discrete",
			sw.value_track_get_update_mode(vis) == Animation.UPDATE_DISCRETE)
		_key_at(sw, vis, 0, true)
		_key_at(sw, vis, F_END, false)

	var fr := _track(sw, "Sprite2D:frame")
	_check("there is a Sprite2D:frame track", fr >= 0)
	if fr >= 0:
		_check("the body's frame track is discrete",
			sw.value_track_get_update_mode(fr) == Animation.UPDATE_DISCRETE)
		_key_at(sw, fr, 0, CELL_BRACED)
		_key_at(sw, fr, F_END, CELL_IDLE)
		var in_sheet := true
		for k in sw.track_get_key_count(fr):
			if int(sw.track_get_key_value(fr, k)) >= cells:
				in_sheet = false
		_check("every frame key is inside the sheet (< %d)" % cells, in_sheet)

	# --- RESET holds the sword's default pose -----------------------------
	var reset := ap.get_animation("RESET")
	for path in ["SwordArm:rotation_degrees", "SwordArm/Blade:visible",
			"SwordArm/Hitbox:monitoring"]:
		_check("RESET holds %s" % path, _track(reset, path) >= 0)
	var rr := _track(reset, "SwordArm/Hitbox:monitoring")
	if rr >= 0:
		_check("RESET leaves the hitbox off",
			sw.track_get_key_count(rr) >= 0
				and reset.track_get_key_value(rr, 0) == false)

	scene.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("Structure only. Whether the swing reads as committed is the strip")
	print("and the author's verdict in play — CHANGE-BRIEF.md section 9.")
	quit(0 if _failures == 0 else 1)
