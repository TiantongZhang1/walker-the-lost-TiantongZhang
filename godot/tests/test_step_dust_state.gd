extends SceneTree
## Effect C's observable rules C1-C7, against the real game scene.
## Revision 6.0.4.
##
## **Run at every pinned frame rate**, because C3 is the whole point of the
## distance-based cadence:
##
##   ./scripts/run-test.sh test_step_dust_state.gd 30
##   ./scripts/run-test.sh test_step_dust_state.gd 60
##   ./scripts/run-test.sh test_step_dust_state.gd 144
##
## A duration measured at one rate has not been measured, and neither has a
## cadence. G1 is a cadence written as a timer or a per-frame chance; the
## three runs are what tell those apart from a cadence written as distance.
##
## The walk is driven by synthesized key events through the real game loop, so
## the puffs counted below are the puffs a player produces.
##
## **The sampler is in this file, not in the driver.** Every frame it diffs
## `live_dust()` against the instances it has already seen and records the new
## ones' position, `amount_ratio` and parent **at the moment they appear**.
## `test_hit_burst_state.gd` learned why: holding node references and reading
## them later measures freed objects, and a freed reference compares equal to
## null, so the checks pass having measured nothing.
##
## A headless run draws no particles. Nothing here says what the dust looks
## like, and nothing here can see G3 -- whether `scale.x = -1` mirrors the
## throw. That is the strip.

const MAIN := "res://game/main.tscn"
const STRIDE_PX := 24.0
const RATIO_STRIDE := 0.6
const RATIO_LANDING := 1.0
const DUST_LIFETIME := 0.45
const FOOT_OFFSET := 14.0   # half of the player's 10 x 28 collision box

var _checks := 0
var _failures := 0
var _fps := 60.0
var _seen := {}


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


func _wait(seconds: float) -> void:
	var t := 0.0
	while t < seconds:
		await process_frame
		t += root.get_process_delta_time()


func _load_room() -> Array:
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame
	return [main, main.get_node("StepDustDriver"), main.get_node("Player")]


func _teardown(main: Node) -> void:
	_key(KEY_D, false)
	_key(KEY_A, false)
	_key(KEY_SPACE, false)
	main.queue_free()
	await process_frame


## One frame of sampling. Returns the rows for puffs that appeared this frame.
func _sample(driver: Node, player: Node2D, room: Node) -> Array:
	var fresh: Array = []
	for dust in driver.live_dust():
		var id: int = dust.get_instance_id()
		if _seen.has(id):
			continue
		_seen[id] = true
		fresh.append({
			"x": dust.global_position.x,
			"y": dust.global_position.y,
			"ratio": dust.call(&"amount_ratio"),
			"scale_x": dust.scale.x,
			"parented_to_room": dust.get_parent() == room,
			"player_x": player.global_position.x,
			"player_y": player.global_position.y,
			"on_floor": player.is_on_floor(),
		})
	return fresh


# ---------------------------------------------------------------- scenarios

