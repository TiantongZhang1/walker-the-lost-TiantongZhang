extends Node
## Picks the player's pose from state the player already has.
##
## **It changes no game script.** `player.gd` is not touched: this node reads
## `velocity`, `is_on_floor()` and `health` and writes one `Sprite2D.texture`.
## Presentation reads game state and never writes it, which is the boundary
## `trap_warning_driver.gd` keeps for the shader and `room_audio.gd` keeps for
## the sound. Assignment 5's CLAUDE.md puts player movement and the input map
## out of scope, and nothing here is either.
##
## **Provenance.** The five poses in `godot/assets/poses/` are carried from
## walker-ninja-TiantongZhang, where they were generated and documented:
## GPT-6 from a single character reference, prompts and per-pose measurements
## recorded in that repository's `SOURCES.md` section 3 and `CHARACTER-SHEET`.
## They are **generated art**, and `ATTRIBUTION.md` here says so rather than
## letting this repository go on claiming it has none. Three of walker-ninja's
## eight are not carried: dash, windup and live belong to a combat move this
## slice does not have.
##
## **Why the sprite is centred and not offset.** The poses are 32 x 32 with
## the figure's feet on row 30; the body is a 10 x 28 box centred on the
## origin, so its underside is at y = +14. A centred 32 px sprite spans
## y -16..+16 and puts row 30 at y = +14 — the feet land on the collision
## box's floor with no offset to maintain. That was arithmetic, and then it
## was checked against a rendered frame.

const POSE_IDLE: Texture2D = preload("res://assets/poses/p1-idle.png")
const POSE_RUN: Texture2D = preload("res://assets/poses/p2-run.png")
const POSE_RISING: Texture2D = preload("res://assets/poses/p3-rising.png")
const POSE_FALLING: Texture2D = preload("res://assets/poses/p4-falling.png")
const POSE_DEATH: Texture2D = preload("res://assets/poses/p8-death.png")

## Below this the player is standing still as far as the pose is concerned.
## player.gd decelerates with move_toward(…, SPEED), so x velocity lands
## exactly on 0 rather than drifting, and any small value means input.
const MOVING_EPS := 1.0

@onready var _body: CharacterBody2D = get_parent() as CharacterBody2D
@onready var _sprite: Sprite2D = _body.get_node_or_null(^"Sprite2D")

## The poses are drawn facing right. player.gd has no facing of its own -- it
## does not need one -- so the last direction actually walked is remembered
## here, where it is a presentation detail.
var _facing := 1.0


func _process(_delta: float) -> void:
	if _body == null or _sprite == null:
		return

	if absf(_body.velocity.x) > MOVING_EPS:
		_facing = signf(_body.velocity.x)
	_sprite.flip_h = _facing < 0.0

	_sprite.texture = _pose_for_state()


func _pose_for_state() -> Texture2D:
	if _body.health <= 0:
		return POSE_DEATH
	if not _body.is_on_floor():
		return POSE_RISING if _body.velocity.y < 0.0 else POSE_FALLING
	if absf(_body.velocity.x) > MOVING_EPS:
		return POSE_RUN
	return POSE_IDLE
