extends Node
## Puts Effect A on the game's own event. Assignment 6, Step 3.
##
## **It changes no game script.** `spike_trap.gd` is not touched: this node
## connects to the `fired` signal it already emits at `:98` and instances a
## burst. Presentation reads game state and never writes it — the same
## boundary `trap_warning_driver.gd`, `room_audio.gd` and `pose_driver.gd`
## keep. No setting lives here either; those are in `hit_burst.tscn`.
##
## **The burst is parented to the room, not to the trap.** `CHANGE-BRIEF.md`
## section 1.4 rule A5. Nothing frees a trap in this game, so parenting to it
## would never fail *here* — and would fail silently in the next game that
## reuses this code, which is the assignment's named "freed parent" failure.
## Parenting to the room costs nothing and removes the question.
##
## **One instance per event, never a reused node.** Rule A3. Setting
## `emitting = true` on a `one_shot` node that is still emitting does not
## restart it, so a single shared node drops the second of two close events.
## Three traps in one room makes that ordinary play.

const BURST := preload("res://effects/hit_burst.tscn")

## Where bursts are parented. Set from the scene so the test can read it back.
@export var room_path: NodePath = ^".."
## Where the traps are found.
@export var traps_path: NodePath = ^"../Traps"

var _room: Node = null
var _live: Array[Node2D] = []


func _ready() -> void:
	_room = get_node_or_null(room_path)
	var traps := get_node_or_null(traps_path)
	if traps == null:
		return
	for trap in traps.get_children():
		if trap is Node2D and trap.has_signal(&"fired"):
			# bind() so the handler knows WHICH trap fired without asking the
			# trap for anything. A2: the burst goes at that trap's position.
			trap.fired.connect(_on_trap_fired.bind(trap as Node2D))


func _on_trap_fired(trap: Node2D) -> void:
	if _room == null:
		return
	var burst := BURST.instantiate() as Node2D
	_room.add_child(burst)
	burst.global_position = trap.global_position
	burst.call(&"fire")
	_live.append(burst)


## A4/A6, for the state test: how many bursts are alive right now. Instances
## free themselves, so this prunes rather than counts a stale list.
##
## **Not `filter()`.** The first version of this was
## `_live.filter(func(b: Node2D) -> bool: ...)`, which works until an instance
## actually frees itself and then throws every single call afterwards --
## a freed object cannot be passed to a parameter typed `Node2D`, and
## `filter()` returns an untyped `Array` that will not assign back to
## `Array[Node2D]` either. `test_hit_burst_state.gd` caught it on the A6
## scenario, which is the first place in the repository where this function is
## called after a burst has died.
func live_count() -> int:
	var kept: Array[Node2D] = []
	for b in _live:
		if is_instance_valid(b):
			kept.append(b)
	_live = kept
	return _live.size()


## A3, for the state test: the live instances, newest last.
func live_bursts() -> Array[Node2D]:
	live_count()
	return _live
