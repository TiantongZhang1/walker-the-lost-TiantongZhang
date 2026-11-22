extends SceneTree
## Walkthrough capture driver for Assignment 8's film.
##
##   WALKER_TAKE=a godot --path godot --script res://tests/capture_walkthrough.gd \
##       --write-movie out/frame.png --fixed-fps 60 --disable-vsync
##
## Normally invoked through `scripts/render_takes.py`, which supplies the 4K
## override Movie Maker needs.
##
## **This is a different driver from `capture_animation.gd`, and the
## difference is the subject.** That one records three takes about the two
## clips: a cycle, a committing action, and the two revisions the author
## asked for. This one records a WALKTHROUGH -- every implemented feature of
## the game, each with its precondition, its input and its visible outcome,
## which is what `coverage.json` has to account for.
##
## **Every take is scripted input through the real input map.** Nothing is
## teleported, no state is written, no clip is seeked, no collision is
## disabled and no test-only shortcut is called. The one thing the driver
## does that a player cannot is read the player's position to decide when to
## press a key -- which the skill allows explicitly, and which is recorded in
## the input log so a reviewer can see every decision it made.
##
##   take a  THE ROOM AND THE STATES. Fall, settle, run both ways with the
##           cycle wrapping, jump, rise, fall, land. Four of the five states
##           entered by their own input, plus the floating key looping
##           behind all of it and the step dust under the feet.
##
##   take b  THE COMMITTING ACTION. Four standing swings, then the edge the
##           assignment names: an action requested DURING another action.
##           One attack in startup (ignored) and one in recovery (buffered,
##           and it plays), with the playhead logged on every frame so the
##           phase each press landed in is evidence rather than a claim.
##
##   take c  MOVING, AND JUMPING, THROUGH A SWING. Revisions 7.0.9 and
##           7.0.10: a swing that travels with its gait under it, and a
##           swing jumped out of that does not restart.
##
##   take d  THE HAZARD, AND FAILURE. The trap's warning, its strike, the
##           damage it does, and the fifth hit -- death, which is the fifth
##           state and the only one entered by a game condition rather than
##           a key. Recovery is not shown because THIS GAME HAS NONE: there
##           is no respawn, and `coverage.json` records that as a planned
##           feature with a reason rather than quietly omitting it.

const MAIN := "res://game/main.tscn"

var _log: Array[String] = []
var _t := 0.0
var _probe: Probe = null


func _init() -> void:
	var take := OS.get_environment("WALKER_TAKE")
	if take == "":
		take = "a"
	if not (take in ["a", "b", "c", "d"]):
		push_error("capture_walkthrough.gd knows takes a, b, c and d, not %s"
			% take)
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
		"a":
			await _take_states()
		"b":
			await _take_action()
		"c":
			await _take_moving()
		"d":
			await _take_hazard()

	_write_log(take)
	_verdict(take, main)


## ---------------------------------------------------------------- take a ---
## The room, and four states entered by their own input. It paces the clear
## 190 px west of the first trap, so the figure is undamaged throughout and
## the take is about the states rather than about the hazard.
## **The takes are LONG on purpose.** The first cut of this driver made
## each one a few seconds -- just the moment a feature happens -- and the
## beats built on it carried twenty to thirty seconds of frozen final frame
## apiece. The skill allows a labelled hold for extra narration time; it does
## not make a three-second action with a thirty-second hold into a
## walkthrough. A walkthrough's body should be mostly moving.
##
## So each take now runs about as long as the narration laid over it, with
## the player doing the same things repeatedly in the clear stretch west of
## the first trap. Repetition is the point: a cycle has to be seen wrapping
## several times before anyone can say whether it wraps cleanly.
func _take_states() -> void:
	await _hold(1.4)                      # FALLING, then IDLE
	await _hold(1.6)                      # idle, held, with nothing pressed
	await _leg(KEY_A, 0.9)                # RUN, west
	await _hold(0.6)
	await _leg(KEY_D, 1.7)                # east -- the mirrored gait
	await _hold(0.6)
	await _leg(KEY_A, 1.7)                # and back, several more wraps
	await _hold(0.6)
	await _leg(KEY_D, 1.7)
	await _hold(0.8)
	await _tap(KEY_SPACE)                 # RISING, then FALLING, then land
	await _hold(1.4)
	await _leg(KEY_A, 1.2)                # a running jump, both states again
	_key(KEY_A, true)
	await _tap(KEY_SPACE)
	await _hold(1.1)
	_key(KEY_A, false)
	await _hold(1.0)
	await _leg(KEY_D, 1.5)
	await _hold(0.7)
	await _leg(KEY_A, 1.5)
	await _hold(0.7)
	await _tap(KEY_SPACE)
	await _hold(1.3)
	await _leg(KEY_D, 1.4)
	await _hold(2.6)                      # idle again, and the key turning


