extends GPUParticles2D
## Effect B's condition, and nothing else.
##
## **No setting lives here.** `CLAUDE.md`'s Ownership rule puts the design in
## `dungeon_motes.tscn`. This script writes exactly one property, `emitting`,
## and only ever to `false`.
##
## **It reads game state and never writes it.** `CHANGE-BRIEF.md` section 2.4
## rule B5. It listens to `player.gd`'s `died` signal, which already exists at
## `:16` and is emitted at `:48` — the same boundary `trap_warning_driver.gd`,
## `room_backdrop.gd`, `room_audio.gd` and `pose_driver.gd` keep.
##
## **Nothing starts the field.** It is emitting from the first frame because
## the scene says so, and `preprocess = 8.0` means that first frame is already
## at steady state. A script that turned it on in `_ready()` would be a script
## that could forget to.
##
## **B2: stopping is not clearing.** Setting `emitting = false` stops new motes
## being born; the ones already alive finish their 8 s and fade out on the
## colour ramp. `restart()` or `emitting = false` plus a `hide()` would both
## cut the field off mid-air, which is the thing a death transition should not
## do.

## Where the player is. Set in the scene so the state test can read it back.
@export var player_path: NodePath = ^"../Player"

var _player: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path)
	if _player != null and _player.has_signal(&"died"):
		_player.died.connect(_on_player_died)


func _on_player_died() -> void:
	emitting = false


## For the state test: did this node find the signal it depends on? A missing
## player would otherwise look exactly like a player who never dies.
func is_listening() -> bool:
	return _player != null and _player.has_signal(&"died") \
		and _player.died.is_connected(_on_player_died)
