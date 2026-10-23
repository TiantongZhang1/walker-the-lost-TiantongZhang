extends SceneTree
## One-off: write the input map and the main scene into project.godot through
## Godot itself, so InputEventKey is serialized exactly as the engine expects
## rather than hand-written into the .ini. Kept in the repository as the
## provenance of those settings. Run once:
##   godot --headless --path godot --script res://tools/setup_input_map.gd

func _key(physical: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = physical
	return e

func _action(name: String, keys: Array) -> void:
	var path := "input/" + name
	var events: Array[InputEvent] = []
	for k in keys:
		events.append(_key(k))
	ProjectSettings.set_setting(path, {"deadzone": 0.2, "events": events})

func _init() -> void:
	_action("move_left",  [KEY_A, KEY_LEFT])
	_action("move_right", [KEY_D, KEY_RIGHT])
	_action("jump",       [KEY_SPACE, KEY_W, KEY_UP])
	ProjectSettings.set_setting("application/run/main_scene", "res://game/main.tscn")
	var err := ProjectSettings.save()
	print("ProjectSettings.save() -> ", err, " (0 == OK)")
	quit(0 if err == OK else 1)
