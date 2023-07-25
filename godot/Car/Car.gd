# TODO: implement braking
extends VehicleBody

# -------- states --------
# Flag whether the agent has colided
onready var is_collided = false
# Actions
onready var steering_delta: float
onready var acceleration_delta: float
onready var sensor_placeholder = $SensorPlaceholder

# -------- parameters --------
var car_parameters = {
	"max_rpm": 500,  # Maximum wheel rotational speed in revolutions per minute
	"max_torque": 200,
	"max_steering": 0.8  # I think 0.8 is cosine value of angle the wheel turn at
}

# -------- built-ins --------
func _ready():
	_configure_collision()

func _physics_process(delta):
	var manual_steering = Input.get_axis("move_right", "move_left")
	var manual_acceleration = Input.get_axis("move_backward", "move_forward")
	if manual_steering != 0:
		steering_delta = manual_steering
	if manual_acceleration != 0:
		acceleration_delta = manual_acceleration

	steering = lerp(
		steering,
		steering_delta * car_parameters["max_steering"],
		5 * delta)

	$back_left_wheel.engine_force = _calculate_engine_force(
		acceleration_delta,
		$back_left_wheel)
	$back_right_wheel.engine_force = _calculate_engine_force(
		acceleration_delta,
		$back_right_wheel)
	steering_delta = 0
	acceleration_delta = 0

# -------- configurators --------
func _configure_collision():
	set_contact_monitor(true)
	set_max_contacts_reported(4)
	connect("body_entered", self, "_on_collision")

# -------- setters --------
func set_sensors(sensors: NodePath):
	sensor_placeholder.set_remote_node(sensors)

func set_car_parameters(overriden_car_parameters: Dictionary):
	for key in overriden_car_parameters.keys():
		car_parameters = overriden_car_parameters[key]

func set_steering(value: float):
	steering_delta = value

func set_acceleration(value: float):
	acceleration_delta = value

# -------- getters --------
func get_is_crashed() -> bool:
	return is_collided

func get_steering() -> float:
	return steering

func get_speed() -> float:
	return $back_left_wheel.engine_force

# -------- helpers --------
func _calculate_engine_force(acceleration: float, wheel: VehicleWheel) -> float:
	var force = (
		acceleration
		* car_parameters["max_torque"]
		* (1 - wheel.get_rpm() / car_parameters["max_rpm"])
	)
	return force

# -------- events --------
func _on_collision(_body):
	is_collided = true

