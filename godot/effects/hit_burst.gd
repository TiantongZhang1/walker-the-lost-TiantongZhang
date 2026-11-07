extends Node2D
## Effect A's lifecycle, and nothing else.
##
## **No setting lives here.** `CLAUDE.md`'s Ownership rule puts the design in
## `hit_burst.tscn`, and this script never writes one: it turns the three
## emitters on, and it frees the instance when the longest of them is done.
## `LIFETIME` below is read back from the scene rather than typed, so it
## cannot drift from the brief.
##
## **Why an instance per event.** `CHANGE-BRIEF.md` section 1.4, rule A3:
## setting `emitting = true` on a `one_shot` node that is still emitting does
## not restart it, so a single reused node silently drops the second of two
## close events. Three traps in one room makes that ordinary play, not an
## edge case. Every `fired` gets its own instance, which cannot drop one.

## A1: it must not emit on scene load. The scene already ships with
## `emitting = false` on all three; this is the belt to that braces.
var _firing := false
var _elapsed := 0.0
var _lifetime := 0.0


func _ready() -> void:
	for child in get_children():
		if child is GPUParticles2D:
			var p := child as GPUParticles2D
			p.emitting = false
			_lifetime = maxf(_lifetime, p.lifetime)
	set_process(false)


## The longest emitter's lifetime, read from the scene. A6 asserts that no
## instance survives past it.
func lifetime() -> float:
	return _lifetime


func fire() -> void:
	for child in get_children():
		if child is GPUParticles2D:
			(child as GPUParticles2D).emitting = true
	_firing = true
	_elapsed = 0.0
	set_process(true)


func _process(delta: float) -> void:
	if not _firing:
		return
	_elapsed += delta
	if _elapsed >= _lifetime:
		queue_free()
