extends Node
## The vsync toggle Assignment 6's "Use It" section asks for, and nothing else.
##
## **Why this exists.** `CHANGE-BRIEF.md` §7 answers that with vsync on, the
## frame rate reads the display's refresh rate with the effects off and the
## same with them on, because vsync holds it there until a frame actually
## misses. That is an argument. The assignment asks for it to be *shown*, and
## shown the right way: **turn vsync off for that comparison only, with a
## debug key rather than a project-setting change**, so the shipped game is
## never running under different settings than the one that was measured.
##
## **It does not touch the input map.** `CHANGE-BRIEF.md` §3 keeps the input
## map out of scope for this assignment and it stays out: this reads the raw
## keycode off the event, exactly as the assignment's own example does, and
## adds no action. An earlier version of this report claimed the vsync key
## could not be added without breaking that boundary. That was wrong, and the
## assignment's example is what showed it.
##
## **It writes no game state.** `DisplayServer`'s vsync mode is a property of
## the window, not of the game. Presentation reads game state and never writes
## it; this does not read any.
##
## F9 is not bound to anything this game uses, and `README.md` lists it under
## controls because the assignment requires the key to be named there.

const TOGGLE_KEY := KEY_F9


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey):
		return
	var key := event as InputEventKey
	if not key.pressed or key.echo or key.keycode != TOGGLE_KEY:
		return
	var disabled := DisplayServer.window_get_vsync_mode() \
		== DisplayServer.VSYNC_DISABLED
	DisplayServer.window_set_vsync_mode(
		DisplayServer.VSYNC_ENABLED if disabled else DisplayServer.VSYNC_DISABLED)
	# Printed rather than drawn: the number that matters is read in the
	# Visual Profiler, and an on-screen overlay would be one more thing in
	# the frame while the GPU time is being measured.
	print("[debug] vsync %s   FPS %d"
		% ["ON" if disabled else "OFF", Engine.get_frames_per_second()])


## For the state test: the mode the window is in right now.
func vsync_enabled() -> bool:
	return DisplayServer.window_get_vsync_mode() != DisplayServer.VSYNC_DISABLED
