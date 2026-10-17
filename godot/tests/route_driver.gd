extends RefCounted
## Fixed input route through the real level. No position/velocity edits.
##
## The starter's five marks carried the player to the original finish at x=916.
## The finish is now at 1500 (CHANGE-BRIEF revision 0.5.0), so the route is
## extended rather than relaxed: it must still reach COMPLETE with zero deaths.
##
## `jump_marks` fire on the ground, as before. `air_marks` are new and fire
## while airborne, because trap T2 cannot be cleared with ground jumps alone:
## the 16 px landing window between L2's edge (1280) and the spike (1296) can
## only be jumped into from x 1176..1192, and that stretch is inside T1's
## lethal range (1151..1193). The only remaining ground-jump landing strip on
## L1 is 1193..1216, from which a single jump lands on T2. The air jump is
## therefore required, not merely convenient.
var jump_marks: Array[float] = [138.0, 292.0, 424.0, 548.0, 712.0,
	930.0,    # cross the 48 px gap at 960..1008 onto the low road
	1096.0,   # clear trap T1 (1160..1184) and land on the 1193..1216 strip
	1205.0,   # launch across the 64 px gap at 1216..1280
	1390.0,   # clear trap T3 (1432..1456)
	1700.0,   # gap 1728..1792, under the first flying horse
	2020.0,   # gap 2048..2112
	2212.0,   # gap 2240..2304
	2404.0,   # gap 2432..2496
	2596.0,   # gap 2624..2688 onto the final ground
	2770.0]   # clear trap T4 (2800..2824)
var air_marks: Array[float] = [1258.0]   # second jump at apex, to clear trap T2
## The driver SWINGS AT WHAT IT CAN SEE rather than on a blind cycle. Holding
## attack down past a fixed x produced a 36% duty cycle whose active window
## happened to end 8 px short of the first slime, and the player then walked
## into it during the next windup. Reading enemy positions to decide when to
## swing is observation, which the walkthrough skill allows; it still has to
## actually connect. No teleporting, no forced completion, no disabled
## collisions, no test-only gameplay shortcut.
## The driver simply keeps the attack held once it reaches the enemy half. A
## press during a swing is ignored, so this produces back-to-back 16-tick
## swings, each sweeping the full -120..+40 arc, i.e. one complete sweep every
## 43 px of travel.
##
## Two cleverer versions were tried and abandoned. Swinging only when a target
## was within 52 px started the swing too late once the swing grew to 16 ticks:
## the three frames that bring the blade to floor level are ticks 10-12, and
## the player had already collided by tick 9. Adding a vertical-reach filter
## made it worse - from the ground the blade tops out 0.5 px below a flying
## horse, so the filter suppressed the swing entirely until the player was
## airborne, by which point the collision was two frames away. Fitting a
## heuristic to eleven hand-placed enemies was over-fitting a fixture; holding
## the button is what a player would actually do.
const SLASH_FROM := 1500.0
## Stand and fight a ground enemy rather than running into it. Standing still
## at 48 px or less puts the enemy's near edge inside the 35 px the blade
## reaches at floor level, so a full sweep connects; running at 160 px/s meant
## relying on the 9-of-16 live window happening to line up, and a 19 px gap in
## that cycle is what killed the run at the widest patrol.
const STOP_AT := 48.0
const GROUND_BAND := 20.0

func _blocking_ground_enemy(game: Node2D, at: Vector2) -> bool:
	if not game.player.is_on_floor():
		return false
	for i in range(game.enemy_areas.size()):
		if not game.enemy_alive[i]:
			continue
		if absf(game.enemy_anchor[i].y - at.y) > GROUND_BAND:
			continue
		var ahead: float = game.enemy_x[i] - at.x
		if ahead > 0.0 and ahead <= STOP_AT:
			return true
	return false
var next_jump: int = 0
var next_air: int = 0

func step(game: Node2D) -> void:
	var player: CharacterBody2D = game.player
	player.test_control = true
	var fighting: bool = _blocking_ground_enemy(game, player.position)
	player.test_axis = 0.0 if fighting else 1.0
	player.test_jump_held = false
	# A flying horse cannot be hit from the ground - the blade tops out about
	# half a pixel below one - and once airborne the player collides with it
	# about seven frames later, before a fresh windup could finish. So the swing
	# before a jump is TIMED rather than mashed: go quiet long enough for any
	# running swing to end, then press four frames (about 11 px) before the jump
	# mark so the live window is already open at takeoff.
	var mark: float = jump_marks[next_jump] if next_jump < jump_marks.size() else 1.0e9
	var aiming: bool = player.position.x >= mark - 12.0 and player.position.x < mark
	var going_quiet: bool = player.position.x >= mark - 58.0 and player.position.x < mark - 12.0
	# Fighting something on the ground outranks the jump timing: the first
	# version of this went quiet 58 px before a mark, which happened to be
	# exactly where the third slime's fight takes place, so the driver stood
	# still and stopped swinging while the slime walked into it.
	if fighting or aiming or (player.position.x >= SLASH_FROM and not going_quiet):
		player.test_attack_pressed = true
	if next_jump < jump_marks.size() and player.position.x >= jump_marks[next_jump] and player.is_on_floor():
		player.test_jump_pressed = true
		next_jump += 1
	elif next_air < air_marks.size() and player.position.x >= air_marks[next_air] and not player.is_on_floor():
		player.test_jump_pressed = true
		next_air += 1
