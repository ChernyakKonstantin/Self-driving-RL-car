extends Control
tool

export var max_steering_wheel_angle: float = 90

func _enter_tree():
	# Set viewport size.
	get_node("ViewportContainer").set_size(get_size())
	get_node("ViewportContainer/Viewport").set_size(get_size())
	get_node("ServerConfiguration/").set_size(get_size())
	
func set_steering_wheel_angle(value: float):
	$SteeringWheelSprite.set_rotation_degrees(-value * max_steering_wheel_angle)