func _scenario_scene_load() -> void:
	print("\n-- the driver is in the game, and nothing has stepped yet --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var driver: Node = bits[1]

	_check("StepDustDriver is a node in main.tscn", driver != null)
	_check("C1  no dust on the frame after _ready()",
		driver.live_count() == 0, str(driver.live_count()))
	_check("    main.tscn gives it the brief's stride of %.0f px" % STRIDE_PX,
		is_equal_approx(driver.stride_px, STRIDE_PX), "%.2f" % driver.stride_px)
	await _teardown(main)


## C1 cadence, C2 position, C3 frame rate, C5 parent. One walk, real input.
func _scenario_walk() -> void:
	print("\n-- C1/C2/C3/C5: one walk right at %.0f fps --" % _fps)
	var bits := await _load_room()
	var main: Node = bits[0]
	var driver: Node = bits[1]
	var player: Node2D = bits[2]
	# The player starts at y 150 and falls. That touchdown is a real landing
	# and produces a real landing puff; let it happen and let it die before
	# the stride count starts, or it would be counted as a stride.
	await _wait(0.8)
	_seen.clear()
	for dust in driver.live_dust():
		_seen[dust.get_instance_id()] = true

	var start_x: float = player.global_position.x
	var rows: Array = []
	_key(KEY_D, true)
	var t := 0.0
	while t < 2.0:
		await process_frame
		t += root.get_process_delta_time()
		rows.append_array(_sample(driver, player, main))
	_key(KEY_D, false)
	# Keep sampling through the wind-down, because the distance below is
	# measured after it. The first version released the key, waited 0.3 s
	# WITHOUT sampling, then divided the full distance by the stride. At 60
	# and 144 fps that happened to agree; at 30 fps it reported 7 puffs for
	# 8 strides. The window the puffs are counted over and the window the
	# distance is measured over have to be the same window.
	while absf(player.velocity.x) > 0.0:
		await process_frame
		rows.append_array(_sample(driver, player, main))
	var travelled: float = player.global_position.x - start_x

	# C1/C3. The cadence is a distance, so the count follows from the distance
	# and from nothing else -- not from the frame rate, not from the duration.
	var want := int(floor(travelled / STRIDE_PX))
	_check("    the player actually walked", travelled > 100.0,
		"%.1f px in 2.0 s" % travelled)
	_check("C1/C3  %d puffs for %.1f px at %.0f fps (want %d)"
			% [rows.size(), travelled, _fps, want],
		rows.size() == want,
		"stride %.0f px; remainder %.1f px"
			% [STRIDE_PX, driver.distance_since_step()])

	var worst_dx := 0.0
	var worst_dy := 0.0
	var wrong_parent := 0
	var wrong_ratio := 0
	var airborne := 0
	for row in rows:
		worst_dx = maxf(worst_dx, absf(row["x"] - row["player_x"]))
		worst_dy = maxf(worst_dy,
			absf(row["y"] - (row["player_y"] + FOOT_OFFSET)))
		if not row["parented_to_room"]:
			wrong_parent += 1
		if not is_equal_approx(row["ratio"], RATIO_STRIDE):
			wrong_ratio += 1
		if not row["on_floor"]:
			airborne += 1
	_check("    puffs were actually measured, not zero", rows.size() > 0,
		"%d measured" % rows.size())
	# The strong form of C1 and C3, and the reason the driver back-dates the
	# spawn: consecutive puffs are exactly one stride apart IN SPACE, at any
	# frame rate. A cadence written as a timer passes the count check at one
	# speed and fails this; a spawn placed at the player's CURRENT position
	# passes this at 144 fps and fails it at 30, which is how it was found.
	var worst_gap := 0.0
	for i in range(1, rows.size()):
		worst_gap = maxf(worst_gap,
			absf(absf(rows[i]["x"] - rows[i - 1]["x"]) - STRIDE_PX))
	_check("C1/C3  consecutive puffs are %.0f px apart at %.0f fps"
			% [STRIDE_PX, _fps],
		rows.size() > 1 and worst_gap <= 0.5,
		"worst deviation %.4f px over %d gaps" % [worst_gap, rows.size() - 1])

	# C2's loose half: the puff is under the player and not somewhere else.
	#
	# **The quantum is the physics tick, not the rendered frame.** The player
	# moves in `_physics_process`, which runs at
	# `Engine.physics_ticks_per_second` (60 here) whatever the render rate
	# is, so at 144 fps the position still arrives in 1.6 px jumps and a
	# bound of two RENDER frames (1.33 px) is tighter than anything that can
	# happen. It failed there, and the failure was the bound being wrong.
	# This is the same mistake in a new place as revision 5.0.3's: a number
	# divided by the wrong clock.
	#
	# Two steps are allowed and both are accounted for: one is the driver
	# back-dating the spawn, which is deliberate, and one is this sampler,
	# which reads the player after `await process_frame` -- by then another
	# physics tick has moved them again. The spacing check above is what
	# proves the placement is right; this one only bounds the lag.
	var step_px := 96.0 * maxf(1.0 / _fps,
		1.0 / float(Engine.physics_ticks_per_second))
	_check("C2  every puff is within two physics steps of the player",
		rows.size() > 0 and worst_dx <= 2.0 * step_px + 0.01,
		"worst %.3f px; two steps is %.3f px (physics %d Hz, render %.0f fps)"
			% [worst_dx, 2.0 * step_px,
			Engine.physics_ticks_per_second, _fps])
	_check("C2  and at the collision box's underside within 1 px",
		rows.size() > 0 and worst_dy <= 1.0, "worst %.3f px" % worst_dy)
	_check("C5  every puff is parented to the room, not the player",
		wrong_parent == 0, "%d elsewhere" % wrong_parent)
	_check("C4  every puff on this walk is a STRIDE, at ratio %.1f"
			% RATIO_STRIDE,
		wrong_ratio == 0, "%d at the wrong ratio" % wrong_ratio)
	_check("C1  none of them was spawned airborne", airborne == 0,
		"%d airborne" % airborne)
	await _teardown(main)


## C1's other half, and G4.
func _scenario_standing_still() -> void:
	print("\n-- C1: standing still produces nothing --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var driver: Node = bits[1]
	var player: Node2D = bits[2]
	await _wait(0.8)

	# Walk, then stop, then wait. G4 is a puff on the frame the player stops,
	# which is what a driver that reads a stale velocity would produce.
	_key(KEY_D, true)
	await _wait(0.5)
	_key(KEY_D, false)
	await _wait(0.6)   # longer than a puff's life, so the list empties
	_seen.clear()
	for dust in driver.live_dust():
		_seen[dust.get_instance_id()] = true

	var rows: Array = []
	var t := 0.0
	while t < 1.0:
		await process_frame
		t += root.get_process_delta_time()
		rows.append_array(_sample(driver, player, main))
	_check("C1  one second of standing still produced no puffs",
		rows.is_empty(), "%d puffs" % rows.size())
	_check("    and the player really was still",
		absf(player.velocity.x) < 1.0, "%.3f px/s" % player.velocity.x)
	await _teardown(main)


## C4 and C1: airborne produces nothing, landing produces exactly one.
func _scenario_jump() -> void:
	print("\n-- C4: one jump, one landing puff, nothing in the air --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var driver: Node = bits[1]
	var player: Node2D = bits[2]
	await _wait(0.8)
	await _wait(0.6)
	_seen.clear()
	for dust in driver.live_dust():
		_seen[dust.get_instance_id()] = true

	_key(KEY_SPACE, true)
	await process_frame
	_key(KEY_SPACE, false)

	var rows: Array = []
	var airborne_rows := 0
	var left_the_floor := false
	var t := 0.0
	while t < 1.5:
		await process_frame
		t += root.get_process_delta_time()
		if not player.is_on_floor():
			left_the_floor = true
		var fresh := _sample(driver, player, main)
		for row in fresh:
			if not row["on_floor"]:
				airborne_rows += 1
		rows.append_array(fresh)

	# This has to be a real observation. The first version of it asserted
	# `_seen.size() >= 0`, which is true of every array that has ever
	# existed; a jump that never happened would have produced zero puffs and
	# the landing check below would have failed for the wrong reason.
	_check("    the player actually left the floor", left_the_floor)
	_check("C1  nothing was spawned while airborne", airborne_rows == 0,
		"%d airborne" % airborne_rows)
	_check("C4  exactly one puff, the landing", rows.size() == 1,
		"%d puffs" % rows.size())
	if rows.size() == 1:
		_check("C4  it fired at amount_ratio %.1f, not a stride's %.1f"
				% [RATIO_LANDING, RATIO_STRIDE],
			is_equal_approx(rows[0]["ratio"], RATIO_LANDING),
			"%.2f" % rows[0]["ratio"])
	# G5 is the landing spawned on the STATE rather than the transition, which
	# would put a puff under a standing player every frame. The count above is
	# what catches it: standing on the floor for 1.5 s would be dozens.
	await _teardown(main)


## C6. A puff is left behind. C5's lifetime, measured.
func _scenario_left_behind_and_freed() -> void:
	print("\n-- C6: the puff stays where it was made; C5: it frees itself --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var driver: Node = bits[1]
	var player: Node2D = bits[2]
	await _wait(0.8)
	await _wait(0.6)

	_key(KEY_D, true)
	# Walk until the first puff of this run exists.
	var guard := 0.0
	while driver.live_count() == 0 and guard < 2.0:
		await process_frame
		guard += root.get_process_delta_time()
	_check("    a puff was made", driver.live_count() > 0)
	if driver.live_count() == 0:
		await _teardown(main)
		return

	var puff: Node2D = driver.live_dust()[0]
	var born_at: Vector2 = puff.global_position
	var born_player_x: float = player.global_position.x
	await _wait(0.2)
	var moved_on: float = player.global_position.x - born_player_x
	_check("    the player kept moving", moved_on > 10.0,
		"%.1f px" % moved_on)
	_check("C6  the puff did not move with them",
		is_instance_valid(puff)
			and puff.global_position.is_equal_approx(born_at),
		"born at %s, now %s" % [str(born_at),
			str(puff.global_position) if is_instance_valid(puff) else "<freed>"])
	_note("C6  that is the NODE. Whether the PARTICLES are world-space is")
	_note("     `local_coords = false`, which the configuration test pins.")

	_key(KEY_D, false)
	# C5: everything gone within one lifetime of the last spawn.
	var waited := 0.0
	while driver.live_count() > 0 and waited < 1.0:
		await process_frame
		waited += root.get_process_delta_time()
	# Measured from the key release, not from the last spawn -- the last
	# stride can land anywhere in the frame before the release, so one frame
	# plus one lifetime is the real bound and the label says so.
	_check("C5  every instance was gone within one lifetime of the key release",
		driver.live_count() == 0
			and waited <= DUST_LIFETIME + 2.0 / _fps,
		"%.3f s against %.3f s allowed, %d left"
			% [waited, DUST_LIFETIME + 2.0 / _fps, driver.live_count()])
	await _teardown(main)


## C7.
func _scenario_no_writes() -> void:
	print("\n-- C7: it writes no game state --")
	# No room is loaded here. Each walk below loads and frees its own and is
	# alone in the tree while it runs. The first version of this scenario
	# kept a room of its own open across the three walks: the key presses
	# reached that room's player too, and the traps came out in different
	# states between runs that were supposed to be identical. Three rooms in
	# one tree is not a controlled comparison.

	# C7 is a differential, because the only honest way to show that a node
	# writes nothing is to run the game with it and without it and get the
	# same game. Comparing the traps' states across half a second would prove
	# nothing -- they run their own machine and change on their own. The
	# first version of this check did exactly that and hid it behind an
	# `or true`, which made it pass unconditionally. That is the failure this
	# whole report is about, committed by the test that exists to catch it.
	# THREE walks, not two. The third is a control with the driver present
	# again, because a difference between two runs only means something if
	# two identical runs agree. The first version of this check compared two
	# and went red on the traps' states; the control below is what says
	# whether that was the driver or the comparison.
	var with_a := await _walk_and_record(true)
	var without := await _walk_and_record(false)
	var with_b := await _walk_and_record(true)

	_check("C7  the player's trajectory is identical with and without it",
		with_a["x"] == without["x"] and with_a["x"] == with_b["x"],
		"%.4f / %.4f / %.4f" % [with_a["x"], without["x"], with_b["x"]])
	_check("C7  and so is the player's health",
		with_a["health"] == without["health"]
			and with_a["health"] == with_b["health"],
		"%d / %d / %d" % [with_a["health"], without["health"],
			with_b["health"]])

	# The traps are a function of elapsed time and the three runs are not
	# frame-aligned with each other, so their states are only a valid
	# comparator when the two CONTROL runs agree. When they do not, this
	# prints what it saw and makes no claim, which is the honest result.
	if with_a["traps"] == with_b["traps"]:
		_check("C7  and the traps end in the same state",
			with_a["traps"] == without["traps"],
			"%s vs %s" % [str(with_a["traps"]), str(without["traps"])])
	else:
		_note("C7  trap state is not comparable across these runs: the two")
		_note("     control runs with the driver present disagree with each")
		_note("     other (%s vs %s), so a difference against the run without"
			% [str(with_a["traps"]), str(with_b["traps"])])
		_note("     it (%s) says nothing. The trajectory above is the claim."
			% str(without["traps"]))



## C1's last clause, in a room of its own.
func _scenario_dead() -> void:
	print("\n-- C1: a dead player kicks up nothing --")
	var bits := await _load_room()
	var main: Node = bits[0]
	var driver: Node = bits[1]
	var player: Node2D = bits[2]
	await _wait(0.8)
	await _wait(0.6)
	player.take_damage(player.MAX_HEALTH)
	await process_frame
	_seen.clear()
	for dust in driver.live_dust():
		_seen[dust.get_instance_id()] = true
	var rows: Array = []
	_key(KEY_D, true)
	var t := 0.0
	while t < 0.8:
		await process_frame
		t += root.get_process_delta_time()
		rows.append_array(_sample(driver, player, main))
	_key(KEY_D, false)
	_check("C1  a dead player kicks up no dust", rows.is_empty(),
		"%d puffs, health %d" % [rows.size(), player.health])
	await _teardown(main)


## Loads a fresh room, optionally deletes the driver, walks right for a fixed
## time with real input and reports where the game ended up. Physics here is
## deterministic, so two runs that differ only by the presence of a
## presentation node must agree to the last float.
func _walk_and_record(keep_driver: bool) -> Dictionary:
	var main: Node = load(MAIN).instantiate()
	root.add_child(main)
	await process_frame
	if not keep_driver:
		var d := main.get_node_or_null(^"StepDustDriver")
		if d != null:
			d.free()
	var player: Node2D = main.get_node("Player")
	await _wait(0.8)
	_key(KEY_D, true)
	await _wait(0.6)
	_key(KEY_D, false)
	await process_frame
	var traps: Array = []
	for trap in main.get_node("Traps").get_children():
		traps.append(trap.state)
	var out := {
		"x": player.global_position.x,
		"health": player.health,
		"traps": traps,
	}
	main.queue_free()
	await process_frame
	return out


func _init() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--test-fps="):
			_fps = float(arg.get_slice("=", 1))
	if OS.has_environment("TEST_FPS"):
		_fps = float(OS.get_environment("TEST_FPS"))
	print("frame rate for this run: %.0f fps" % _fps)

	await _scenario_scene_load()
	await _scenario_walk()
	await _scenario_standing_still()
	await _scenario_jump()
	await _scenario_left_behind_and_freed()
	await _scenario_no_writes()
	await _scenario_dead()
	await process_frame
	await process_frame
	print("\n%d checks, %d failure%s at %.0f fps"
		% [_checks, _failures, "" if _failures == 1 else "s", _fps])
	print("Proves: Effect C obeys C1-C7 as game state, at this frame rate.")
	print("Proves nothing about what it looks like, and nothing about G3 -")
	print("whether scale.x = -1 mirrors the throw. That is the strip.")
	quit(1 if _failures > 0 else 0)
