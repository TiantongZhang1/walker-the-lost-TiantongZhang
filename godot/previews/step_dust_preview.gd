extends Node2D
## The fixture behind Effect C's frame strips. Revision 6.0.4 section C.5.
##
##   godot --path godot res://previews/step_dust_preview.tscn \
##       --write-movie "$PWD/captures/step_dust/r0/frame.png" \
##       --fixed-fps 30 --quit-after 110
##
## **This is a fixture, not the game.** Every capture taken from it is
## labelled as one wherever it appears.
##
## **It runs right, then left, then stops**, because the one thing no test in
## this repository can answer is G3: whether `scale.x = -1` on the instance
## actually mirrors the throw of a `local_coords = false` emitter. One strip
## with both facings in it settles that by being looked at.
##
## The walk is bounded so the player never enters a trap's detection zone --
## the nearest starts at x 175 and the run turns around at x 150. A trap
## firing mid-strip would put Effect A's burst in the frame and make the
## picture about two effects at once.
##
## Seeds are pinned **on the instances the driver spawns**, from here, never
## in `step_dust.tscn`: section C.2's variation paragraph needs every step to
## differ in the game, and `test_step_dust_config.gd` asserts the effect scene
## does not pin a seed.

## Section C.5's timeline, in frames at 30 fps.
const RUN_RIGHT_FRAME := 10
const TURN_FRAME := 42
const STOP_FRAME := 82

@export var fixed_seed: int = 727003

var _frame := 0
var _seeded := {}

@onready var _room: Node = self


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == RUN_RIGHT_FRAME:
		_key(KEY_D, true)
	elif _frame == TURN_FRAME:
		_key(KEY_D, false)
		_key(KEY_A, true)
	elif _frame == STOP_FRAME:
		_key(KEY_A, false)
	_pin_seeds()


## The driver owns the instances, so the seed is pinned here, on each one, as
## it appears. Every instance gets the SAME seed on purpose: two captures of
## this preview then produce the same picture, which is what makes a
## before-and-after comparison mean anything.
func _pin_seeds() -> void:
	for child in _room.get_children():
		if not child.has_method("fire") or _seeded.has(child.get_instance_id()):
			continue
		_seeded[child.get_instance_id()] = true
		for grand in child.get_children():
			if grand is GPUParticles2D:
				var p := grand as GPUParticles2D
				p.use_fixed_seed = true
				p.seed = fixed_seed


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()
