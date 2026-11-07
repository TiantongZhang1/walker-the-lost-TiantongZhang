extends Node
## Puts Effect C on an event the game does not have. Revision 6.0.4, step C.
##
## **It changes no game script.** `player.gd` and the input map are out of
## scope in `CHANGE-BRIEF.md` §3 and stay out of scope. This node reads
## `global_position`, `is_on_floor()` and `health` — the same three things
## `pose_driver.gd` reads — and writes nothing back.
##
## **There is no footstep signal, so the event is derived.** The cadence is
## **distance travelled on the ground**, not a timer and not a per-frame
## chance:
##
##     _since_step += absf(x - previous x)      # only while on the floor
##     if _since_step >= stride_px:  one puff,  _since_step -= stride_px
##
## Section C.1 gives the reasoning and G1 the failure this avoids. A timer is
## right at exactly one speed; a per-frame spawn changes with the frame rate,
## which is the mistake Assignment 5's chapter 6 is about. Measured position
## delta is correct at any speed and any frame rate **by construction**, and
## `test_step_dust_state.gd` runs at 30, 60 and 144 to show it rather than to
## trust it.
##
## **The stride length is not in this file.** `stride_px` is an `@export` and
## `game/main.tscn` sets it, because 24 px is design and §3 puts design in
## scene files. Everything else here is lifecycle.

const DUST := preload("res://effects/step_dust.tscn")

## Section C.3: a stride displaces less dust than a landing.
const RATIO_STRIDE := 0.6
const RATIO_LANDING := 1.0

## Below this the player is standing still as far as the dust is concerned.
## Same constant and same reasoning as `pose_driver.gd`: `player.gd`
## decelerates with `move_toward(..., SPEED)`, so x velocity lands exactly on
## 0 and any smaller value is numerical noise, not a step.
const MOVING_EPS := 1.0

## Section C.1. 24 px is 1.5 m at this game's 16 px = 1 m — a running stride.
## Set from the scene; the default is here only so the node works unconfigured.
@export var stride_px: float = 24.0
## Where puffs are parented. Rule C5: the room, never the player.
@export var room_path: NodePath = ^".."
@export var player_path: NodePath = ^"../Player"

var _room: Node = null
var _player: CharacterBody2D = null
var _foot_offset := 14.0
var _since_step := 0.0
var _last_x := 0.0
var _was_on_floor := true
var _live: Array[Node2D] = []


func _ready() -> void:
	_room = get_node_or_null(room_path)
	_player = get_node_or_null(player_path) as CharacterBody2D
	if _player == null:
		return
	_last_x = _player.global_position.x
	_was_on_floor = _player.is_on_floor()
	# C2: the puff belongs at the underside of the collision box, not at the
	# body origin. Read from the shape so it cannot drift if the box changes.
	var cs := _player.get_node_or_null(^"CollisionShape2D") as CollisionShape2D
	if cs != null and cs.shape is RectangleShape2D:
		_foot_offset = (cs.shape as RectangleShape2D).size.y * 0.5


func _process(_delta: float) -> void:
	if _player == null or _room == null:
		return

	var x: float = _player.global_position.x
	var previous_x: float = _last_x
	var moved: float = absf(x - previous_x)
	_last_x = x

	var on_floor: bool = _player.is_on_floor()
	var alive: bool = _player.health > 0

	# C1: nothing at all once the player is dead.
	if not alive:
		_was_on_floor = on_floor
		return

	# C4: the landing is the TRANSITION, not the state. Spawning on the state
	# would put a puff under the player on every frame they stand on the
	# floor, which is G5.
	if on_floor and not _was_on_floor:
		_spawn(RATIO_LANDING)
		# The landing already kicked the dust up; the next stride starts from
		# zero rather than from whatever was left over before the jump.
		_since_step = 0.0
	_was_on_floor = on_floor

	# C1: strides only on the ground, and only while actually moving.
	if not on_floor or absf(_player.velocity.x) <= MOVING_EPS:
		return

	_since_step += moved
	# `while`, not `if`: at a low frame rate one frame can cover more than one
	# stride, and the cadence is a distance. Dropping the extra puff would
	# make the effect frame-rate dependent in exactly the way C3 forbids.
	#
	# **The puff is placed where the stride finished, not where the player is
	# now.** After the subtraction `_since_step` IS the distance travelled
	# past the crossing, so stepping back by it lands on the crossing exactly.
	# Without this the puff is up to one frame of travel ahead of the foot --
	# 1.6 px at 60 fps and 3.2 px at 30 -- and the spacing between puffs is
	# frame-rate dependent, which is the thing C3 exists to forbid. It was
	# measured at 3.2 px by `test_step_dust_state.gd` at 30 fps before this.
	var direction: float = signf(x - previous_x)
	while _since_step >= stride_px:
		_since_step -= stride_px
		_spawn(RATIO_STRIDE, -direction * _since_step)


## `x_offset` steps the spawn back to where the stride actually finished.
## Zero for a landing, which happens on its own frame and needs no back-dating.
func _spawn(ratio: float, x_offset := 0.0) -> void:
	var dust := DUST.instantiate() as Node2D
	_room.add_child(dust)
	dust.global_position = Vector2(
		_player.global_position.x + x_offset,
		_player.global_position.y + _foot_offset)
	# C.2's facing. The scene throws its specks back and up for a character
	# running right; a negative x scale mirrors the whole instance. Whether
	# that actually mirrors the emission of a local_coords = false emitter is
	# what the strip is for.
	if _player.velocity.x < -MOVING_EPS:
		dust.scale.x = -1.0
	dust.call(&"fire", ratio)
	_live.append(dust)


## C5, for the state test: how many puffs are alive right now. Instances free
## themselves, so this prunes rather than counts a stale list. Written as a
## loop and not `filter()` — see `hit_burst_spawner.gd`, where a typed lambda
## threw on every call once an instance had died.
func live_count() -> int:
	var kept: Array[Node2D] = []
	for d in _live:
		if is_instance_valid(d):
			kept.append(d)
	_live = kept
	return _live.size()


## C2/C4/C6, for the state test: the live instances, newest last.
func live_dust() -> Array[Node2D]:
	live_count()
	return _live


## C3, for the state test: how far the player has walked since the last puff.
func distance_since_step() -> float:
	return _since_step
