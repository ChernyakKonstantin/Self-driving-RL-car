extends Node
class_name PhysicsFramesTimer, "icons/custom_node_icon.png"

signal timer_end

export var limit: int = 4

onready var _counter: int = 0
onready var is_started: bool = false
	
func _physics_process(delta):
	if is_started:
		_counter += 1
		if _counter > limit:
			_counter = 0
			is_started = false
			emit_signal("timer_end")
	
func start():
	_counter = 0	
	is_started = true
	return self
