extends Node2D
## The fixture behind Effect A's frame strips. Assignment 6, Step 2.
##
##   godot --path godot res://previews/hit_burst_preview.tscn \
##       --write-movie "$PWD/captures/hit_burst/r0/frame.png" \
##       --fixed-fps 30 --quit-after 60
##
## **This is a fixture, not the game.** Every capture taken from it is
## labelled as one wherever it appears. It exists because particle randomness
## differs between runs, which would confound a before-and-after comparison,
## and because a burst in play happens when the player happens to walk past.
##
## `use_fixed_seed` is pinned **here, on the instance this preview spawns** —
## never in `hit_burst.tscn`, where `CHANGE-BRIEF.md` section 1.2's variation
## paragraph needs every repeat to differ. `test_hit_burst_config.gd` asserts
## the effect scene does not pin it.
##
## The background is a real stretch of this level: `room_backdrop.gd`'s wall
## and torches, the floor tile, and a real `spike_trap.tscn` standing where
## the backdrop breaks the floor's lit lip. Section 1.2 judges the burst's
## contrast against exactly that, not against the editor's grey.

const BURST := preload("res://effects/hit_burst.tscn")

## Section 1.5. Frame 10 gives the renderer time to start; frame 16 is 0.20 s
## later at 30 fps, inside the 0.60 s lifetime, so the two bursts overlap.
const TRIGGER_FRAME := 10
const RETRIGGER_FRAME := 16

## Off by default: the strip the brief reads is a single burst. Turn it on
## for the capture that demonstrates rule A3.
@export var retrigger := false

## Pinned so two runs of this preview produce the same picture. The game's
## own bursts are never seeded.
@export var fixed_seed: int = 727001

var _frame := 0
@onready var _trap: Node2D = $Traps/SpikeTrap


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == TRIGGER_FRAME:
		_spawn()
	elif _frame == RETRIGGER_FRAME and retrigger:
		_spawn()


func _spawn() -> void:
	var burst := BURST.instantiate() as Node2D
	# Section 1.1: the burst originates at the floor line, which is where the
	# spikes punch through. The trap sprite is 16 x 16 centred on y 200.
	burst.global_position = _trap.global_position
	for child in burst.get_children():
		if child is GPUParticles2D:
			var p := child as GPUParticles2D
			p.use_fixed_seed = true
			p.seed = fixed_seed
	add_child(burst)
	burst.call(&"fire")
