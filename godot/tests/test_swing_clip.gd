extends SceneTree
## Assignment 7 — the read-back for the SPRITE-SHEET clip, `swing`.
##
##   ./scripts/run-test.sh test_swing_clip.gd 60
##
## The committing action, played as frames off the sheet: cell 5 (windup) for
## startup, cell 6 (live) for the active window, back through 5 and out to 1.
## Those two cells are p6-windup and p7-live, generated for walker-ninja in
## 2026-10 and never used until this assignment.
##
## `CHANGE-BRIEF.md` §6 is the phase table; these are the assertions that the
## keys came from it. One assertion per phase boundary, by name, so a failure
## says which phase moved.
##
## It proves the clip is **structured** as the table says. It cannot prove the
## swing feels committed: a headless run advances the clip and draws nothing.
## The strip and the author's verdict in play are §9's HUMAN rows.

const PLAYER := "res://features/player/player.tscn"
const Clips := preload("res://tests/test_player_clips.gd")

## CHANGE-BRIEF.md §6, in frames at 30 fps.
const FPS := 30.0
const LENGTH := 0.6
const F_ACTIVE_OPENS := 6      # 0.200 s
const F_ACTIVE_CLOSES := 10    # 0.333 s
const F_END := 18              # 0.600 s
const CELL_WINDUP := 5
const CELL_LIVE := 6
const CELL_IDLE := 1
const F_SETTLE := 12          # 0.400 s, back through the windup shape

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
	var sprite: Sprite2D = scene.get_node(^"Rig/Body")
	var cells := sprite.hframes * sprite.vframes

	# --- the hitbox the active window switches on -------------------------
	for path in ["Hitbox", "Hitbox/CollisionShape2D"]:
		_check("the scene has %s" % path,
			scene.get_node_or_null(NodePath(path)) != null)
	var hitbox: Area2D = scene.get_node(^"Hitbox")
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
	_check("swing has five tracks", sw.get_track_count() == 5,
		str(sw.get_track_count()))

	# --- the body cells, key by key, against the phase table --------------
	var fr := _track(sw, "Rig/Body:frame")
	_check("there is a Rig/Body:frame track", fr >= 0)
	if fr >= 0:
		_check("the frame track is UPDATE_DISCRETE — a sheet holds a cell, "
			+ "it does not interpolate toward the next one",
			sw.value_track_get_update_mode(fr) == Animation.UPDATE_DISCRETE,
			str(sw.value_track_get_update_mode(fr)))
		_key_at(sw, fr, 0, CELL_WINDUP)
		_key_at(sw, fr, F_ACTIVE_OPENS, CELL_LIVE)
		_key_at(sw, fr, F_SETTLE, CELL_WINDUP)
		_key_at(sw, fr, F_END, CELL_IDLE)
		var in_sheet := true
		var seen: Array = []
		for k in sw.track_get_key_count(fr):
			var v := int(sw.track_get_key_value(fr, k))
			seen.append(v)
			if v >= cells:
				in_sheet = false
		_check("every frame key is inside the sheet (< %d)" % cells, in_sheet,
			str(seen))

	# --- THE gameplay fact: the active window -----------------------------
	var mon := _track(sw, "Hitbox:monitoring")
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

	# --- the cut-out legs stay hidden: the pose cells have their own ------
	for leg in ["Rig/LegFront:visible", "Rig/LegBack:visible"]:
		var lt := _track(sw, leg)
		_check("swing hides %s" % leg,
			lt >= 0 and sw.track_get_key_value(lt, 0) == false,
			"no track" if lt < 0 else str(sw.track_get_key_value(lt, 0)))

	# --- RESET holds the default pose -------------------------------------
	var reset := ap.get_animation("RESET")
	for path in ["Rig/Body:frame", "Rig/LegFront:rotation_degrees",
			"Rig/LegBack:rotation_degrees", "Hitbox:monitoring"]:
		_check("RESET holds %s" % path, _track(reset, path) >= 0)
	var rr := _track(reset, "Hitbox:monitoring")
	if rr >= 0:
		# `rr` indexes RESET, so it must be read from RESET. An earlier
		# version of this line asked `sw` -- the swing clip -- for the key
		# count at RESET's track index. It passed while the two clips
		# happened to have compatible indices and started failing the moment
		# the scene was restructured, which is the only reason it was found.
		_check("RESET leaves the hitbox off",
			reset.track_get_key_value(rr, 0) == false,
			str(reset.track_get_key_value(rr, 0)))

	scene.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("Structure only. Whether the swing reads as committed is the strip")
	print("and the author's verdict in play — CHANGE-BRIEF.md section 9.")
	quit(0 if _failures == 0 else 1)
