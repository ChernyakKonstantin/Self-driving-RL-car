extends Spatial
class_name InternalPositionTracker, "../icons/custom_node_icon.png"

# Steering wheel is expected here.
export (NodePath) var wheel_path

var wheel: VehicleWheel

onready var position = Vector2(0, 0)
onready var orientation = deg2rad(0.0)

func _ready():
	wheel = get_node(wheel_path)
	
func reset():
	position = Vector2(0, 0)
	orientation = deg2rad(0.0)
	
func _physics_process(delta):
	var N_wh_rev = wheel.get_rpm() / 60 * delta
	var delta_l = N_wh_rev * 2 * PI * wheel.get_radius()
	var steering_angle = wheel.get_steering()
	var delta_x
	var delta_y
	if steering_angle != 0:
		steering_angle = deg2rad(steering_angle)
		var turning_arc_radius = delta_l / steering_angle
		var turning_arch_chord = 2 * sin(steering_angle / 2) * turning_arc_radius
		delta_x = cos(steering_angle) * turning_arch_chord
		delta_y = sin(steering_angle) * turning_arch_chord
		orientation += steering_angle
	else:
		delta_x = cos(orientation) * delta_l
		delta_y = sin(orientation) * delta_l
	var delta_position = Vector2(delta_x, delta_y)
	position += delta_position
	
func get_data() -> Dictionary:
	var data = Dictionary()
	data["x"] = position.x
	data["y"] = position.y
	data["orientation"] = orientation
	return data
