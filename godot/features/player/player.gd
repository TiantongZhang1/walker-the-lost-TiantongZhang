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

	# **Revision 7.0.6: a swing no longer locks movement.** The author asked
	# to be able to walk while swinging, so the movement block below now runs
	# whether or not a swing owns the player. Revision 7.0.5's ground-plant /
	# air-carry split goes with it: there is nothing left to plant or to carry
	# once the axis is read every tick either way.
	#
	# **What a commitment still means here, and it is not nothing:**
	#   * it cannot be CANCELLED -- no input sets `action` back to NONE;
	#   * it cannot be RESTARTED -- a second attack is ignored in startup and
	#     active and buffered in recovery, the phase coming from the clip's
	#     own playhead rather than from a timer kept here;
	#   * it always plays ALL 18 FRAMES; `animation_finished` is the only way
	#     out of it, and death;
	#   * **no jump** -- still gated by `is_locked()` below;
	#   * **no turn.** `player_anim.gd` freezes `Rig.scale.x` while locked, so
	#     you may walk backwards out of your own swing but you may not change
	#     which way the blade is going. Direction is the commitment that
	#     survives, and it is the one the blade's arc actually depends on.
	#
	# What is lost is the movement COST -- the half of `GDD.md:198` that made
	# holding attack a risk. CHANGE-BRIEF.md revision 7.0.6 argues that trade
	# instead of hiding it.
	if is_locked():
		if Input.is_action_just_pressed("attack") \
				and _anim.current_animation == SWING_CLIP \
				and _anim.current_animation_position >= RECOVERY_START:
			_buffered_attack = true
	else:
		if Input.is_action_just_pressed("jump") and is_on_floor():
			velocity.y = JUMP_VELOCITY
		# No `is_on_floor()` on the attack since revision 7.0.5: the swing
		# works in the air. `player_anim.gd` ranks `is_locked()` above the
		# airborne branch, so `swing` wins over `rising` / `falling`.
		if Input.is_action_just_pressed("attack") and health > 0:
			_start_swing()

	var direction := Input.get_axis("move_left", "move_right")
	if is_zero_approx(direction):
		velocity.x = move_toward(velocity.x, 0.0, SPEED)
	else:
		velocity.x = direction * SPEED

	move_and_slide()


func _start_swing() -> void:
	action = Action.SWING
	swing_count += 1
	# Revision 7.0.6: this no longer touches velocity at all. A swing
	# that planted the player on its first frame and let them walk on
	# the second would read as a stutter, and the movement block runs
	# on this frame too now.


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
