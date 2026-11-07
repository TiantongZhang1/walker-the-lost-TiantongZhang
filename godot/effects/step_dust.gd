extends Node2D
## Effect C's lifecycle, and nothing else.
##
## **No setting lives here.** `CLAUDE.md`'s Ownership rule puts the design in
## `step_dust.tscn`. `_lifetime` is read back from the scene rather than
## typed, so it cannot drift from the brief.
##
## **The one value a driver may set.** `fire()` takes an `amount_ratio`:
## `CHANGE-BRIEF.md` revision 6.0.4 section C.3 gives a stride 0.6 and a
## landing 1.0, because a landing displaces more dust than a stride. That is
## the feature §0.1 probed and the first two effects did not need — Effect B
## is ambience and §2.4 ruled it out, Effect A has nothing to scale.
##
## **This is deliberately the same shape as `hit_burst.gd` and is not shared
## with it.** Two one-shot effects is not enough to justify a base class; the
## indirection would cost more to read than the twenty lines it saves. If a
## fourth appears, extract it then, and say so here.

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


## The longest emitter's lifetime, read from the scene. C5 asserts that no
## instance survives past it.
func lifetime() -> float:
	return _lifetime


## `ratio` is section C.3's amount_ratio: 0.6 for a stride, 1.0 for a landing.
func fire(ratio := 1.0) -> void:
	for child in get_children():
		if child is GPUParticles2D:
			var p := child as GPUParticles2D
			p.amount_ratio = ratio
			p.emitting = true
	_firing = true
	_elapsed = 0.0
	set_process(true)


## C4, for the state test: which event made this instance.
func amount_ratio() -> float:
	for child in get_children():
		if child is GPUParticles2D:
			return (child as GPUParticles2D).amount_ratio
	return -1.0


## Seconds since `fire()`.
func elapsed() -> float:
	return _elapsed


func _process(delta: float) -> void:
	if not _firing:
		return
	_elapsed += delta
	if _elapsed >= _lifetime:
		queue_free()
