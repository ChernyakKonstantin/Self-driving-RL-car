extends Spatial
class_name InternalPositionTracker, "../icons/custom_node_icon.png"

# Steering wheel is expected here.
export (NodePath) var left_steering_wheel_path
export (NodePath) var right_steering_wheel_path

var left_steering_wheel: VehicleWheel
var right_steering_wheel: VehicleWheel
var wheel_base: float = 2.465

onready var position: Vector2
onready var orientation: float

func _ready():
	left_steering_wheel = get_node(left_steering_wheel_path)
	right_steering_wheel = get_node(right_steering_wheel_path)
#	wheel_base = steering_wheel.get_global_translation().distance_to(traction_wheel.get_global_translation())
#	print(wheel_base)
	reset()
	
func reset():
	position = Vector2(0.0, 0.0)
	orientation = 0.0
	
func _physics_process(delta):
	var steering_angle = left_steering_wheel.get_steering()
	var rpm
	if left_steering_wheel.is_in_contact() and right_steering_wheel.is_in_contact():
		var rpm_left = left_steering_wheel.get_rpm()
		var rpm_right = right_steering_wheel.get_rpm()
		rpm = abs(rpm_left + rpm_right) / 2
	else:
		rpm = 0
	var N_wh_rev = rpm / 60 * delta
	var distance = N_wh_rev * 2 * PI * left_steering_wheel.get_radius()
	var turning_radius = wheel_base / (tan(steering_angle) + 1e-12)
	var real_angle = distance / turning_radius
#	print("real: ", rad2deg(real_angle), " steering: ", rad2deg((steering_angle)))
	var delta_x = turning_radius * (1 - cos(real_angle))
	var delta_y = turning_radius * sin(real_angle)
	# Rotate back to non-rotated system.
	var delta_x_no_rotation = delta_x * cos(orientation) - delta_y * sin(orientation)
	var delta_y_no_rotation = delta_x * sin(orientation) + delta_y * cos(orientation)
	var delta_position = Vector2(delta_x_no_rotation, delta_y_no_rotation)
	orientation += real_angle
	position += delta_position
	
#
func get_data() -> Dictionary:
	var data = Dictionary()
	data["x"] = position.x
	data["y"] = position.y
	data["orientation"] = orientation
	return data
