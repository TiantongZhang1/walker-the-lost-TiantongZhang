class_name TrapWarningDriver
extends Node

## Presentation for SpikeTrap: reads `warn_amount` and writes it into the
## hand-written shader's uniform once per frame.
##
## The shader is res://shaders/trap_warning.gdshader and is NOT this file's
## to edit. This script only moves a number from game state into a material.
##
## CHANGE-BRIEF.md section 4: presentation may read game state and never
## writes it. Nothing here calls into SpikeTrap, times anything, or decides
## when the trap fires - grep this file for `_trap.` and every hit is a read.
##
## The two failure cases it is built against:
##   F1/R6  Sub-resources in a PackedScene are shared between instances of
##          that scene, so all three traps in main.tscn would hold ONE
##          ShaderMaterial and turn red together. _ready() duplicates it.
##   F5     set_shader_parameter() on a name the shader does not declare
##          writes nowhere and reports nothing. _ready() asks the shader what
##          it actually declares and says so loudly if the name is missing.

## The uniform this driver writes. Named once, so the Step 2 rename mutation
## has exactly one place to disagree with the shader.
const UNIFORM_WARN := &"warn_amount"

## This instance's own copy of the material. Public so a test can read the
## uniform back without reaching through the sprite.
var material: ShaderMaterial = null

## False when the shader does not declare UNIFORM_WARN. A test asserts this
## rather than trusting that a silent write arrived.
var uniform_declared := false

var _trap: SpikeTrap = null
var _sprite: Sprite2D = null


func _ready() -> void:
	# After SpikeTrap._process (priority 0) and before the test sampler
	# (1000), so the uniform written this frame carries the value computed
	# this frame rather than the previous one.
	process_priority = 100

	_trap = get_parent() as SpikeTrap
	if _trap == null:
		push_error("TrapWarningDriver must be a child of a SpikeTrap.")
		set_process(false)
		return

	_sprite = _trap.get_node_or_null(^"Sprite2D") as Sprite2D
	if _sprite == null:
		push_error("TrapWarningDriver found no Sprite2D sibling.")
		set_process(false)
		return

	var shared := _sprite.material as ShaderMaterial
	if shared == null:
		push_error("Sprite2D carries no ShaderMaterial; nothing to drive.")
		set_process(false)
		return

	# R6. duplicate() is shallow, which is what is wanted: the Shader itself
	# stays shared (it is read-only program text) while the parameter block
	# becomes this trap's own.
	material = shared.duplicate() as ShaderMaterial
	_sprite.material = material

	uniform_declared = _declares(material.shader, UNIFORM_WARN)
	if not uniform_declared:
		push_error("Shader does not declare a uniform named '%s'; every write from this driver would be discarded in silence." % UNIFORM_WARN)


func _process(_delta: float) -> void:
	if material == null:
		return
	material.set_shader_parameter(UNIFORM_WARN, _trap.warn_amount)


## Whether `shader` declares a uniform by this name. Asks the engine rather
## than the source text, because the engine is what set_shader_parameter
## will consult.
static func _declares(shader: Shader, uniform: StringName) -> bool:
	if shader == null:
		return false
	for entry in shader.get_shader_uniform_list():
		if StringName(entry.get("name", "")) == uniform:
			return true
	return false
