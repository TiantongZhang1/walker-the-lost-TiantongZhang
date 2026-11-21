extends SceneTree
## Capture driver for Assignment 7's film. Three takes, each recorded from the
## running game at 3840 x 2160 through Godot's Movie Maker.
##
##   WALKER_TAKE=c godot --path godot --script res://tests/capture_animation.gd \
##       --write-movie out/frame.png --fixed-fps 60 --disable-vsync
##
## Normally invoked through `scripts/render_takes.py`, which also supplies the
## 4K override Movie Maker needs.
##
## **EVERY TAKE IS PLAYED.** Assignment 6's film needed one scripted take,
## because three bursts alive at once cannot be produced by walking the room.
## Nothing in Assignment 7 is like that: a clip plays because the player
## pressed a key, and all three takes here are held keys parsed through the
## real input map. Nothing is teleported, no clip is seeked, no state is
## written. If a take cannot be produced by playing, it is not in this film.
##
## **take c - THE CYCLE.** Walk the length of the room and back. The cycle
## wraps many times in both facings, and Effect C's dust lands under the
## planted foot because the two share a clock (`CHANGE-BRIEF.md` revision
## 7.0.7 section 5). Asserts wraps, facings, puffs, and that no swing happened.
##
## **take s - THE COMMITTING ACTION.** Standing, four swings with gaps. The
## three phases, the hitbox window opening and closing on the clip's own
## timeline, and the clip running to its own end every time. Asserts that
## every swing was 0.600 s and that the window opened exactly once inside it.
##
## **take m - WHAT THE AUTHOR ASKED FOR.** The two revisions that came from
## playing: a swing held through a direction (7.0.9, the legs keep their gait)
## and a swing jumped out of (7.0.10, the clip does not notice). Asserts a
## travelling swing with `legs_run` under it, and a swing that left the floor
## without `swing_count` moving.
##
## Every take asserts its own outcome and prints CAPTURE OK only if it holds.
## A completed render is not the claim; that line is.

const MAIN := "res://game/main.tscn"

var _log: Array[String] = []
var _t := 0.0
var _probe: Probe = null


func _init() -> void:
	var take := OS.get_environment("WALKER_TAKE")
	if take == "":
		take = "c"
	if not (take in ["c", "s", "m"]):
		push_error("capture_animation.gd knows takes c, s and m, not %s" % take)
		quit(2)
		return

	var main: Node = (load(MAIN) as PackedScene).instantiate()
	root.add_child(main)
	await process_frame

	_probe = Probe.new()
	_probe.main = main
	_probe.owner_driver = self
	root.add_child(_probe)
	await process_frame

	match take:
		"c":
			await _take_cycle()
		"s":
			await _take_swing()
		"m":
			await _take_moving()

	_write_log(take)
	_verdict(take, main)


## ---------------------------------------------------------------- take c ---
## The room's own geometry supplies the legs. The player starts at x 96, the
## left wall is at −8 and the first trap is at 208, so there is a **clear
## 190 px stretch** west of it; at SPEED 96 px/s that is two seconds each way.
##
## **This take never crosses a trap, and that is a decision rather than an
## accident.** The first version walked the length of the room and back and
## the player arrived dead: five hits kill, and six traps are crossed. A take
## about the gait that ends in the death pose is a take about two things, and
## the one it is about is the one nobody can check afterwards.
##
## **It walks both ways, and that is not padding.** `Rig.scale.x` is the
## facing and it mirrors the two cut-out legs together; a cycle that only ever
## ran one way would never show that the mirrored gait still alternates.
func _take_cycle() -> void:
	await _hold(1.0)                      # fall to the floor and settle
	await _leg(KEY_A, 0.8)                # west to x ~19, clear of the wall
	await _hold(0.4)
	await _leg(KEY_D, 1.7)                # east to x ~182, short of trap 1
	await _hold(0.4)
	await _leg(KEY_A, 1.6)                # west again, the mirrored gait
	await _hold(0.4)
	await _leg(KEY_D, 1.5)
	await _hold(1.0)                      # the last puffs finish their lives


## ---------------------------------------------------------------- take s ---
## Four swings, standing still, with a gap between them. The gap is 0.5 s,
## longer than the 0.3333 s recovery, so nothing here is a buffered swing --
## each one is a fresh press, which is what the phases are read against.
func _take_swing() -> void:
	await _hold(1.0)
	for i in range(4):
		await _tap(KEY_J)
		await _hold(1.1)                  # 0.600 clip + 0.5 clear


