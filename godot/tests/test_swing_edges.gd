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
	_check("the player moves 0 px for the whole lock",
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

	# Steering is locked out; momentum is not.
	_key(KEY_A, true)                       # hold the OPPOSITE direction
	var carried := true
	var fell := false
	var vy_rose := false
	var prev_vy: float = player.velocity.y
	for i in range(10):
		await process_frame
		if player.is_on_floor():
			break
		if not is_equal_approx(player.velocity.x, vx_air):
			carried = false
		if player.velocity.y > prev_vy:
			vy_rose = true
		prev_vy = player.velocity.y
		fell = true
	_key(KEY_A, false)
	_check("the jump's horizontal velocity is CARRIED through the air swing",
		carried, "was %.1f" % vx_air)
	_check("holding the opposite direction does not turn the swing around",
		carried)
	_check("gravity still runs during an air swing", fell and vy_rose)
	_check("it was moving, so 'carried' is not trivially true",
		absf(vx_air) > 1.0, "vx %.1f (walking was %.1f)" % [vx_air, vx_before])

	# Jump is still refused mid-swing, in the air as on the ground.
	var y_before: float = player.velocity.y
	await _tap(KEY_SPACE)
	_check("jump is still ignored during an air swing",
		player.velocity.y >= y_before, "%.1f -> %.1f"
			% [y_before, player.velocity.y])

	var n := 0
	while player.is_locked() and n < 120:
		await process_frame
		n += 1
	_check("the air swing ends on its own", not player.is_locked(),
		"%d physics frames" % n)

	# And landing plants, because the lock re-tests is_on_floor() every tick.
	await _settle(player)
	_key(KEY_D, true)
	for i in range(10):
		await process_frame
	await _tap(KEY_J)
	await process_frame
	_key(KEY_D, false)
	_check("a GROUND swing still plants: x velocity is 0",
		is_zero_approx(player.velocity.x), "%.3f" % player.velocity.x)
	await _settle(player)

	main.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("Boundaries and interrupts only. Whether the phases READ as")
	print("distinct is the strip and the author's verdict in play.")
	quit(0 if _failures == 0 else 1)
