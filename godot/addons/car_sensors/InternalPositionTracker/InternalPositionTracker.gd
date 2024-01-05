extends Spatial
class_name InternalPositionTracker, "../icons/custom_node_icon.png"

# Steering wheel is expected here.
export (NodePath) var left_steering_wheel_path
export (NodePath) var right_steering_wheel_path
export (NodePath) var left_traction_wheel_path
export (NodePath) var right_traction_wheel_path

var left_steering_wheel: VehicleWheel
var right_steering_wheel: VehicleWheel
var left_traction_wheel: VehicleWheel
var right_traction_wheel: VehicleWheel
var wheel_base: float
var max_rpm = 300  # TODO: fix hardcode
	
onready var position: Vector2
onready var orientation: float
var prev_vel_vec: Vector2
var prev_rpm: float

func _ready():
	left_steering_wheel = get_node(left_steering_wheel_path)
	right_steering_wheel = get_node(right_steering_wheel_path)
	left_traction_wheel = get_node(left_traction_wheel_path)
	right_traction_wheel = get_node(right_traction_wheel_path)
	# Calculate wheel base for an usual 4-wheel car.
	var l_st_wh_glob_tr = left_steering_wheel.get_global_translation()
	var l_tr_wh_gl_tr = left_traction_wheel.get_global_translation()
	wheel_base = l_st_wh_glob_tr.distance_to(l_tr_wh_gl_tr)
	reset()
	
func reset():
	position = Vector2(0.0, 0.0)
	orientation = 0.0
	prev_vel_vec = Vector2(0.0, 0.0)
	prev_rpm = 0.0

	
func _physics_process(delta):
	var steering_angle = left_steering_wheel.get_steering()

	var rpm_left = clamp(left_traction_wheel.get_rpm(), -max_rpm, max_rpm)
	var rpm_right = clamp(right_traction_wheel.get_rpm(), -max_rpm, max_rpm)
	var rpm = (rpm_left + rpm_right) / 2
	var N_wh_rev = abs(rpm) / 60 * delta
	
	var distance = N_wh_rev * 2 * PI * left_steering_wheel.get_radius()
	var turning_radius = wheel_base / (tan(steering_angle) + 1e-12)
	var real_angle = distance / turning_radius
	var delta_x = turning_radius * (1 - cos(real_angle))
	var delta_y = turning_radius * sin(real_angle)
	# Rotate back to non-rotated system.
	var delta_x_no_rotation = delta_x * cos(orientation) - delta_y * sin(orientation)
	var delta_y_no_rotation = delta_x * sin(orientation) + delta_y * cos(orientation)
	var delta_position = Vector2(delta_x_no_rotation, delta_y_no_rotation)
	orientation += real_angle
	position += delta_position

func get_data() -> Dictionary:
	var data = Dictionary()
	data["x"] = position.x
	data["y"] = position.y
	data["orientation"] = orientation
	return data
