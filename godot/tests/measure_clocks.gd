extends SceneTree
## Assignment 7 §8 — THE TWO CLOCKS, measured rather than asserted.
##
##   ./scripts/run-test.sh measure_clocks.gd 60
##
## `test_player_clips.gd` already asserts that `callback_mode_process` is
## PHYSICS. That is a check on a *setting*. This is the measurement the brief
## actually asks for: **run the same clip in both modes and report, in
## seconds, how far apart the two answers are.**
##
## The quantity is the one gameplay reads — the physics frame on which
## `Hitbox.monitoring` first comes back `true` when it is read on the physics
## tick, which is where `player.gd` and the physics server read it.
##
## `CHANGE-BRIEF.md` §8's prediction, written before this existed:
##
##   > at physics, the physics frame corresponding to 0.200 s; at idle, up to
##   > ONE PHYSICS STEP LATE — 1/60 s ≈ 0.0167 s — and jittering between runs
##   > because the render tick is not locked to the physics tick.
##
## **The second half of that prediction cannot be tested here, and this file
## says so rather than quietly reporting the first half.** `run-test.sh`
## passes `--fixed-fps`, which locks the render tick to the physics tick on
## purpose, so every run of this measurement is deterministic. The jitter is
## real and lives in a windowed run; what a fixed-fps run can establish is
## the *size* of the disagreement, not its variance. §9's split again: this
## file measures, and what it cannot see it names.

const MAIN := "res://game/main.tscn"
const PHYS := 60.0
const T_ACTIVE_OPEN := 0.2

var _checks := 0
var _failures := 0


func _check(label: String, ok: bool, detail := "") -> void:
	_checks += 1
	if not ok:
		_failures += 1
	print("PASS  " if ok else "FAIL  ", label,
		"" if detail == "" else "   [" + detail + "]")


func _note(label: String) -> void:
	print("NOTE  ", label)


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()


## One swing, with the mixer on `mode`. Returns the physics frame on which
## `Hitbox.monitoring` first reads `true` **from the physics tick**, counting
## the frame the attack was pressed as 0, or -1 if it never did.
func _first_open(mode: int) -> Array:
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await physics_frame
	var player: Player = main.get_node(^"Player")
	var ap: AnimationPlayer = player.get_node(^"AnimationPlayer")
	var hitbox: Area2D = player.get_node(^"Hitbox")

	# The one line under test.
	ap.callback_mode_process = mode

	var n := 0
	while (not player.is_on_floor() or player.is_locked()) and n < 200:
		await physics_frame
		n += 1
	for i in range(4):
		await physics_frame

	_key(KEY_J, true)
	await physics_frame
	_key(KEY_J, false)

	var opened := -1
	var head_at_open := -1.0
	var started := -1
	var head_at_start := -1.0
	var trace := ""
	for f in range(60):
		# read on the PHYSICS tick, which is where gameplay reads it
		if hitbox.monitoring and opened < 0:
			opened = f
			head_at_open = ap.current_animation_position
		if started < 0 and ap.current_animation == "swing":
			started = f
			head_at_start = ap.current_animation_position
		if f <= 16:
			trace += "    f%-3d playhead %.4f  monitoring %s
" % [
				f, ap.current_animation_position, str(hitbox.monitoring)]
		await physics_frame
	print("  trace around the boundary, mode %d:" % mode)
	print(trace)
	main.queue_free()
	await physics_frame
	return [opened, head_at_open, started, head_at_start]


func _init() -> void:
	await physics_frame
	var want := int(roundf(T_ACTIVE_OPEN * PHYS))

	var phys := await _first_open(
		AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS)
	var idle := await _first_open(
		AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE)

	print("")
	print("  mode                    clip starts   window opens   playhead there")
	print("  PHYSICS (what ships)        f%-3d          f%-3d           %.4f"
		% [phys[2], phys[0], phys[1]])
	print("  IDLE (engine default)       f%-3d          f%-3d           %.4f"
		% [idle[2], idle[0], idle[1]])
	print("")
	print("  playhead on the frame `swing` becomes current:")
	print("    PHYSICS  %.4f      IDLE  %.4f   <- the whole difference"
		% [phys[3], idle[3]])
	print("  frames from THAT frame to the window opening:")
	print("    PHYSICS  %d            IDLE  %d        (key at %.3f s = %d frames)"
		% [phys[0] - phys[2], idle[0] - idle[2], T_ACTIVE_OPEN, want])
	print("")

	# --- what the brief asked for ----------------------------------------
	_check("PHYSICS: the window opens on the frame the playhead reads "
		+ "%.4f -- writer and reader share a tick, so the disagreement "
			% T_ACTIVE_OPEN + "is ZERO",
		absf(phys[1] - T_ACTIVE_OPEN) < 0.0005, "%.4f" % phys[1])
	_check("IDLE: it opens on the frame its playhead reads %.4f TOO"
			% T_ACTIVE_OPEN,
		absf(idle[1] - T_ACTIVE_OPEN) < 0.0005, "%.4f" % idle[1])
	# **Where the one frame actually goes.** Both modes make `swing` the
	# current animation on the same physics frame. The difference is the
	# playhead ON that frame: the physics-mode mixer ran its advance earlier
	# in that same physics step, before `player_anim.gd` called `play()`, so
	# it is still at 0. The idle-mode mixer advances in the frame's IDLE
	# step, which comes after every `_physics_process`, so it has already
	# taken one step by the time this reads it.
	_check("on the frame `swing` becomes current, the PHYSICS clip is at "
		+ "0.0000", absf(phys[3]) < 0.0005, "%.4f" % phys[3])
	_check("and the IDLE clip is already one step in, at %.4f" % (1.0 / PHYS),
		absf(idle[3] - 1.0 / PHYS) < 0.0005, "%.4f" % idle[3])
	_check("but the two clips are offset by exactly one physics step",
		phys[0] - idle[0] == 1, "%d frames" % (phys[0] - idle[0]))

	print("")
	print("  WHAT THIS MEASURES, AND WHERE CHANGE-BRIEF.md SECTION 8 WAS WRONG")
	print("")
	print("  Section 8 predicted the idle figure would be UP TO ONE PHYSICS")
	print("  STEP LATE. Measured, it is one physics step EARLY, and the cause")
	print("  is not read latency at all. An idle-mode mixer gets an extra")
	print("  advance during the idle step of the frame the clip STARTS -- a")
	print("  step the physics-mode mixer does not get until the next frame.")
	print("  So the idle clip runs one step ahead of the physics clip for the")
	print("  whole of its length.")
	print("")
	print("  Section 8's actual CLAIM survives, and is what the first two")
	print("  checks establish: the window opens on the frame the playhead")
	print("  reaches 0.2000, in both modes. Writer and reader share a tick.")
	print("  The disagreement between the clip's write and gameplay's read")
	print("  is ZERO SECONDS, which is what shipping on physics buys.")
	print("")

	_note("WHAT THIS RUN CANNOT SEE. `--fixed-fps` locks the render tick to "
		+ "the physics tick, so the idle step always falls between the same")
	_note("two physics steps and every run of this file is identical. "
		+ "Section 8 also predicts the idle figure JITTERS between runs, and")
	_note("THAT is where idle's real unreliability lives: at a free frame "
		+ "rate the idle step wanders. It needs a windowed run and is NOT")
	_note("established here. The SIZE of the offset is measured; its "
		+ "VARIANCE is not. Running this three times under a locked clock")
	_note("would be one measurement repeated, not three measurements.")

	print("")
	print("%d checks, %d failures" % [_checks, _failures])
	quit(0 if _failures == 0 else 1)
