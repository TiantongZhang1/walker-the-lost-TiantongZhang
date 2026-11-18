extends Node2D
## The fixture behind the cycle's frame strip. `CHANGE-BRIEF.md` §10.
##
##   godot --path godot res://previews/run_preview.tscn \
##       --write-movie "$PWD/captures/run/r0/frame.png" \
##       --fixed-fps 30 --quit-after 60
##
## **This is a fixture, not the game.** Every capture taken from it is
## labelled as one wherever it appears.
##
## **The cycle is 0.250 s and the capture is 30 fps**, so one cycle is 7.5
## captured frames — the strip is NOT one frame per key. It is read for
## registration and for whether the legs read as a stride, not for cell
## order; cell order is the read-back's job and there are no cells here
## anyway, because the cycle is a rig.
##
## It runs RIGHT, then LEFT, so one strip carries both facings and the
## `Rig.scale.x` mirror can be read rather than assumed — the same reason
## Effect C's fixture turns around.
##
## The run is bounded so the player never enters a trap's detection zone:
## the nearest starts at x 175 and the turn is at x 150.

const RUN_RIGHT_FRAME := 10
const TURN_FRAME := 34
const STOP_FRAME := 54

var _frame := 0


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == RUN_RIGHT_FRAME:
		_key(KEY_D, true)
	elif _frame == TURN_FRAME:
		_key(KEY_D, false)
		_key(KEY_A, true)
	elif _frame == STOP_FRAME:
		_key(KEY_A, false)


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()
