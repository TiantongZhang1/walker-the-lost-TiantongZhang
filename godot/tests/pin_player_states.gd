extends SceneTree
## Assignment 7, Step 2 — what the player does now, pinned before it changes.
##
##   ./scripts/run-test.sh pin_player_states.gd 60
##
## **This pin is written to survive the change it is guarding.** It records
## what the player *does* — floor contact, the sign of each velocity
## component, health — and derives the animation state from those facts with
## the same rule the game uses. Today that rule lives in `pose_driver.gd`;
## after A7 it lives in `player.gd`'s state machine and `player_anim.gd`. A
## pin that asked either of those nodes directly would break on the refactor
## and prove nothing about behaviour, which is the opposite of its job.
##
## So the derivation is **in this file**, written once, from
## `CHANGE-BRIEF.md` §7's table. If the sequence below changes, either the
## player moves differently or the state table is wrong — and the brief
## predicted neither.
##
## **Real input only.** Every key goes through `Input.parse_input_event`, so
## the run exercises the same path a player does. `Input.action_press` never
## reaches `_input` or `_unhandled_input`, and a test built on it silently
## exercises nothing — Assignment 7 names that trap and the step-dust suite
## already learned it here.
##
## **Frame counts are only meaningful at a pinned rate.** Run it at 60, which
## is this project's physics tick (`project.godot` has no `[physics]`
## section, so the engine default stands). The frame numbers below are
## recorded, not asserted to the frame, except where the brief says a
## transition must be immediate.

const MAIN := "res://game/main.tscn"
const MOVING_EPS := 1.0

## The states of `CHANGE-BRIEF.md` §7, derived here so the pin outlives the
## node that implements them.
enum S { IDLE, RUN, AIRBORNE_RISING, AIRBORNE_FALLING, DEAD }
const NAMES := ["IDLE", "RUN", "RISING", "FALLING", "DEAD"]

var _checks := 0
var _failures := 0
var _frame := 0
var _log: Array = []          # [[frame, state], ...] transitions only
var _last := -1


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


## The rule, written once. Order matters: dead beats airborne beats moving.
func _state_of(body: CharacterBody2D) -> int:
	if body.health <= 0:
		return S.DEAD
	if not body.is_on_floor():
		return S.AIRBORNE_RISING if body.velocity.y < 0.0 else S.AIRBORNE_FALLING
	if absf(body.velocity.x) > MOVING_EPS:
		return S.RUN
	return S.IDLE


## One frame: advance, sample, and record a transition if the state moved.
func _step(body: CharacterBody2D, hold_right := false) -> int:
	if hold_right:
		_key(KEY_D, true)
	await process_frame
	_frame += 1
	var s := _state_of(body)
	if s != _last:
		_log.append([_frame, s])
		_last = s
	return s


func _run_frames(body: CharacterBody2D, n: int, hold_right := false) -> void:
	for i in range(n):
		await _step(body, hold_right)


func _sequence() -> Array[String]:
	var out: Array[String] = []
	for row in _log:
		out.append(NAMES[row[1]])
	return out


func _init() -> void:
	await process_frame
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame

	var player: CharacterBody2D = main.get_node(^"Player")
	print("Player at ", player.global_position, ", health ", player.health)

	# --- 1. the fall onto the floor, and the first IDLE -------------------
	var settle := 0
	while not player.is_on_floor() and settle < 120:
		await _step(player)
		settle += 1
	_check("lands on the floor within 120 frames", player.is_on_floor(),
		"took %d frames" % settle)
	await _run_frames(player, 5)
	_check("settles to IDLE", _state_of(player) == S.IDLE,
		NAMES[_state_of(player)])

	# --- 2. RUN, and the deceleration that is one frame long --------------
	var run_from := _frame
	await _run_frames(player, 30, true)
	_check("holding right gives RUN", _state_of(player) == S.RUN,
		"vx %.1f" % player.velocity.x)
	_check("runs at SPEED", is_equal_approx(absf(player.velocity.x), 96.0),
		"vx %.3f" % player.velocity.x)
	var x_after_run := player.global_position.x

	_key(KEY_D, false)
	await _step(player)
	# player.gd decelerates with move_toward(vx, 0, SPEED), so one call lands
	# exactly on zero. This is a behaviour, not an accident, and A7 must not
	# change it: the run cycle's RUN -> IDLE edge is one frame wide.
	_check("releasing right stops in ONE frame",
		_state_of(player) == S.IDLE, "vx %.3f" % player.velocity.x)

	# --- 3. the jump arc --------------------------------------------------
	var before_jump := _frame
	_key(KEY_SPACE, true)
	await _step(player)
	_key(KEY_SPACE, false)
	_check("jump leaves the floor at once",
		_state_of(player) == S.AIRBORNE_RISING,
		"vy %.1f" % player.velocity.y)
	var air := 1
	while not player.is_on_floor() and air < 200:
		await _step(player)
		air += 1
	_check("lands again within 200 frames", player.is_on_floor(),
		"airborne %d frames" % air)
	_note("airborne for %d frames at 60 fps = %.3f s" % [air, air / 60.0])
	_check("the arc passed through FALLING",
		_sequence().has("FALLING"), " -> ".join(_sequence()))

	# --- 4. the gameplay fact the swing will later be read against --------
	# A7's committing action locks movement. Nothing locks it today, so what
	# is pinned is the thing that must still be true afterwards: on the
	# floor, with no input, the player does not move.
	await _run_frames(player, 10)
	var x0 := player.global_position.x
	await _run_frames(player, 20)
	_check("no input, no movement",
		is_equal_approx(player.global_position.x, x0),
		"drift %.4f px" % absf(player.global_position.x - x0))

	# --- 5. health and death ---------------------------------------------
	_check("starts at MAX_HEALTH", player.health == 5, str(player.health))
	player.take_damage(1)
	_check("one point of damage removes one", player.health == 4,
		str(player.health))
	await _step(player)
	_check("damage alone does not change the state",
		_state_of(player) == S.IDLE, NAMES[_state_of(player)])
	player.take_damage(99)
	await _step(player)
	_check("health floors at 0", player.health == 0, str(player.health))
	_check("zero health is DEAD", _state_of(player) == S.DEAD,
		NAMES[_state_of(player)])

	# --- the sequence itself, which is the pin ----------------------------
	var seq := " -> ".join(_sequence())
	print("")
	print("STATE SEQUENCE  ", seq)
	for row in _log:
		print("  frame %4d  %s" % [row[0], NAMES[row[1]]])
	print("")
	_check("the ordered sequence is the one the brief's table produces",
		seq == "FALLING -> IDLE -> RUN -> IDLE -> RISING -> FALLING -> IDLE -> DEAD",
		seq)
	_note("x at the end of the 30-frame run: %.1f" % x_after_run)
	_note("frames: settle %d, run from %d, jump at %d" % [
		settle, run_from, before_jump])
	_note("the jump is airborne for 0.600 s, which is exactly the swing's")
	_note("  length in CHANGE-BRIEF.md section 6. Noticed, not designed:")
	_note("  it means a jump and a swing cost the player the same time.")

	main.queue_free()
	await process_frame

	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("A headless run draws nothing. This pin says what the player DOES,")
	print("never what it looks like doing it.")
	quit(0 if _failures == 0 else 1)
