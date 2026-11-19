extends SceneTree
## Assignment 7 — the state machine, asserted against the resource and then
## driven through the real game loop.
##
##   ./scripts/run-test.sh test_player_states.gd 60
##
## Two halves, and they prove different things:
##
## **Structure.** Every clip name `player_anim.gd` can ask for exists in the
## library, and every clip the brief's §7 table names is there. A state that
## requests a clip nobody wrote fails at the moment it is entered, in play,
## with nothing in the log — this catches it before that.
##
## **Behaviour.** The machine is driven with synthesized key events through
## `Input.parse_input_event`, which is the path a player's keys take.
## `Input.action_press` never reaches `_input` or `_unhandled_input`, so a
## test built on it exercises nothing — Assignment 7 names that trap.
##
## **The current clip is read with `current_animation`**, which is the
## `AnimationPlayer` property. `AnimatedSprite2D`'s is called `animation`, and
## a state test that reads the wrong one passes whatever the game does. This
## project has no `AnimatedSprite2D`; the distinction is asserted anyway,
## because the next person to add one will not remember it.
##
## It proves the right clip is PLAYING. It cannot prove anything about how
## the motion looks: a headless run draws nothing.

const MAIN := "res://game/main.tscn"
## CHANGE-BRIEF.md §7's table, and nothing else may be requested.
const STATE_CLIPS := {
	"IDLE": "idle", "RUN": "run", "AIRBORNE_RISING": "rising",
	"AIRBORNE_FALLING": "falling", "SWING": "swing", "DEAD": "dead",
}

var _checks := 0
var _failures := 0
var _frame := 0


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


func _step(hold: Array = []) -> void:
	for code in hold:
		_key(code, true)
	await process_frame
	_frame += 1


func _run(n: int, hold: Array = []) -> void:
	for i in range(n):
		await _step(hold)


func _init() -> void:
	await process_frame
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame

	var player: Player = main.get_node(^"Player")
	var ap: AnimationPlayer = player.get_node(^"AnimationPlayer")

	# --- structure: the state table against the resource ------------------
	for state in STATE_CLIPS:
		var clip: String = STATE_CLIPS[state]
		_check("state %s requests a clip that exists: '%s'" % [state, clip],
			ap.has_animation(clip))
	_check("the library holds no clip the table does not name, except RESET",
		_extra_clips(ap).is_empty(), ", ".join(_extra_clips(ap)))
	_check("the clip is read through AnimationPlayer.current_animation",
		"current_animation" in ap,
		"AnimatedSprite2D's property is called `animation`; this is not one")
	_check("nothing autoplays", ap.autoplay == "", ap.autoplay)

	# --- behaviour: driven through the real loop --------------------------
	while not player.is_on_floor() and _frame < 120:
		await _step()
	await _run(6)
	_check("standing still plays 'idle'", ap.current_animation == "idle",
		ap.current_animation)

	await _run(20, [KEY_D])
	_check("holding right plays 'run'", ap.current_animation == "run",
		ap.current_animation)
	_check("'run' is the looping clip",
		ap.get_animation("run").loop_mode == Animation.LOOP_LINEAR)
	_key(KEY_D, false)
	await _step()
	_check("releasing goes back to 'idle'", ap.current_animation == "idle",
		ap.current_animation)

	_key(KEY_SPACE, true)
	await _step()
	_key(KEY_SPACE, false)
	_check("jumping plays 'rising'", ap.current_animation == "rising",
		ap.current_animation)
	var air := 1
	var saw_falling := false
	while not player.is_on_floor() and air < 200:
		await _step()
		air += 1
		if ap.current_animation == "falling":
			saw_falling = true
	_check("the arc passes through 'falling'", saw_falling)
	await _run(2)
	_check("landing goes back to 'idle'", ap.current_animation == "idle",
		ap.current_animation)

	# --- the committing action ---------------------------------------------
	var before := player.swing_count
	_key(KEY_J, true)
	await _step()
	_key(KEY_J, false)
	_check("attack plays 'swing'", ap.current_animation == "swing",
		ap.current_animation)
	_check("the player is locked", player.is_locked())
	_check("swing_count incremented", player.swing_count == before + 1,
		"%d -> %d" % [before, player.swing_count])

	# **Inverted by revision 7.0.6**, not deleted. Until then this asserted
	# "holding right during the swing moves the player 0 px", and it passed
	# for a year of commits. The author then asked to be able to walk while
	# swinging, so the rule changed and the assertion changed with it -- a
	# test left asserting the old rule would have been the loudest possible
	# way to find out the design had moved, which is why it is inverted here
	# rather than removed.
	#
	# What a commitment still forbids is asserted in `test_swing_edges.gd`
	# section D: no cancel, no restart, no jump, no TURN, all 18 frames.
	var x0 := player.global_position.x
	await _run(6, [KEY_D])
	_key(KEY_D, false)
	_check("holding right during the swing DOES move the player now",
		absf(player.global_position.x - x0) > 1.0,
		"travelled %.4f px" % absf(player.global_position.x - x0))
	_check("and it is still playing `swing`, not `run`",
		ap.current_animation == "swing", ap.current_animation)

	# Let it finish. 0.600 s is 36 frames at 60 fps, plus slack. The count
	# starts at the frame the swing began, NOT here -- six frames of holding
	# right have already gone by, and a duration measured from the wrong
	# zero is the mistake this project keeps finding.
	var locked_frames := 6
	while player.is_locked() and locked_frames < 120:
		await _step()
		locked_frames += 1
	_check("the swing ends on its own", not player.is_locked(),
		"after %d frames (%.3f s)" % [locked_frames, locked_frames / 60.0])
	_check("the lock lasts the clip's own 0.600 s, within one frame",
		absf(locked_frames / 60.0 - 0.6) <= 1.0 / 60.0,
		"%.4f s against 0.6000" % (locked_frames / 60.0))
	await _run(2)
	_check("after the swing, back to 'idle'", ap.current_animation == "idle",
		ap.current_animation)

	# --- death wins over everything ----------------------------------------
	player.take_damage(99)
	await _run(2)
	_check("zero health plays 'dead'", ap.current_animation == "dead",
		ap.current_animation)
	_check("'dead' does not loop",
		ap.get_animation("dead").loop_mode == Animation.LOOP_NONE)

	main.queue_free()
	await process_frame
	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	print("This says the right clip is PLAYING in each state. It says nothing")
	print("about how any of it looks — a headless run draws nothing.")
	quit(0 if _failures == 0 else 1)


func _extra_clips(ap: AnimationPlayer) -> Array[String]:
	var named: Array = STATE_CLIPS.values()
	named.append("RESET")
	var extra: Array[String] = []
	for name in ap.get_animation_list():
		if not named.has(String(name)):
			extra.append(String(name))
	return extra
