extends Node2D
## The fixture behind Effect B's frame strips. Assignment 6, Step 4.
##
##   godot --path godot res://previews/dungeon_motes_preview.tscn \
##       --write-movie "$PWD/captures/dungeon_motes/r0/frame.png" \
##       --fixed-fps 30 --quit-after 350
##
## **This is a fixture, not the game.** Every capture taken from it is
## labelled as one wherever it appears. The background is a real stretch of
## this level -- `room_backdrop.gd`'s wall, torches and alcoves, the floor
## tile, all three traps where the backdrop breaks the lit lip, and the real
## player -- at in-game camera scale.
##
## **The player is real, and the death is real.** Effect B's condition ends on
## `player.gd`'s `died` signal, so this preview ends it by dealing the player
## its whole health through `take_damage()`, the same entry point a spike uses.
## A preview that set `emitting = false` itself would be testing the preview.
##
## `use_fixed_seed` is pinned **here, on the node this preview owns** -- never
## in `dungeon_motes.tscn`, where `CHANGE-BRIEF.md` section 2.2's variation
## paragraph needs the field to differ. `test_dungeon_motes_config.gd` asserts
## the effect scene does not pin it.
##
## Section 2.5 reads frames 10, 11, 40, 100, 130 and 340. Frame **1** is kept
## as well -- revision 6.0.3 -- because B1 is a claim about the FIRST drawn
## frame and frame 10 is not it.

## Section 2.5: the condition ends here, and the strip reads 30 frames later.
const KILL_FRAME := 100

## Pinned so two runs of this preview produce the same field. The game's own
## motes are never seeded.
@export var fixed_seed: int = 727002

var _frame := 0
var _killed := false

@onready var _player: Node = $Player
@onready var _motes: GPUParticles2D = $DungeonMotes


func _ready() -> void:
	_motes.use_fixed_seed = true
	_motes.seed = fixed_seed


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == KILL_FRAME and not _killed:
		_killed = true
		# The real entry point, with the real signal on the other end.
		_player.take_damage(_player.MAX_HEALTH)