## ---------------------------------------------------------------- take b ---
## **The edge the assignment names.** Two of these presses are the whole
## point and the probe logs the clip's playhead on every frame, so which
## phase each one landed in is read off the log rather than asserted from
## the driver's own timings.
func _take_action() -> void:
	await _hold(1.4)
	await _tap(KEY_J)                     # a clean swing, all 18 frames
	await _hold(1.6)
	await _tap(KEY_J)                     # and another, so the phases repeat
	await _hold(1.8)

	await _tap(KEY_J)                     # a second attack IN STARTUP
	await _hold(0.1)                      # 0.1 s < 0.2 s: startup
	await _tap(KEY_J)                     # -> ignored
	await _hold(2.2)

	await _tap(KEY_J)                     # again, so it is not a one-off
	await _hold(0.1)
	await _tap(KEY_J)                     # -> ignored again
	await _hold(2.4)

	await _tap(KEY_J)                     # now the press in RECOVERY
	await _hold(0.45)                     # 0.45 s > 0.3333 s
	await _tap(KEY_J)                     # -> buffered, and it plays
	await _hold(2.4)
	await _tap(KEY_J)                     # and once more, both swings seen
	await _hold(0.45)
	await _tap(KEY_J)
	await _hold(3.0)


## ---------------------------------------------------------------- take c ---
func _take_moving() -> void:
	await _hold(1.3)
	for code in [KEY_D, KEY_A]:           # a travelling swing each way
		_key(code, true)
		await _hold(0.8)
		await _tap(KEY_J)
		await _hold(1.0)
		_key(code, false)
		await _hold(1.1)

	await _tap(KEY_J)                     # a swing jumped out of, standing
	await _hold(0.15)
	await _tap(KEY_SPACE)
	await _hold(2.2)

	_key(KEY_D, true)                     # and one jumped out of, running
	await _hold(0.8)
	await _tap(KEY_J)
	await _hold(0.25)
	await _tap(KEY_SPACE)
	await _hold(1.6)
	_key(KEY_D, false)
	await _hold(2.0)

	await _tap(KEY_J)                     # one more travelling swing, west
	await _hold(0.1)
	_key(KEY_A, true)
	await _hold(1.4)
	_key(KEY_A, false)
	await _hold(2.4)


## ---------------------------------------------------------------- take d ---
## The hazard, and the only state a key cannot reach. Five crossings kill.
func _take_hazard() -> void:
	await _hold(1.6)
	# East across all three traps, then back, and back again. The player
	# takes a hit per crossing; the fifth is fatal. The pauses between legs
	# let each trap finish its cycle on screen rather than being walked past.
	await _leg(KEY_D, 1.5)
	await _hold(1.6)                      # trap 1: warning, strike, re-arm
	await _leg(KEY_D, 1.3)
	await _hold(1.6)                      # trap 2
	await _leg(KEY_D, 1.3)
	await _hold(1.8)                      # trap 3
	await _leg(KEY_A, 1.4)
	await _hold(1.6)
	await _leg(KEY_A, 1.4)
	await _hold(1.6)
	await _leg(KEY_D, 1.4)
	await _hold(1.6)
	await _leg(KEY_D, 1.4)
	await _hold(4.0)                      # the death pose holds, and holds


## -------------------------------------------------------------- plumbing ---
func _leg(code: Key, seconds: float) -> void:
	var left := seconds
	while left > 0.0:
		_key(code, true)                  # re-pressed every frame: Godot
		await process_frame               # releases held keys on focus loss
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


