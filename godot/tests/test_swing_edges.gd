extends SceneTree
## Assignment 7, Step 6 — the committing action at every phase boundary, and
## an interrupt inside every phase.
##
##   ./scripts/run-test.sh test_swing_edges.gd 60
##
## **Run at 60**, which is this project's physics tick. The clip is authored
## at 30 fps and the lock is read every physics frame, so one table frame is
## two physics frames and the boundaries land on even numbers. A frame count
## is only meaningful at a pinned rate.
##
## Two halves:
##
## **The window.** One clean swing is run and every physics frame of it is
## recorded — the playhead, `Hitbox.monitoring`, the lock, the player's x.
## The boundaries are then asserted against that trace rather than against a
## press timed by hand, which is the difference between measuring the clip
## and measuring the test's own reflexes.
##
## **The interrupts.** `CHANGE-BRIEF.md` §7's table says a second attack is
## IGNORED in startup and active and BUFFERED in recovery. Each case is a
## fresh swing with the key pressed on one named frame: one before each
## boundary, on it, and one after.
##
## A headless run draws nothing. Nothing here says the swing looks committed.

const MAIN := "res://game/main.tscn"
const PHYS := 60.0

## CHANGE-BRIEF.md §6 in seconds, and the physics frame each lands on.
const T_ACTIVE_OPEN := 0.2
const T_ACTIVE_CLOSE := 0.3333333
const T_END := 0.6
const F_ACTIVE_OPEN := 12       # 0.200 s * 60
const F_ACTIVE_CLOSE := 20      # 0.3333 s * 60, rounded to the physics grid
const F_END := 36               # 0.600 s * 60

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


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()


func _tap(code: Key) -> void:
	_key(code, true)
	await process_frame
	_key(code, false)


## Start one swing from a settled, idle player and record the clip's clock
## for `F_END` physics frames. `jump_on >= 0` presses SPACE on that frame of
## the swing; `-1` is the baseline.
##
## Each row is `[playhead, monitoring, locked, clip, on_floor, velocity.y]`.
## The first four are the swing's own state and must not depend on the jump;
## the last two are the jump's, and must.
func _swing_trace(player: Player, ap: AnimationPlayer, hitbox: Area2D,
		jump_on: int) -> Array:
	var rows: Array = []
	_key(KEY_J, true)
	await process_frame
	_key(KEY_J, false)
	for fr in range(F_END):
		if jump_on >= 0:
			if fr == jump_on:
				_key(KEY_SPACE, true)
			elif fr == jump_on + 1:
				_key(KEY_SPACE, false)
		rows.append([ap.current_animation_position, hitbox.monitoring,
			player.is_locked(), String(ap.current_animation),
			player.is_on_floor(), player.velocity.y])
		await process_frame
	if jump_on >= 0:
		_key(KEY_SPACE, false)
	return rows


## Drop the player onto the floor and leave it idle.
func _settle(player: Player) -> void:
	var n := 0
	while (not player.is_on_floor() or player.is_locked()) and n < 200:
		await process_frame
		n += 1
	for i in range(4):
		await process_frame


