extends Spatial
class_name InternalPositionTracker, "../icons/custom_node_icon.png"

# Steering wheel is expected here.
export (NodePath) var wheel_path
export (float) var max_rpm = 1000.0

var wheel: VehicleWheel

onready var position: Vector2
onready var orientation: float

func _ready():
	wheel = get_node(wheel_path)
	reset()
	
func reset():
	position = Vector2(0.0, 0.0)
	orientation = 0.0
	
func _physics_process(delta):
	var rpm = abs(wheel.get_rpm())
	if rpm > max_rpm:
		rpm = 0
	var N_wh_rev = rpm / 60 * delta # Why I have negative RPM here?
	print(wheel.get_rpm())
	var delta_l = N_wh_rev * 2 * PI * wheel.get_radius()
	var steering_angle = wheel.get_steering()
	orientation += steering_angle
	var delta_x = cos(orientation) * delta_l
	var delta_y = sin(orientation) * delta_l
	var delta_position = Vector2(delta_x, delta_y)
	print(position, " / ", delta_position, " / ", steering_angle, " / ", delta_l)
	print()
	position += delta_position
	
func get_data() -> Dictionary:
	var data = Dictionary()
	data["x"] = position.x
	data["y"] = position.y
	data["orientation"] = orientation
	return data
