extends Node2D
## The dungeon the room is actually in: masonry wall, blind arches, wall
## torches and a torchlit floor lip.
##
## **Ported from walker-ninja-TiantongZhang**, `game/session.gd::_draw()`,
## `_draw_alcove()` and `_draw_torch()` — the author's own original Godot
## vector drawing, not recovered or generated art, recorded as such in that
## repository's `SOURCES.md` section 2. Nothing of walker-ninja was modified
## to bring it here; the geometry below was re-derived for this room.
##
## **Why this exists at all.** Until it did, this room was two flat colours:
## a `#17141B` sky over a `#16242B` floor, a largest-channel difference of
## 16. Assignment 5's Gate V counted the floor as *not content* for exactly
## that reason, and Assignment 6 asks for each particle effect to be judged
## "over your actual level art at its darkest and lightest". There was no
## darkest and lightest. Now there is:
##
##     lightest   torch core `#ffe08a` and the lit floor lip `#c89a5a`
##     darkest    alcove recess `#241e2c` over wall `#1b1620`
##
## **It draws nothing below the floor line.** The floor is a Sprite2D tiling
## `floor_tile.png` over y 200..360, and `CHANGE-BRIEF.md` section 6 fixed
## that tile at `#16242B` *before* the trap sprite was drawn, so the A5 pixel
## predictions are stated against it. Repainting it would invalidate eight
## measured values. Everything here is above y = 200.
##
## **Nothing moves.** walker-ninja learned this the hard way and left the
## note: a flickering torch makes two renders of the same frame differ, and
## the capture pipeline diffs frames pixel-exactly. Assignment 6's frame
## strips have the same requirement, so the torches are static.

## The floor's top edge: Floor sits at y 280 with a 640 x 160 shape.
const GROUND_Y := 200.0
const ROOM_W := 640.0

## Masonry. The wall is deliberately the quietest surface on screen; the
## contrast is spent on the torches and the floor lip, which is where the
## player's attention belongs.
const WALL := Color("1b1620")
const MORTAR := Color("2b2430")
const ALCOVE_EDGE := Color("352c40")
const ALCOVE_RECESS := Color("241e2c")

## Torch. 16 nested discs rather than 4: at four, walker-ninja's rendered
## frames showed the rings as visible banding, which a screenshot caught and
## the code did not.
const TORCH_BRACKET := Color("3a2f26")
const TORCH_FLAME := Color("ff9a3c")
const TORCH_CORE := Color("ffe08a")
const LIT_LIP := Color("c89a5a")

## Placed against the traps at x 208, 320 and 432, not independently of them.
## The middle torch stands over SpikeTrap2 so that one trap sits in the
## brightest stretch of the room and the outer two sit in dim stretches —
## which is what makes "judge it at its darkest and lightest" a real check
## rather than a sentence.
const TORCH_X: Array[float] = [64.0, 320.0, 576.0]
const TORCH_Y := 140.0
const TORCH_POOL_R := 60.0

## Clear of both the torches and the traps. The first placement put these at
## 112 and 528, inside the outer torches' 60 px pools, and the rendered frame
## showed each arch washed out by the light it was supposed to sit beside.
const ALCOVE_X: Array[float] = [160.0, 480.0]
const ALCOVE_HALF := 28.0
const ALCOVE_APEX_Y := 104.0


func _draw() -> void:
	# The wall, generously oversized so a camera nudge cannot reveal an edge.
	draw_rect(Rect2(-64.0, -64.0, ROOM_W + 128.0, GROUND_Y + 64.0), WALL)

	# Staggered mortar courses, so the wall reads as masonry rather than as
	# graph paper. Every other course offsets its vertical joints by half a
	# block.
	var course := 0
	for y in range(40, int(GROUND_Y) + 1, 32):
		draw_line(Vector2(0.0, y), Vector2(ROOM_W, y), MORTAR, 1.0)
		var off: int = 0 if course % 2 == 0 else 32
		for x in range(off, int(ROOM_W) + 1, 64):
			draw_line(Vector2(x, y), Vector2(x, minf(float(y) + 32.0, GROUND_Y)),
				MORTAR, 1.0)
		course += 1

	for cx in ALCOVE_X:
		_draw_alcove(cx)
	for cx in TORCH_X:
		_draw_torch(cx, TORCH_Y)

	_draw_lit_lip()