func _init() -> void:
	await process_frame
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame
	var player: Player = main.get_node(^"Player")
	var ap: AnimationPlayer = player.get_node(^"AnimationPlayer")
	var hitbox: Area2D = player.get_node(^"Hitbox")
	# Revision 7.0.6 checks the FACING, which is Rig.scale.x: the one
	# thing a swing still commits you to.
	var rig: Node2D = player.get_node(^"Rig")
	await _settle(player)

	# ----------------------------------------------------------------- A
	# One clean swing, recorded frame by frame.
	var x0 := player.global_position.x
	_key(KEY_J, true)
	await process_frame
	_key(KEY_J, false)

	var trace: Array = []          # [frame, playhead, monitoring, locked, x]
	var f := 0
	while f < 50:
		trace.append([f, ap.current_animation_position, hitbox.monitoring,
			player.is_locked(), player.global_position.x])
		await process_frame
		f += 1

	_check("the hitbox is OFF on frame 0", not trace[0][2])
	var opened := -1
	var closed := -1
	for row in trace:
		if row[2] and opened < 0:
			opened = row[0]
		if opened >= 0 and not row[2] and closed < 0 and row[0] > opened:
			closed = row[0]
	_check("the hitbox opens on physics frame %d (%.4f s)"
			% [F_ACTIVE_OPEN, T_ACTIVE_OPEN],
		opened == F_ACTIVE_OPEN, "opened on %d" % opened)
	_check("the hitbox closes on physics frame %d (%.4f s)"
			% [F_ACTIVE_CLOSE, T_ACTIVE_CLOSE],
		closed == F_ACTIVE_CLOSE, "closed on %d" % closed)
	_check("the active window is %d physics frames, %.4f s"
			% [F_ACTIVE_CLOSE - F_ACTIVE_OPEN,
				(F_ACTIVE_CLOSE - F_ACTIVE_OPEN) / PHYS],
		closed - opened == F_ACTIVE_CLOSE - F_ACTIVE_OPEN,
		"%d frames" % (closed - opened))

	# One frame before, on, and one after each boundary.
	for b in [[F_ACTIVE_OPEN, "the active window opens"],
			[F_ACTIVE_CLOSE, "the active window closes"]]:
		var fr: int = b[0]
		var what: String = b[1]
		var want_open := fr == F_ACTIVE_OPEN
		_check("one frame BEFORE %s, monitoring is %s"
				% [what, str(not want_open)],
			trace[fr - 1][2] == (not want_open), str(trace[fr - 1][2]))
		_check("ON the frame %s, monitoring is %s" % [what, str(want_open)],
			trace[fr][2] == want_open, str(trace[fr][2]))
		_check("one frame AFTER %s, monitoring is %s"
				% [what, str(want_open)],
			trace[fr + 1][2] == want_open, str(trace[fr + 1][2]))

	var unlocked := -1
	for row in trace:
		if not row[3] and unlocked < 0 and row[0] > 0:
			unlocked = row[0]
	_check("the lock releases on physics frame %d (%.3f s)"
			% [F_END, T_END],
		unlocked == F_END, "released on %d (%.4f s)" % [unlocked, unlocked / PHYS])
	_check("one frame BEFORE the end, still locked", trace[F_END - 1][3])
	_check("ON the end frame, no longer locked", not trace[F_END][3])

	var moved := 0.0
	for row in trace:
		if row[3]:
			moved = maxf(moved, absf(row[4] - x0))
	# Revision 7.0.6 reworded this rather than deleting it. A swing no
	# longer locks movement, so "0 px" is no longer a statement about the
	# LOCK -- it is a statement about DRIFT. No direction key is held
	# anywhere in section A, so the player must stay exactly where it was;
	# anything else would be the clip or the plant moving it on its own.
	# Section D is where a key IS held.
	_check("with no direction held, the swing moves the player 0 px",
		is_equal_approx(moved, 0.0), "max drift %.4f px" % moved)
	_note("the hitbox masks layer 3, Enemy. This room has none, so the "
		+ "window opens on nothing — CHANGE-BRIEF.md §11 says so")

	# ----------------------------------------------------------------- B
	# An interrupt in each phase: one frame before each boundary, on it, and
	# one after. CHANGE-BRIEF.md §7: ignored in startup and active, buffered
	# in recovery.
	var cases := [
		[0, "startup, on the first frame", 1],
		[F_ACTIVE_OPEN - 1, "startup, one frame before active", 1],
		[F_ACTIVE_OPEN, "active, on the frame it opens", 1],
		[F_ACTIVE_OPEN + 1, "active, one frame after it opens", 1],
		[F_ACTIVE_CLOSE - 1, "active, one frame before it closes", 1],
		[F_ACTIVE_CLOSE, "recovery, on its first frame", 2],
		[F_ACTIVE_CLOSE + 1, "recovery, one frame in", 2],
		[F_END - 1, "recovery, one frame before the end", 2],
		[F_END + 1, "after the end — a fresh swing, not a buffer", 2],
	]
	for case in cases:
		var press_on: int = case[0]
		var label: String = case[1]
		var want: int = case[2]
		await _settle(player)
		var base := player.swing_count
		_key(KEY_J, true)
		await process_frame
		_key(KEY_J, false)
		for i in range(F_END + 60):
			if i == press_on:
				await _tap(KEY_J)
			else:
				await process_frame
		var got := player.swing_count - base
		_check("attack pressed on frame %d (%s) -> %d swing(s)"
				% [press_on, label, want],
			got == want, "got %d" % got)

	# ----------------------------------------------------------------- C
	# THE SWING IN THE AIR. Revision 7.0.5. The author asked for it, and
	# until then `player.gd` gated the attack on `is_on_floor()` -- a gate
	# NO TEST IN THIS REPOSITORY EVER ASSERTED. It could have been deleted
	# by accident at any point in A7 and every suite would have stayed
	# green. Both sides of the new rule are asserted here.
	#
	# The rule: a commitment locks out INPUT, not physics. On the ground the
	# swing plants (x velocity held at 0). In the air the jump's horizontal
	# velocity is carried, because there is nothing to plant against, and no
	# key can change it.
	await _settle(player)
	var base_air := player.swing_count
	await _tap(KEY_D)                       # face and move right
	_key(KEY_D, true)
	for i in range(10):
		await process_frame
	var vx_before: float = player.velocity.x
	_key(KEY_SPACE, true)
	await process_frame
	_key(KEY_SPACE, false)
	for i in range(6):                      # get clear of the floor
		await process_frame
	_key(KEY_D, false)

	_check("the test is airborne before it swings", not player.is_on_floor(),
		"on_floor=%s y=%.1f" % [player.is_on_floor(), player.velocity.y])
	var vx_air: float = player.velocity.x
	await _tap(KEY_J)
	await process_frame

	_check("attack in the AIR starts a swing",
		player.swing_count - base_air == 1,
		"swing_count +%d" % (player.swing_count - base_air))
	_check("the lock is on in the air", player.is_locked())
	_check("`swing` beats `rising`/`falling` -- is_locked() outranks the "
		+ "airborne branch in player_anim.gd",
		ap.current_animation == "swing", str(ap.current_animation))

	# Revision 7.0.6: steering is NOT locked out any more, in the air or on
	# the ground. r5 asserted the opposite one revision ago and the author
	# changed the design the next day; the assertion is inverted rather than
	# deleted, so the file still says what the rule is.
	#
	# **What is still locked is the FACING.** `player_anim.gd` only updates
	# `_facing` when `not is_locked()`, so holding the opposite direction
	# walks the character backwards without flipping `Rig.scale.x` -- and
	# `Rig.scale.x` is what mirrors the whole sword arm. Turning mid-arc
	# would teleport the blade across the body in one frame.
	var face_before: float = rig.scale.x
	_key(KEY_A, true)                       # hold the OPPOSITE direction
	var steered := false
	var flipped := false
	var fell := false
	var vy_rose := false
	var prev_vy: float = player.velocity.y
	for i in range(10):
		await process_frame
		if player.is_on_floor():
			break
		if player.velocity.x < -1.0:
			steered = true
		if not is_equal_approx(rig.scale.x, face_before):
			flipped = true
		if player.velocity.y > prev_vy:
			vy_rose = true
		prev_vy = player.velocity.y
		fell = true
	_key(KEY_A, false)
	_check("steering WORKS during an air swing (revision 7.0.6)", steered,
		"vx on entry was %.1f" % vx_air)
	_check("but the FACING does not flip, so the blade does not teleport "
		+ "across the body mid-arc", not flipped,
		"Rig.scale.x %.1f -> %.1f" % [face_before, rig.scale.x])
	_check("gravity still runs during an air swing", fell and vy_rose)
	_check("it entered the swing moving, so none of this is trivially true",
		absf(vx_air) > 1.0, "vx %.1f (walking was %.1f)" % [vx_air, vx_before])

	# **Revision 7.0.10: this assertion survives, and its REASON changed.**
	# Jump is still refused here -- but not because the swing forbids it any
	# more. `player.gd` reads jump on every tick now, locked or not, and the
	# only gate left is `is_on_floor()`. The player is in the air, so there
	# is nothing to jump from, exactly as in any other airborne frame of
	# this game: there is no double jump.
	#
	# An assertion that passes for a new reason is worth more than a deleted
	# one, but only if the reason is written down. Section E is the half that
	# would NOT have passed before.
	var y_before: float = player.velocity.y
	_check("the test is still off the floor, so this is the no-double-jump "
		+ "rule and not the lock", not player.is_on_floor())
	await _tap(KEY_SPACE)
	_check("jump does nothing during an AIR swing -- no double jump",
		player.velocity.y >= y_before, "%.1f -> %.1f"
			% [y_before, player.velocity.y])

	var n := 0
	while player.is_locked() and n < 120:
		await process_frame
		n += 1
	_check("the air swing ends on its own", not player.is_locked(),
		"%d physics frames" % n)

	# ----------------------------------------------------------------- D
	# MOVING THROUGH A GROUND SWING. Revision 7.0.6, and the inverse of what
	# section A used to assert about the lock.
	await _settle(player)
	var face0: float = rig.scale.x
	var gx0: float = player.global_position.x
	_key(KEY_D, true)
	for i in range(10):
		await process_frame
	await _tap(KEY_J)
	await process_frame
	_check("a ground swing does NOT plant any more: x velocity is full SPEED",
		absf(player.velocity.x) > 90.0, "%.3f" % player.velocity.x)
	var travelled := 0.0
	var flipped_ground := false
	var still_locked_at_18 := false
	var fr := 0
	while player.is_locked() and fr < 120:
		if fr == 20:                         # mid-recovery, turn around
			_key(KEY_D, false)
			_key(KEY_A, true)
		await process_frame
		fr += 1
		travelled = maxf(travelled, absf(player.global_position.x - gx0))
		# **Only while STILL LOCKED.** The first version of this check sampled
		# the facing after the `await` without re-testing the lock, so on the
		# loop's last turn the swing had already ended and `player_anim.gd` had
		# correctly flipped the facing on that same physics tick. It failed,
		# and it was the test that was wrong, not the game: a flip one frame
		# AFTER the commitment ends is the commitment ending.
		if player.is_locked() and not is_equal_approx(rig.scale.x, face0):
			flipped_ground = true
		if fr == F_END - 2:
			still_locked_at_18 = player.is_locked()
	_key(KEY_A, false)
	_check("the player TRAVELS during a ground swing", travelled > 20.0,
		"%.1f px over %d physics frames" % [travelled, fr])
	_check("reversing mid-swing does not flip the facing", not flipped_ground,
		"Rig.scale.x stayed %.1f" % face0)
	_check("and it is still committed: the clip ran to its own end, not to "
		+ "a key release", still_locked_at_18 and fr >= F_END - 2,
		"%d physics frames" % fr)
	_note("since revision 7.0.9 the legs keep their gait through a moving "
		+ "swing -- `LegAnim` owns them and never hears about the sword -- "
		+ "so this no longer slides. The note that used to be here said it "
		+ "did, and was a revision out of date")
	await _settle(player)

	# ----------------------------------------------------------------- E
	# JUMPING OUT OF A GROUND SWING. Revision 7.0.10, and the author's
	# request has two halves that are different claims:
	#
	#   "I want to jump while swinging"        -> the jump happens
	#   "without interrupting the swing"       -> the swing does not notice
	#
	# The first half is one assertion. **The second half is not assertable by
	# looking at the jump at all** -- it is a claim about what the swing's
	# clock did, so the only honest form of it is to run the SAME swing twice,
	# once with a jump through it and once without, and compare the two clocks
	# frame by frame. That is what this section does. If the playhead, the
	# hitbox window, the lock and the clip name all agree on all 36 physics
	# frames, "it did not interrupt" is a measurement rather than a feeling.
	#
	# The jump is tried in all three phases, because "does not interrupt"
	# said once about startup says nothing about recovery, where a second
	# attack IS buffered and the input path is therefore not empty.
	await _settle(player)
	var plain := await _swing_trace(player, ap, hitbox, -1)
	var plain_floor := true
	for row in plain:
		if not row[4]:
			plain_floor = false
	_check("the baseline swing never leaves the floor, so the comparison "
		+ "below is not trivially true", plain_floor)

	for case in [[4, "startup"], [14, "the active window"], [26, "recovery"]]:
		var jump_on: int = case[0]
		var phase: String = case[1]
		await _settle(player)
		var count_before := player.swing_count
		var jumped := await _swing_trace(player, ap, hitbox, jump_on)

		var left_floor := false
		var rose := false
		for i in range(jump_on + 1, F_END):
			if not jumped[i][4]:
				left_floor = true
			if jumped[i][5] < -1.0:
				rose = true
		_check("jump in %s LEAVES THE FLOOR" % phase, left_floor and rose,
			"off_floor=%s vy<0=%s" % [left_floor, rose])

		# --- and the swing's own clock is untouched, frame for frame ------
		var drift := 0.0
		var window_differs := false
		var lock_differs := false
		var clip_differs := false
		for i in range(F_END):
			drift = maxf(drift, absf(plain[i][0] - jumped[i][0]))
			if plain[i][1] != jumped[i][1]:
				window_differs = true
			if plain[i][2] != jumped[i][2]:
				lock_differs = true
			if plain[i][3] != jumped[i][3]:
				clip_differs = true
		_check("the playhead is IDENTICAL to the un-jumped swing for all "
			+ "%d frames (jump in %s)" % [F_END, phase],
			drift <= 0.0005, "worst disagreement %.6f s" % drift)
		_check("the active window opens and closes on the same frames "
			+ "(jump in %s)" % phase, not window_differs)
		_check("the lock is on for the same frames (jump in %s)" % phase,
			not lock_differs)
		_check("`swing` is still the clip while airborne -- is_locked() "
			+ "outranks rising/falling (jump in %s)" % phase,
			not clip_differs)
		_check("the jump started NO new swing (jump in %s)" % phase,
			player.swing_count - count_before == 1,
			"swing_count +%d" % (player.swing_count - count_before))

		var n2 := 0
		while player.is_locked() and n2 < 120:
			await process_frame
			n2 += 1
		_check("the jumped swing still ends on its own clock, not on the "
			+ "landing (jump in %s)" % phase, not player.is_locked() and n2 <= 2,
			"%d extra frames past frame %d" % [n2, F_END])

	_note("nothing here says the jumped swing LOOKS right. While airborne "
		+ "the legs play `legs_planted` or `legs_run`, because the swing "
		+ "torsos are legless and hiding the rig's legs would leave a "
		+ "floating torso. Whether a braced stance reads in mid-air is the "
		+ "author's call in play")
	await _settle(player)

	main.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("Boundaries and interrupts only. Whether the phases READ as")
	print("distinct is the strip and the author's verdict in play.")
	quit(0 if _failures == 0 else 1)
