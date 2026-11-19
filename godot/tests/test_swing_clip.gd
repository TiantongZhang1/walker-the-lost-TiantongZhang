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

## r2. The blade is drawn at frame 2 and sheathed at frame 13, so the long
## return to rest is travelled unwatched. CHANGE-BRIEF.md revision 7.0.2.
const F_DRAWN := 2            # 0.0667 s
const F_COCK := 4             # 0.1333 s
const F_SHEATHED := 13        # 0.4333 s
const REST_DEG := -150.0

## r3. The hilt travels. These come from a COLUMN PROFILE of sheet cell 6,
## printed by `tools/check_sword_reach.py`, which asserts these two values
## against the committed sheet on every run. The dense mass runs +3..+13,
## so **x = +3 is the torso's BACK EDGE** -- and x = +3 is where the pivot
## sat for r1 and r2. The ink BOUNDING BOX starts at x = -11, but that is
## the scarf streaming out behind; trusting it is what made +3 look
## central on paper while it sat on the character's back in the game.
## The Blade sprite is 3 x 20 with offset (0, -10), so the hilt sits ON the
## pivot and the tip is BLADE_PX away along the arm's local -Y. 16 first; the
## author played r3 and asked for a longer blade. tools/make_sprites.py's
## SWORD_LEN is the source and check_sword_reach.py asserts they agree.
const BLADE_PX := 20.0
const TORSO_BACK := 3.0
const TORSO_FRONT := 13.0
const REST_POS := Vector2(0, 2)
const COCK_POS := Vector2(3, -5)
const STRIKE_POS := Vector2(13, 1)

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