## Observes and records. It writes nothing: every field below is read off a
## node the game already owns, so the take stays play.
class Probe:
	extends Node
	var main: Node = null
	var owner_driver: SceneTree = null

	var rows := 0
	var states := {}                      # every clip that was current
	var swings := 0
	var wraps := 0
	var faced_left := false
	var faced_right := false
	var dust_ids := {}
	var window_opens := 0
	var key_bobbed := 0.0                 # the floating key's travel
	var key_turned := 0.0
	var min_health := 99
	var traps_fired := 0

	var _player: Node2D = null
	var _steps: Node = null
	var _anim: AnimationPlayer = null
	var _legs: AnimationPlayer = null
	var _hitbox: Area2D = null
	var _rig: Node2D = null
	var _key: Node2D = null
	var _key_spr: Sprite2D = null
	var _last_leg_pos := 0.0
	var _was_monitoring := false
	var _last_swing := -1
	var _key_y0 := INF
	var _key_r0 := INF

	func _ready() -> void:
		process_priority = 2000
		_player = main.get_node("Player")
		_steps = main.get_node("StepDustDriver")
		_anim = _player.get_node("AnimationPlayer")
		_legs = _player.get_node("LegAnim")
		_hitbox = _player.get_node("Hitbox")
		_rig = _player.get_node("Rig")
		_key = main.get_node_or_null("FloatingKey")
		if _key != null:
			_key_spr = _key.get_node_or_null("Sprite2D")
		for trap in main.get_node("Traps").get_children():
			trap.fired.connect(_on_fired)

	func _on_fired() -> void:
		traps_fired += 1

	func _process(_delta: float) -> void:
		rows += 1
		var clip := String(_anim.current_animation)
		if clip != "":
			states[clip] = true

		if _legs.current_animation == "legs_run":
			var pos := _legs.current_animation_position
			if pos < _last_leg_pos - 0.01:
				wraps += 1
			_last_leg_pos = pos
		else:
			_last_leg_pos = 0.0

		if _rig.scale.x < 0.0:
			faced_left = true
		else:
			faced_right = true

		for d in _steps.call(&"live_dust"):
			dust_ids[d.get_instance_id()] = true

		var monitoring: bool = _hitbox.monitoring
		if monitoring and not _was_monitoring:
			window_opens += 1
		_was_monitoring = monitoring

		var count: int = _player.get(&"swing_count")
		if count != _last_swing:
			if _last_swing >= 0 and count > 0:
				swings += 1
			_last_swing = count

		min_health = mini(min_health, _player.get(&"health"))

		# The simple animation, measured rather than assumed to be running.
		if _key_spr != null:
			if _key_y0 == INF:
				_key_y0 = _key_spr.position.y
				_key_r0 = _key_spr.rotation_degrees
			key_bobbed = maxf(key_bobbed, absf(_key_spr.position.y - _key_y0))
			key_turned = maxf(key_turned,
				absf(_key_spr.rotation_degrees - _key_r0))

		owner_driver.record(_player.global_position.x, clip,
			_anim.current_animation_position,
			String(_legs.current_animation), monitoring,
			_player.call(&"is_locked"), count,
			_player.call(&"is_on_floor"), _rig.scale.x,
			_player.get(&"health"),
			_key_spr.position.y if _key_spr != null else 0.0,
			_key_spr.rotation_degrees if _key_spr != null else 0.0)


func elapsed() -> float:
	return _t


func record(x: float, clip: String, pos: float, legs: String,
		monitoring: bool, locked: bool, count: int, on_floor: bool,
		facing: float, health: int, key_y: float, key_rot: float) -> void:
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
		"health": health,
		"key_y": snappedf(key_y, 0.001),
		"key_rot": snappedf(key_rot, 0.01),
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
	var player: Node2D = main.get_node("Player")
	print("  frames sampled      : %d" % _probe.rows)
	print("  clips seen          : %s"
		% ", ".join(PackedStringArray(_probe.states.keys())))
	print("  cycle wraps         : %d" % _probe.wraps)
	print("  facings             : right %s  left %s"
		% [_probe.faced_right, _probe.faced_left])
	print("  distinct dust puffs : %d" % _probe.dust_ids.size())
	print("  swings              : %d, window opened %d time(s)"
		% [_probe.swings, _probe.window_opens])
	print("  traps fired         : %d" % _probe.traps_fired)
	print("  health, lowest      : %d" % _probe.min_health)
	print("  floating key        : bobbed %.2f px, turned %.1f deg"
		% [_probe.key_bobbed, _probe.key_turned])

	# **The simple animation is asserted in EVERY take**, because it is the
	# one feature that needs nobody to do anything: if it ever stops looping
	# the whole room is wrong, and a take that did not check it would be the
	# place that silence hid.
	var key_ok := _probe.key_bobbed > 1.0 and _probe.key_turned > 20.0
	var ok := false
	var why := ""
	match take:
		"a":
			ok = _probe.states.has("idle") and _probe.states.has("run") \
				and _probe.states.has("rising") and _probe.states.has("falling") \
				and _probe.wraps >= 3 and _probe.faced_left and _probe.faced_right \
				and _probe.swings == 0
			why = "%d clips incl. idle/run/rising/falling, %d wraps, both facings" \
				% [_probe.states.size(), _probe.wraps]
		"b":
			# TEN attack presses, EIGHT swings. The two that are missing are
			# the two pressed inside a startup, and that difference IS the
			# edge the assignment names -- counted rather than described. The
			# four pressed inside a recovery are all there, because a
			# buffered attack is not a lost one.
			ok = _probe.swings == 8 and _probe.window_opens == 8
			why = "%d swings from 10 presses (2 ignored in startup), window opened %d times" \
				% [_probe.swings, _probe.window_opens]
		"c":
			ok = _probe.swings >= 2 and _probe.states.has("swing")
			why = "%d swings, travelling and jumped" % _probe.swings
		"d":
			ok = _probe.traps_fired >= 3 and _probe.min_health == 0 \
				and _probe.states.has("dead")
			why = "%d trap firings, health reached %d, `dead` played" \
				% [_probe.traps_fired, _probe.min_health]
	if not key_ok:
		ok = false
		why += "  -- BUT the floating key did not animate (bob %.2f, turn %.1f)" \
			% [_probe.key_bobbed, _probe.key_turned]
	if ok:
		print("CAPTURE OK  take %s: %s" % [take, why])
		quit(0)
	else:
		print("CAPTURE FAILED  take %s: %s" % [take, why])
		quit(1)
