class_name SpikeTrap
extends Node2D

## A floor trap that announces itself before it fires.
##
## Specified in CHANGE-BRIEF.md. This script owns the game state only: it
## advances `warn_amount` and never touches a material. The driver that reads
## `warn_amount` and writes it into a shader uniform is a separate file, added
## after the shader exists, so that the commit history shows which came first.
##
## Rules this implements, by their numbers in the brief:
##   R1  warn_amount is 0.0 while ARMED, 0.0 at the first frame of WARNING,
##       and 1.0 at the instant FIRING begins.
##   R2  WARNING ramps 0 -> 1 linearly over WARN_SECONDS of game time, so the
##       window lasts the same at 30, 60 and 144 fps.
##   R3  Retrigger restarts: a fresh DetectArea entry while ARMED or WARNING
##       puts warn_amount back to 0.0 and begins a new window. While the trap
##       is busy (FIRING, RETRACTING, COOLDOWN) an entry does nothing.
##   R4  Ordinary scaled delta. The Lost sets Engine.time_scale nowhere.
##   R5  disarm() snaps warn_amount to 0.0 in the same frame, with no fade.
##   R6  Each instance owns its own state, so three traps warn independently.

signal warning_started
signal fired
signal player_hit

enum State { ARMED, WARNING, FIRING, RETRACTING, COOLDOWN }

## The warning window. 0.30 s per CHANGE-BRIEF.md revision 5.0.2, after the
## 0.45 s of revision 5.0.1 turned out to make the trap unable to hit a
## walking player at all.
##
## DetectArea's width in spike_trap.tscn is DERIVED from this number:
##
##     detect half-width = Player.SPEED * WARN_SECONDS - player half-width
##                       = 96 * 0.30 - 5  =  24 px        (48 px wide)
##
## so a player who keeps walking is centred over the trap when the spikes
## arrive. Change WARN_SECONDS and that shape has to change with it.
const WARN_SECONDS := 0.30
const FIRE_SECONDS := 0.18
const RETRACT_SECONDS := 0.22
const COOLDOWN_SECONDS := 0.60

## Firing is a texture swap, not a moving node, so the trap stays one
## Sprite2D with one material. See tools/make_sprites.py for why.
const TEX_ARMED := preload("res://assets/sprites/spike_trap.png")
const TEX_FIRED := preload("res://assets/sprites/spike_trap_fired.png")

## Read by the driver. Never written from outside this script.
var warn_amount := 0.0
var state := State.ARMED

var _elapsed := 0.0

@onready var _sprite: Sprite2D = $Sprite2D
## Only bodies standing on the trap itself are hurt. DetectArea is far wider,
## because it has to notice the player early enough for the warning to mean
## something; being seen is not the same as being hit.
@onready var _hurt_area: Area2D = $HurtArea


func _process(delta: float) -> void:
	_elapsed += delta
	match state:
		State.WARNING:
			# R2: by game time, not by frame count. clampf guards the frame
			# that overshoots the window.
			warn_amount = clampf(_elapsed / WARN_SECONDS, 0.0, 1.0)
			if _elapsed >= WARN_SECONDS:
				_enter(State.FIRING)
		State.FIRING:
			# R1: held at full through the strike. The spikes are out; the
			# trap is at its most dangerous, so it stays red.
			warn_amount = 1.0
			if _elapsed >= FIRE_SECONDS:
				_enter(State.RETRACTING)
		State.RETRACTING:
			if _elapsed >= RETRACT_SECONDS:
				_enter(State.COOLDOWN)
		State.COOLDOWN:
			if _elapsed >= COOLDOWN_SECONDS:
				_enter(State.ARMED)


func _enter(next: State) -> void:
	state = next
	_elapsed = 0.0
	match next:
		State.ARMED:
			warn_amount = 0.0
			_sprite.texture = TEX_ARMED
		State.WARNING:
			warn_amount = 0.0
			warning_started.emit()
		State.FIRING:
			warn_amount = 1.0
			_sprite.texture = TEX_FIRED
			fired.emit()
			for body in _hurt_area.get_overlapping_bodies():
				if body.has_method("take_damage"):
					body.take_damage(1)
					player_hit.emit()
		State.RETRACTING, State.COOLDOWN:
			warn_amount = 0.0
			if next == State.COOLDOWN:
				_sprite.texture = TEX_ARMED


## R5. Called when the trap must stop warning without firing.
func disarm() -> void:
	warn_amount = 0.0
	_elapsed = 0.0
	state = State.COOLDOWN
	_sprite.texture = TEX_ARMED


## Seconds of game time left in the current warning window, or -1.0 when the
## trap is not warning. The test reads this to check R3's restart.
func warning_remaining() -> float:
	if state != State.WARNING:
		return -1.0
	return maxf(WARN_SECONDS - _elapsed, 0.0)


func _on_detect_body_entered(_body: Node2D) -> void:
	# R3: restart from ARMED or WARNING. A busy trap ignores the entry;
	# re-arming mid-strike would let a player cancel a trap by touching it.
	if state == State.ARMED or state == State.WARNING:
		_enter(State.WARNING)
