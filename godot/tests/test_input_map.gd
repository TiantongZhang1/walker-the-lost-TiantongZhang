extends SceneTree
## Baseline smoke test: the input map exists and real synthesized key events
## reach Input as actions. Assignment 5 requires the driver test to drive game
## state "through the real game loop and real input", so this proves the
## mechanism those tests will rely on, before relying on it.

var _checks := 0
var _failures := 0

func _check(label: String, ok: bool) -> void:
	_checks += 1
	print(("PASS  " if ok else "FAIL  "), label)
	if not ok:
		_failures += 1

func _init() -> void:
	# Assignment 7 adds `attack`, which CHANGE-BRIEF.md section 11 names as a
	# predicted change to this test rather than letting it arrive as a
	# surprise. Three actions became four.
	for action in ["move_left", "move_right", "jump", "attack"]:
		_check("InputMap has '%s'" % action, InputMap.has_action(action))

	# Synthesize a real key press and read it back as an action.
	var ev := InputEventKey.new()
	ev.physical_keycode = KEY_D
	ev.pressed = true
	Input.parse_input_event(ev)
	Input.flush_buffered_events()
	_check("physical D presses move_right", Input.is_action_pressed("move_right"))
	_check("get_axis reads +1", is_equal_approx(Input.get_axis("move_left", "move_right"), 1.0))

	ev = ev.duplicate()
	ev.pressed = false
	Input.parse_input_event(ev)
	Input.flush_buffered_events()
	_check("releasing D clears move_right", not Input.is_action_pressed("move_right"))

	# 2026-11-18. The author asked for jump to be on the spacebar. It already
	# was -- `jump` carries SPACE, W and UP -- but "it already is" is a claim
	# about a file, and this test only ever asserted that the ACTION EXISTS.
	# An action can exist with the wrong key on it, or with no key at all, and
	# every check above would still be green. So the key is pressed.
	for key in [[KEY_SPACE, "SPACE"], [KEY_W, "W"], [KEY_UP, "UP"]]:
		var k := InputEventKey.new()
		k.physical_keycode = key[0]
		k.pressed = true
		Input.parse_input_event(k)
		Input.flush_buffered_events()
		_check("physical %s presses jump" % key[1],
			Input.is_action_pressed("jump"))
		k = k.duplicate()
		k.pressed = false
		Input.parse_input_event(k)
		Input.flush_buffered_events()
		_check("releasing %s clears jump" % key[1],
			not Input.is_action_pressed("jump"))

	# The count was hard-coded as 5. It stayed 5 when a fourth action
	# was added and the run grew to seven checks -- a summary that lied
	# about its own test. It is counted now.
	print("\n%d checks, %d failures" % [_checks, _failures])
	quit(1 if _failures > 0 else 0)