## ---------------------------------------------------------------- take m ---
## The two things the author asked for after playing, in the order they asked.
##
## First a swing with a direction held through it, which is what revision
## 7.0.9 fixed -- the legs keep their gait because `LegAnim` owns them and
## never hears about the sword. Then a swing jumped out of, revision 7.0.10,
## where the clip's clock does not move at all.
func _take_moving() -> void:
	await _hold(1.0)

	# --- a travelling swing, twice, east then west ------------------------
	for code in [KEY_D, KEY_A]:
		_key(code, true)
		await _hold(0.7)                  # get up to speed and into the gait
		await _tap(KEY_J)
		await _hold(0.9)                  # the whole clip, still travelling
		_key(code, false)
		await _hold(0.6)

	# --- a jumped swing, from standing and then while running -------------
	await _tap(KEY_J)
	await _hold(0.15)                     # mid-startup
	await _tap(KEY_SPACE)
	await _hold(1.4)                      # the clip ends in the air, then land

	_key(KEY_D, true)
	await _hold(0.7)
	await _tap(KEY_J)
	await _hold(0.25)                     # inside the active window
	await _tap(KEY_SPACE)
	await _hold(1.0)
	_key(KEY_D, false)
	await _hold(1.2)


## -------------------------------------------------------------- plumbing ---
func _leg(code: Key, seconds: float) -> void:
	var left := seconds
	# The key is re-pressed EVERY frame. Godot releases every held key when
	# the window loses focus, and a 4K take needs a real window for minutes --
	# A6's BUILD-PROMPT records a take that came back with a sixth of the
	# events it should have had because the author switched applications.
	while left > 0.0:
		_key(code, true)
		await process_frame
		var d := root.get_process_delta_time()
		left -= d
		_t += d
	_key(code, false)


func _hold(seconds: float) -> void:
	var left := seconds
	while left > 0.0:
		await process_frame
		var d := root.get_process_delta_time()
		left -= d
		_t += d


func _tap(code: Key) -> void:
	_key(code, true)
	await process_frame
	_t += root.get_process_delta_time()
	_key(code, false)


