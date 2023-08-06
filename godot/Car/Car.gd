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
var max_steering_angle =  0.8  # I think 0.8 is cosine value of angle the wheel turn at
var max_engine_force = 30

# -------- built-ins --------
func _ready():
	_configure_collision()

func _physics_process(_delta):
	_calculate_steering()
	_calculate_engine_force()

# -------- configurators --------
func _configure_collision():
	set_contact_monitor(true)
	set_max_contacts_reported(4)
	connect("body_entered", self, "_on_collision")

# -------- setters --------
func set_sensors(sensors: NodePath):
	sensor_placeholder.set_remote_node(sensors)

func set_steering_delta(value: float):
	steering_delta = value

func set_engine_force_delta(value: float):
	# TODO: Implement
	pass

# -------- getters --------
func get_is_crashed() -> bool:
	return is_collided

func get_steering() -> float:
	return relative_steering

func get_speed() -> float:
	# TODO: Implement
	return 1.0

# -------- helpers --------
func _calculate_engine_force():
	# TODO: implement
	engine_force = max_engine_force

func _calculate_steering():
	relative_steering = clamp(relative_steering + steering_delta, -1, 1)
	steering = relative_steering * max_steering_angle

func configure(car_config: Dictionary):
	if "max_steering_angle" in car_config.keys():
		max_steering_angle = car_config["max_steering_angle"]
	if "max_engine_force" in car_config.keys():
		max_engine_force = car_config["max_engine_force"]
		
# -------- events --------
func _on_collision(_body):
	is_collided = true
