class_name Player
extends CharacterBody2D

## The Lost's player, cut to the minimum Assignment 5 needs.
##
## Move and jump, and enough health for a spike trap to mean something. The
## GDD's hold-attack combo, MP magic and dodge roll are NOT here: Assignment 5
## grades shaders, and CHANGE-BRIEF.md's boundaries say movement and input are
## not to be changed by this assignment. Building unneeded systems now would
## only give that boundary more to not touch. Recorded as a limitation in
## FRICTIONAL.md rather than left to look like an oversight.
##
## Scale: 16 px = 1 m, so this 28 px sprite is a 1.75 m adventurer.

signal health_changed(current: int, maximum: int)
signal died

const MAX_HEALTH := 5
const SPEED := 96.0           # 6 m/s
const JUMP_VELOCITY := -260.0
const GRAVITY := 900.0

var health := MAX_HEALTH


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	var direction := Input.get_axis("move_left", "move_right")
	if is_zero_approx(direction):
		velocity.x = move_toward(velocity.x, 0.0, SPEED)
	else:
		velocity.x = direction * SPEED

	move_and_slide()


func take_damage(amount: int) -> void:
	if health <= 0:
		return
	health = maxi(health - amount, 0)
	health_changed.emit(health, MAX_HEALTH)
	if health == 0:
		died.emit()
