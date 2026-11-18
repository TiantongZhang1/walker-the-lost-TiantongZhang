extends Node2D
## The fixture behind the committing action's frame strip.
## `CHANGE-BRIEF.md` §10.
##
##   godot --path godot res://previews/swing_preview.tscn \
##       --write-movie "$PWD/captures/swing/r0/frame.png" \
##       --fixed-fps 30 --quit-after 60
##
## **This is a fixture, not the game.** Every capture taken from it is
## labelled as one wherever it appears.
##
## **Captured at 30 fps, which is the phase table's own rate**, so one
## captured frame is one table frame and the strip can be read against §6
## without arithmetic. The trigger is on capture frame 10, leaving ten frames
## of the resting pose to compare against.
##
## The player stands at x 150. `SpikeTrap1`'s detection zone starts at x 175,
## so nothing fires during the strip: a trap firing mid-capture would put
## Effect A's burst in the frame and make the picture about two things.

## §10's timeline, in frames at 30 fps. Capture frame 10 is table frame 0.
const TRIGGER_FRAME := 10

var _frame := 0


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