## Where the blade's TIP is at time t, in rig coordinates. The hilt sits on
## the pivot (the sprite's offset puts it there), so the tip is BLADE_PX away
## along the arm's local -Y, with 0 degrees pointing up.
func _tip(clip: Animation, arm: int, pos: int, t: float) -> Vector2:
	var d := deg_to_rad(float(clip.value_track_interpolate(arm, t)))
	var o: Vector2 = clip.value_track_interpolate(pos, t)
	return o + Vector2(sin(d), -cos(d)) * BLADE_PX


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
	_check("swing has eight tracks", sw.get_track_count() == 8,
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

	# --- the blade: put back in r1, re-aimed in r2 ------------------------
	# r1 restored it (the poses carry no sword). r2 changed WHERE IT GOES,
	# because the author played r1 and reported a sword spinning above the
	# body rather than swinging out. The numbers said the same thing:
	# 20 -> -80 -> +85 -> +20 reverses direction TWICE about a pivot 2 px
	# above the waist, 330 degrees of travel in 0.6 s, tip never below
	# y = -3. "Spinning" was the correct word for those keys.
	#
	# The two rules r2 ships are asserted below, and either one of them
	# would have failed r1 HEADLESSLY -- which is the point. The defect was
	# visible in the key table all along; no test was asking.
	for path in ["Rig/SwordArm", "Rig/SwordArm/Blade"]:
		_check("the rig has %s" % path,
			scene.get_node_or_null(NodePath(path)) != null)
	var arm := _track(sw, "Rig/SwordArm:rotation_degrees")
	_check("there is a SwordArm:rotation_degrees track", arm >= 0)
	var blade := _track(sw, "Rig/SwordArm/Blade:visible")
	_check("there is a Blade:visible track", blade >= 0)
	if arm >= 0:
		_check("the arm track INTERPOLATES (a discrete arc would teleport)",
			sw.value_track_get_update_mode(arm) == Animation.UPDATE_CONTINUOUS,
			str(sw.value_track_get_update_mode(arm)))
		_key_at(sw, arm, 0, REST_DEG)
		_key_at(sw, arm, F_COCK, -60.0)
		_key_at(sw, arm, F_ACTIVE_OPENS, -50.0)
		_key_at(sw, arm, F_ACTIVE_CLOSES, 100.0)
		_key_at(sw, arm, F_SETTLE, 115.0)
		_key_at(sw, arm, F_SHEATHED, 118.0)
		_key_at(sw, arm, F_END, REST_DEG)
		_check("the arc ends where it began, so a second swing starts from "
			+ "rest",
			is_equal_approx(sw.track_get_key_value(arm, 0),
				sw.track_get_key_value(arm,
					sw.track_get_key_count(arm) - 1)))

		# RULE 1 -- while the blade is VISIBLE the arc travels one way.
		var vis_a := _at(F_DRAWN)
		var vis_b := _at(F_SHEATHED)
		var legs := ""
		var reversals := 0
		var prev := 0
		for k in sw.track_get_key_count(arm) - 1:
			var t0 := sw.track_get_key_time(arm, k)
			var t1 := sw.track_get_key_time(arm, k + 1)
			if t1 <= vis_a + _tol or t0 >= vis_b - _tol:
				continue        # this leg is travelled sheathed
			var d: float = (float(sw.track_get_key_value(arm, k + 1))
				- float(sw.track_get_key_value(arm, k)))
			if is_zero_approx(d):
				continue
			legs += "%+.0f " % d
			var s := 1 if d > 0.0 else -1
			if prev != 0 and s != prev:
				reversals += 1
			prev = s
		_check("the VISIBLE arc never reverses direction (r1 reversed twice "
			+ "and read as a sword spinning overhead)", reversals == 0,
			"legs: " + legs)

		# RULE 2 -- it finishes BELOW the hand. 0 deg is straight up, so
		# anything inside +/-90 leaves the blade in the top half of the
		# frame, which is where r1 lived for all 18 frames.
		var last_vis: float = sw.value_track_interpolate(arm, vis_b)
		_check("the last visible angle is past horizontal, so the blade "
			+ "finishes BELOW the hand", absf(last_vis) > 90.0,
			"%.1f deg" % last_vis)
	# RULE 3 (r3) -- the hilt is not nailed to the character's back.
	# r2 got the direction of the arc right and left the pivot at x = +3,
	# which a column profile of sheet cell 6 says is the torso's BACK EDGE.
	# A blade rotating about a fixed point inside the silhouette is a clock
	# hand whichever way it turns. The author saw that before any test did,
	# twice running, and named the fix: the centre belongs in front.
	var pos := _track(sw, "Rig/SwordArm:position")
	_check("there is a SwordArm:position track — the hand TRAVELS", pos >= 0)
	if pos >= 0:
		_check("the position track INTERPOLATES",
			sw.value_track_get_update_mode(pos) == Animation.UPDATE_CONTINUOUS,
			str(sw.value_track_get_update_mode(pos)))
		_key_at(sw, pos, 0, REST_POS)
		_key_at(sw, pos, F_ACTIVE_OPENS, COCK_POS)
		_key_at(sw, pos, F_ACTIVE_CLOSES, STRIKE_POS)
		_key_at(sw, pos, F_END, REST_POS)
		var cock: Vector2 = sw.value_track_interpolate(pos, _at(F_ACTIVE_OPENS))
		var hit: Vector2 = sw.value_track_interpolate(pos, _at(F_ACTIVE_CLOSES))
		_check("the hilt is BEHIND the torso's back edge at full cock",
			cock.x <= TORSO_BACK, "x %.0f, back edge %.0f" % [cock.x, TORSO_BACK])
		_check("the hilt is OUT IN FRONT on the last active frame",
			hit.x > TORSO_BACK + 4.0,
			"x %.0f, torso %.0f..%.0f" % [hit.x, TORSO_BACK, TORSO_FRONT])
		_check("the hilt travels forward through the active window, so the "
			+ "blade is SWUNG and not SPUN", hit.x - cock.x >= 8.0,
			"%.0f px" % (hit.x - cock.x))
		if arm >= 0:
			var t0 := _tip(sw, arm, pos, _at(F_ACTIVE_OPENS))
			var t1 := _tip(sw, arm, pos, _at(F_ACTIVE_CLOSES))
			_check("the tip sweeps further than the figure is wide during the "
				+ "active window",
				absf(t1.x - t0.x) > TORSO_FRONT - TORSO_BACK,
				"%.0f px across a %.0f px figure"
					% [absf(t1.x - t0.x), TORSO_FRONT - TORSO_BACK])
			_check("the tip finishes CLEAR of the torso, not inside it",
				t1.x > TORSO_FRONT, "tip x %.1f, front edge %.0f"
					% [t1.x, TORSO_FRONT])

	if blade >= 0:
		_check("Blade:visible is discrete",
			sw.value_track_get_update_mode(blade) == Animation.UPDATE_DISCRETE)
		_key_at(sw, blade, 0, false)
		_key_at(sw, blade, F_DRAWN, true)
		_key_at(sw, blade, F_SHEATHED, false)
		_note("the blade is visible for frames 2..13 of 18; the 268-degree "
			+ "return to rest is travelled sheathed")

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
