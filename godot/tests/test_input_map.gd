extends SceneTree
## Baseline smoke test: the input map exists and real synthesized key events
## reach Input as actions. Assignment 5 requires the driver test to drive game
## state "through the real game loop and real input", so this proves the
## mechanism those tests will rely on, before relying on it.

var _failures := 0

func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  "), label)
	if not ok:
		_failures += 1

func _init() -> void:
	for action in ["move_left", "move_right", "jump"]:
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

	print("\n%d checks, %d failures" % [5, _failures])
	quit(1 if _failures > 0 else 0)