## The torchlit lip of the floor, warm against the cold stone, in the four
## pixels ABOVE y = 200 so the floor tile itself is untouched.
##
## **It breaks where a trap stands, and that is the point.** The first
## version ran the lip unbroken across the room and the rendered frame
## showed each trap silhouetted against a bright warm band —
## `CHANGE-BRIEF.md` section 6 put the armed trap at 1.12:1 against the
## floor *deliberately*, because a trap visible from across the room is not
## a trap, and an unbroken lip threw that away. Each trap now stands in a
## gap the torchlight does not reach.
##
## The gaps are read from the Traps node at draw time rather than typed
## here, so moving a trap in the scene moves its gap with it.
func _draw_lit_lip() -> void:
	const GAP_HALF := 14.0
	var gaps: Array[float] = []
	var traps := get_node_or_null(^"../Traps")
	if traps != null:
		for t in traps.get_children():
			if t is Node2D:
				gaps.append((t as Node2D).position.x)
	gaps.sort()

	var x := 0.0
	for cx in gaps:
		var from := maxf(x, 0.0)
		var to := clampf(cx - GAP_HALF, 0.0, ROOM_W)
		if to > from:
			draw_rect(Rect2(from, GROUND_Y - 4.0, to - from, 4.0), LIT_LIP)
		x = maxf(x, cx + GAP_HALF)
	if x < ROOM_W:
		draw_rect(Rect2(x, GROUND_Y - 4.0, ROOM_W - x, 4.0), LIT_LIP)


## A blind arch cut into the wall. Drawn twice: once two pixels larger in a
## lighter stone, then the recess on top. The two pixels that survive are the
## arch's own masonry edge, which is what makes it read as cut into the wall
## rather than as a dark blob painted on it.
func _draw_alcove(cx: float) -> void:
	for pass_i in range(2):
		var grow: float = 2.0 if pass_i == 0 else 0.0
		var half := ALCOVE_HALF + grow
		var springing := ALCOVE_APEX_Y + half
		var pts := PackedVector2Array()
		pts.append(Vector2(cx - half, GROUND_Y))
		var steps := 14
		for i in range(steps + 1):
			var a: float = PI - PI * float(i) / float(steps)
			pts.append(Vector2(cx + cos(a) * half, springing - sin(a) * half))
		pts.append(Vector2(cx + half, GROUND_Y))
		draw_colored_polygon(pts, ALCOVE_EDGE if pass_i == 0 else ALCOVE_RECESS)


## A wall torch: a pool of nested translucent discs, then the bracket and the
## flame. Static on purpose — see the note at the top of this file.
func _draw_torch(cx: float, cy: float) -> void:
	for i in range(16):
		draw_circle(Vector2(cx, cy), TORCH_POOL_R - float(i) * 3.6,
			Color(1.0, 0.60, 0.24, 0.018))
	draw_rect(Rect2(cx - 1.0, cy, 2.0, 10.0), TORCH_BRACKET)
	draw_colored_polygon(PackedVector2Array([
		Vector2(cx - 3.0, cy + 1.0), Vector2(cx, cy - 7.0), Vector2(cx + 3.0, cy + 1.0)]),
		TORCH_FLAME)
	draw_colored_polygon(PackedVector2Array([
		Vector2(cx - 1.5, cy), Vector2(cx, cy - 4.0), Vector2(cx + 1.5, cy)]),
		TORCH_CORE)
