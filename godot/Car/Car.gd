# TODO: implement braking
extends VehicleBody

# -------- states --------
# Flag whether the agent has colided
onready var is_collided = false
# Actions
onready var steering_delta: float = 0

onready var relative_steering: float = 0

onready var sensor_placeholder = $SensorPlaceholder


# -------- parameters --------
var car_parameters = {
	"max_steering_angle": 0.8  # I think 0.8 is cosine value of angle the wheel turn at
}

# -------- built-ins --------
func _ready():
	set_car_parameters(car_parameters)
	_configure_collision()

func __physics_process(_delta):
	# Method to be called in agent. 
	# Double underline prefix is used to avoid the method call in GODOT loop.
	_calculate_steering()
	_calculate_engine_force()

# -------- configurators --------
func _configure_collision():
	set_contact_monitor(true)
	set_max_contacts_reported(4)
	connect("body_entered", self, "_on_collision")
#	connect("body_exited", self, "_on_collsion_release")

# -------- setters --------
func set_sensors(sensors: NodePath):
	sensor_placeholder.set_remote_node(sensors)

func set_car_parameters(overriden_car_parameters: Dictionary):
	for key in overriden_car_parameters.keys():
		car_parameters[key] = overriden_car_parameters[key]
	if "mass" in car_parameters.keys():
		mass = car_parameters["mass"]
		weight = car_parameters["mass"] * 9.8

func set_steering_delta(value: float):
	steering_delta = value

func set_engine_force_delta(value: float):
	# TODO: Implement
	pass

# -------- getters --------
func get_is_crashed() -> bool:
	return is_collided

func get_steering() -> float:
	return steering

func get_speed() -> float:
	# TODO: Implement
	return 1.0

# -------- helpers --------
func _calculate_engine_force():
	# TODO: implement
	engine_force = 30

func _calculate_steering():
	relative_steering = clamp(relative_steering + steering_delta, -1, 1)
	steering = relative_steering * car_parameters["max_steering_angle"]

# -------- events --------
func _on_collision(_body):
	is_collided = true
	
#func _on_collision_release(_body):
#	is_collided = false
