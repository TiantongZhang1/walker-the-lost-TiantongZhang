extends Node2D
## Diagnostics only. Prints what the engine ACTUALLY initialised, so that
## "Forward+ works on this machine" is a recorded line of output rather than
## somebody's impression of the window.
##
## CHANGE-BRIEF.md section 0 owes this check: Forward+ was set on 2026-10-23
## and every run since has been headless, which uses a dummy renderer and
## proves nothing.

func _ready() -> void:
	# Headless loads this scene once per test scenario, and its answer is
	# worthless there anyway: the dummy renderer names a driver it never
	# initialised. Only a real run has anything to say.
	if DisplayServer.get_name() == "headless":
		return
	var method: String = ProjectSettings.get_setting(
		"rendering/renderer/rendering_method", "<unset>")
	print("--- renderer check ---")
	print("  project.godot asks for : ", method)
	print("  actually running       : ", RenderingServer.get_current_rendering_method())
	print("  driver                 : ", RenderingServer.get_current_rendering_driver_name())
	print("  adapter                : ", RenderingServer.get_video_adapter_name())
	print("  adapter vendor         : ", RenderingServer.get_video_adapter_vendor())
	print("  window size            : ", DisplayServer.window_get_size())
	print("----------------------")
