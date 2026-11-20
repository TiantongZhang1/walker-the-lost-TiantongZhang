extends Node2D
## The fixture behind revision 7.0.9's strip: a swing WITH A DIRECTION HELD.
##
##   godot --path godot res://previews/swing_move_preview.tscn \
##       --write-movie "$PWD/captures/swing_move/r0/frame.png" \
##       --fixed-fps 30 --quit-after 60
##
## **This is a fixture, not the game.** Every capture taken from it is
## labelled as one wherever it appears.
##
## `swing_preview.tscn` swings standing still, which is what §10's table
## describes and what `captures/swing/r1`–`r4` are. It cannot show the thing
## the author rejected on 2026-11-20 — a swing that *travels* — because
## nothing in it travels. So this one holds **D** from the first frame and
## triggers the swing at frame 10, and the two strips together are the
## before-and-after of revision 7.0.9.
##
## Same background, same traps, same camera as `swing_preview.tscn`, and the
## player starts far enough left that holding D for two seconds does not
## reach `SpikeTrap1`'s detection zone at x 175 before the clip is over.

const TRIGGER_FRAME := 10

var _frame := 0


func _ready() -> void:
	_key(KEY_D, true)


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == TRIGGER_FRAME:
		_key(KEY_J, true)
	elif _frame == TRIGGER_FRAME + 1:
		_key(KEY_J, false)


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()
