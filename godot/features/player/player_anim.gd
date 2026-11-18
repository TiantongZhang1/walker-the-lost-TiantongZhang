extends Node
## Picks the player's clip from state the player already has, and plays it.
##
## **It replaces `pose_driver.gd`**, which wrote `Sprite2D.texture` every
## `_process`. That node was the player sprite's authority; this one writes
## **no animated property at all**. `CHANGE-BRIEF.md` §5: exactly one node
## writes to each animated node, and that node is the `AnimationPlayer`.
##
## What this script does write is `Rig.scale.x`, the facing. **No clip keys
## it**, so there is still one writer per property — and it is `Rig.scale.x`
## rather than `Body.flip_h` because the cut-out legs are separate nodes:
## flipping only the body would leave the legs swinging the wrong way.
## Revision 7.0.1 records the change from `flip_h`.
##
## **`play()` called with the clip already playing RESUMES, it does not
## restart.** Chapter 10 states it and `CHANGE-BRIEF.md` H6 predicts the bug
## it causes: a second swing buffered during recovery would silently not
## happen. So this watches `player.swing_count`, which the player increments
## on every swing that actually starts, and seeks to 0 when it changes.
##
## It reads `velocity`, `is_on_floor()`, `health` and `action`. It writes
## none of them. Presentation reads game state and never writes it.

## Below this the player is standing still as far as the clip is concerned.
## `player.gd` decelerates with `move_toward(..., SPEED)`, so x velocity lands
## exactly on 0 rather than drifting, and any small value means input.
const MOVING_EPS := 1.0

@onready var _body: Player = get_parent() as Player
@onready var _anim: AnimationPlayer = _body.get_node_or_null(^"AnimationPlayer")
@onready var _rig: Node2D = _body.get_node_or_null(^"Rig")

## The poses are drawn facing right. `player.gd` has no facing of its own --
## it does not need one -- so the last direction actually walked is remembered
## here, where it is a presentation detail.
var _facing := 1.0
var _last_swing := -1


## **On the PHYSICS tick, not `_process`.**
##
## `player.gd` writes `velocity`, `action` and `health` in
## `_physics_process`. Reading them from `_process` meant this node saw last
## tick's state: the structure test caught `run` still playing one frame
## after the key was released, and `idle` still playing on the frame the
## swing started. One frame at 60 fps is 16.7 ms, which is exactly the
## disagreement `CHANGE-BRIEF.md` §8 predicts for two nodes on two clocks --
## found here by a test rather than by watching the game.
##
## The AnimationPlayer is already on physics (`callback_mode_process = 0`),
## so writer, reader and mixer now share one tick.
func _physics_process(_delta: float) -> void:
	if _body == null or _anim == null or _rig == null:
		return

	if not _body.is_locked() and absf(_body.velocity.x) > MOVING_EPS:
		_facing = signf(_body.velocity.x)
	_rig.scale.x = _facing

	var want := _clip_for_state()
	var restart := want == "swing" and _body.swing_count != _last_swing
	if restart:
		_last_swing = _body.swing_count
	if want != _anim.current_animation or restart:
		_anim.play(want)
		if restart:
			# play() alone would resume a swing already running. Seeking with
			# `update` true applies frame 0's keys on this tick rather than
			# on the next one.
			_anim.seek(0.0, true)


func _clip_for_state() -> StringName:
	if _body.health <= 0:
		return &"dead"
	if _body.is_locked():
		return &"swing"
	if not _body.is_on_floor():
		return &"rising" if _body.velocity.y < 0.0 else &"falling"
	if absf(_body.velocity.x) > MOVING_EPS:
		return &"run"
	return &"idle"