func _key(code: Key, pressed: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.pressed = pressed
	Input.parse_input_event(e)
	Input.flush_buffered_events()


## Samples once per frame after everything else, at priority 2000, so what it
## reads is this frame's finished state rather than a half-written one.
##
## **It writes nothing.** Every field below is derived from nodes the game
## already owns; the probe is an observer and the take is still play.
class Probe:
	extends Node
	var main: Node = null
	var owner_driver: SceneTree = null

	var rows := 0
	var swings := 0                       # distinct swings, by swing_count
	var wraps := 0                        # times legs_run's playhead went back
	var faced_right := false
	var faced_left := false
	var dust_ids := {}
	var window_opens := 0
	var jumped_swings := 0                # left the floor inside one swing
	var travelling_swing_frames := 0      # |vx| >= 90 with legs_run under it
	var swing_frames: Array[int] = []     # length of each swing, in frames

	var _player: Node2D = null
	var _steps: Node = null
	var _anim: AnimationPlayer = null
	var _legs: AnimationPlayer = null
	var _hitbox: Area2D = null
	var _rig: Node2D = null
	var _last_swing := -1
	var _last_leg_pos := 0.0
	var _was_monitoring := false
	var _this_swing_frames := 0
	var _this_swing_left_floor := false

	func _ready() -> void:
		process_priority = 2000
		_player = main.get_node("Player")
		_steps = main.get_node("StepDustDriver")
		_anim = _player.get_node("AnimationPlayer")
		_legs = _player.get_node("LegAnim")
		_hitbox = _player.get_node("Hitbox")
		_rig = _player.get_node("Rig")

	func _process(_delta: float) -> void:
		rows += 1

		# --- the cycle, and its wraps ------------------------------------
		if _legs.current_animation == "legs_run":
			var pos := _legs.current_animation_position
			if pos < _last_leg_pos - 0.01:
				wraps += 1
			_last_leg_pos = pos
		else:
			_last_leg_pos = 0.0

		# --- the facing, which mirrors both legs together -----------------
		if _rig.scale.x < 0.0:
			faced_left = true
		else:
			faced_right = true

		# --- Effect C, sharing the cycle's clock --------------------------
		for d in _steps.call(&"live_dust"):
			dust_ids[d.get_instance_id()] = true

		# --- the window, counted as EDGES rather than frames --------------
		var monitoring: bool = _hitbox.monitoring
		if monitoring and not _was_monitoring:
			window_opens += 1
		_was_monitoring = monitoring

		# --- one swing at a time ------------------------------------------
		var count: int = _player.get(&"swing_count")
		var locked: bool = _player.call(&"is_locked")
		if count != _last_swing:
			# **`_this_swing_frames > 0` is not a tidy-up, it is a correction.**
			# The first version appended a ZERO-length swing, because the
			# probe's first frame sets `_last_swing` to 0 and the first real
			# swing then takes the `count != _last_swing` edge with nothing
			# counted yet. The take failed on `shortest == 0` while every
			# real swing was exactly 36 frames -- an assertion red on the
			# instrument's own bookkeeping rather than on the game.
			if _last_swing >= 0 and _this_swing_frames > 0:
				swing_frames.append(_this_swing_frames)
				if _this_swing_left_floor:
					jumped_swings += 1
			_last_swing = count
			_this_swing_frames = 0
			_this_swing_left_floor = false
			if count > 0:
				swings += 1
		if locked:
			_this_swing_frames += 1
			if not _player.call(&"is_on_floor"):
				_this_swing_left_floor = true
			if absf(_player.velocity.x) >= 90.0 \
					and _legs.current_animation == "legs_run":
				travelling_swing_frames += 1

		owner_driver.record(_player.global_position.x,
			String(_anim.current_animation),
			_anim.current_animation_position,
			String(_legs.current_animation),
			monitoring, locked, _player.get(&"swing_count"),
			_player.call(&"is_on_floor"), _rig.scale.x)

	## The last swing never reaches the `count != _last_swing` edge, so it is
	## closed here. A take whose final swing was the interesting one would
	## otherwise be invisible to its own assertions.
	func close() -> void:
		if _last_swing >= 0 and _this_swing_frames > 0:
			swing_frames.append(_this_swing_frames)
			if _this_swing_left_floor:
				jumped_swings += 1
			_this_swing_frames = 0


func elapsed() -> float:
	return _t


func record(x: float, clip: String, pos: float, legs: String,
		monitoring: bool, locked: bool, count: int, on_floor: bool,
		facing: float) -> void:
	_log.append(JSON.stringify({
		"t": snappedf(_t, 0.0001),
		"player_x": snappedf(x, 0.01),
		"clip": clip,
		"clip_t": snappedf(pos, 0.0001),
		"legs": legs,
		"monitoring": monitoring,
		"locked": locked,
		"swing_count": count,
		"on_floor": on_floor,
		"facing": facing,
	}))


func _write_log(take: String) -> void:
	var dir := OS.get_environment("WALKER_LOG_DIR")
	if dir == "":
		return
	DirAccess.make_dir_recursive_absolute(dir)
	var path := dir.path_join("take-%s-inputs.jsonl" % take)
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("could not write the take log to " + dir)
		return
	f.store_string("\n".join(_log) + "\n")
	f.close()
	print("  log: %s  (%d frames)" % [path, _log.size()])


func _verdict(take: String, main: Node) -> void:
	_probe.close()
	var player: Node2D = main.get_node("Player")
	var shortest := 9999
	var longest := 0
	for n in _probe.swing_frames:
		shortest = mini(shortest, n)
		longest = maxi(longest, n)
	print("  frames sampled      : %d" % _probe.rows)
	print("  cycle wraps         : %d" % _probe.wraps)
	print("  facings seen        : right %s  left %s"
		% [_probe.faced_right, _probe.faced_left])
	print("  distinct dust puffs : %d" % _probe.dust_ids.size())
	print("  swings              : %d, lengths %s frames"
		% [_probe.swings, str(_probe.swing_frames)])
	print("  window opened       : %d times" % _probe.window_opens)
	print("  travelling-swing fr : %d" % _probe.travelling_swing_frames)
	print("  swings that jumped  : %d" % _probe.jumped_swings)
	print("  health              : %d" % player.health)

	var ok := false
	var why := ""
	match take:
		"c":
			# The cycle, in both facings, with the dust that shares its clock,
			# and NO swing -- a take about the cycle that also swings is a
			# take about two things.
			ok = _probe.wraps >= 5 and _probe.faced_right and _probe.faced_left \
				and _probe.dust_ids.size() >= 12 and _probe.swings == 0
			why = "%d wraps, both facings, %d puffs, no swing" \
				% [_probe.wraps, _probe.dust_ids.size()]
		"s":
			# Four fresh swings, each the clip's own full length. 36 physics
			# frames at 60; the probe runs on the idle tick, so the count is
			# compared with a frame of slack either way rather than to 36.
			ok = _probe.swings == 4 and _probe.window_opens == 4 \
				and shortest >= 34 and longest <= 38
			why = "%d swings, window opened %d times, lengths %d..%d frames" \
				% [_probe.swings, _probe.window_opens, shortest, longest]
		"m":
			# Both of the author's last two requests, in one take: a swing
			# that travelled with the gait under it, and a swing that left
			# the floor without starting a new one.
			ok = _probe.travelling_swing_frames >= 30 \
				and _probe.jumped_swings >= 2 \
				and _probe.swings >= 4 and shortest >= 34 and longest <= 38
			why = "%d frames of travelling swing with legs_run, %d jumped swings, lengths %d..%d" \
				% [_probe.travelling_swing_frames, _probe.jumped_swings,
					shortest, longest]
	if ok:
		print("CAPTURE OK  take %s: %s" % [take, why])
		quit(0)
	else:
		print("CAPTURE FAILED  take %s: %s" % [take, why])
		quit(1)
