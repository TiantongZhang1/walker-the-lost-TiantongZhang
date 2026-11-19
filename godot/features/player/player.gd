class_name Player
extends CharacterBody2D

## The Lost's player.
##
## Move and jump, enough health for a spike trap to mean something, and, from
## Assignment 7, **one committing attack**. The GDD's three-hit combo, MP
## magic and dodge roll are still not here; `GDD.md:393` lists the full state
## machine and this builds five of its states.
##
## **Assignment 7 changes movement, and `CHANGE-BRIEF.md` §11 names the
## change before it happens.** Speed, jump velocity, gravity and the existing
## bindings are untouched. What is new is that a swing LOCKS movement until
## the clip ends, which is `GDD.md:198` in code: *"The combo is committed:
## once a swing starts it finishes, so holding attack is a real risk and
## letting go is a real choice."*
##
## **This script owns the state machine, because locking movement is
## gameplay.** `player_anim.gd` reads it and plays clips; it writes nothing
## here. The one thing that crosses the other way is the clip's own clock:
## this script listens to `AnimationPlayer.animation_finished` to learn that
## the swing is over, and reads `current_animation_position` to tell startup
## and active from recovery. That is the game reading a node in its own
## scene, and it is the measurement `CHANGE-BRIEF.md` §8 is about.
##
## Scale: 16 px = 1 m, so this 28 px sprite is a 1.75 m adventurer.

signal health_changed(current: int, maximum: int)
signal died

## What the player is committed to. Presentation reads it; nothing outside
## this script writes it.
enum Action { NONE, SWING }

const MAX_HEALTH := 5
const SPEED := 96.0           # 6 m/s
const JUMP_VELOCITY := -260.0
const GRAVITY := 900.0

const SWING_CLIP := "swing"
## CHANGE-BRIEF.md §6: recovery begins on frame 10 at 30 fps. A second
## attack is ignored before this and buffered after it.
const RECOVERY_START := 0.3333333

var health := MAX_HEALTH
var action := Action.NONE
## Increments on every swing that actually starts. `player_anim.gd` watches
## it to know a NEW swing began, because `AnimationPlayer.play()` called with
## the name already playing resumes instead of restarting.
var swing_count := 0

var _buffered_attack := false

@onready var _anim: AnimationPlayer = $AnimationPlayer


func _ready() -> void:
	_anim.animation_finished.connect(_on_animation_finished)


## True while the swing owns the player. Read by `_physics_process` every
## physics tick, which is the tick the active window is read on.
func is_locked() -> bool:
	return action == Action.SWING


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta

	if is_locked():
		# Committed. No steering, no turn, no jump. A second attack is
		# ignored in startup and active and buffered in recovery -- the
		# phase comes from the clip's own playhead, not from a timer here.
		#
		# **On the ground the swing PLANTS: velocity.x is held at 0 every
		# tick. In the air it does not.** There is nothing to plant against
		# mid-jump, and zeroing x would stop the arc dead and drop the
		# player straight down. What a commitment locks out is INPUT, not
		# physics: the horizontal velocity the jump already had is carried,
		# and no key can change it. Revision 7.0.5.
		if is_on_floor():
			velocity.x = 0.0
		if Input.is_action_just_pressed("attack") \
				and _anim.current_animation == SWING_CLIP \
				and _anim.current_animation_position >= RECOVERY_START:
			_buffered_attack = true
		move_and_slide()
		return

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	# **No `is_on_floor()` here since revision 7.0.5**: the author asked for
	# the swing in the air. Gravity still runs above, the clip is still
	# `LOOP_NONE` and still 0.600 s, and `player_anim.gd` already ranks
	# `is_locked()` above the airborne branch, so `swing` wins over
	# `rising`/`falling` without that file changing at all.
	if Input.is_action_just_pressed("attack") and health > 0:
		_start_swing()
		move_and_slide()
		return

	var direction := Input.get_axis("move_left", "move_right")
	if is_zero_approx(direction):
		velocity.x = move_toward(velocity.x, 0.0, SPEED)
	else:
		velocity.x = direction * SPEED

	move_and_slide()


func _start_swing() -> void:
	action = Action.SWING
	swing_count += 1
	# Planted on the ground, momentum kept in the air. Landing mid-swing
	# plants on the tick the floor is found, because the lock re-tests
	# `is_on_floor()` every tick rather than remembering this one.
	if is_on_floor():
		velocity.x = 0.0


func _on_animation_finished(name: StringName) -> void:
	if name != SWING_CLIP:
		return
	action = Action.NONE
	# The buffered swing no longer needs the floor either -- otherwise a
	# swing buffered during an airborne recovery would be silently dropped,
	# which is H6's failure wearing a different hat.
	if _buffered_attack and health > 0:
		_buffered_attack = false
		_start_swing()
	else:
		_buffered_attack = false


func take_damage(amount: int) -> void:
	if health <= 0:
		return
	health = maxi(health - amount, 0)
	health_changed.emit(health, MAX_HEALTH)
	if health == 0:
		# Death aborts the swing. Committed means committed to the swing, not
		# to finishing it after dying -- CHANGE-BRIEF.md §7's interrupt table.
		action = Action.NONE
		_buffered_attack = false
		died.emit()
