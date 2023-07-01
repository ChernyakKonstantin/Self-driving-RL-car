extends Spatial

# --------
const STEPS_PER_CALL = 4  # TODO: make configurable
# --------
export var camera_storage_path: NodePath
# --------
# Flag whether the agent has colided
onready var is_collided = false 
# Flag whether to compute the agent movements
onready var enabled: bool = false
# Distance sensors proxemity
onready var max_distance_sensor_proxemity: float = 1.0  # TODO: make configurable
# Actions
onready var steering_delta: float
onready var acceleration_delta: float

onready var car = $Car

onready var parking_sensors = $Sensors/ParkingSensors
onready var rgb_cameras = $Sensors/RGBCameras

onready var rgb_cameras_data_storage = Dictionary() 
onready var parking_sensors_data_storage: = Dictionary()

# -------- built-ins --------
func _ready():
	car.get_node("SensorPlaceholder").set_remote_node(get_node("Sensors").get_path())
	_configure_parking_sensors()
	_configure_rgb_cameras()

func _physics_process(_delta):
	_append_record_to_storage(rgb_cameras_data_storage, get_rgb_cameras_data())
	_append_record_to_storage(parking_sensors_data_storage, get_parking_sensors_data())

# -------- configurators --------
func _configure_parking_sensors():
	for ray in parking_sensors.get_children():
		ray.set_enabled(true)
		ray.set_exclude_parent_body(true)
		ray.set_collide_with_bodies(true)
		ray.set_collide_with_areas(false)
		ray.set_cast_to(Vector3(0, -max_distance_sensor_proxemity, 0))

func _configure_rgb_cameras():
	for camera_placeholder in rgb_cameras.get_children():
		camera_placeholder.get_child(0).set_name(camera_placeholder.get_name())
		camera_placeholder.get_child(0).set_remote_transform(camera_placeholder)
		
# -------- getters --------
func get_parking_sensors_data() -> Dictionary:
	var result = {}
	for ray in parking_sensors.get_children():
		if ray.is_colliding():
			var collison_point = ray.get_collision_point()
			result[ray.name] = ray.global_translation.distance_to(collison_point)
		else:
			 result[ray.name] = max_distance_sensor_proxemity 
	return result

func get_rgb_cameras_data() -> Dictionary:
	var result = {}
	for camera in rgb_cameras.get_children():
		result[camera.get_name()] = camera.get_child(0).get_frame() 
	return result

func get_is_crashed() -> bool:
	return car.get_is_crashed()
#
func get_steering() -> float:
	return car.get_steering()
#
func get_speed() -> float:
	return car.get_speed()
	
# -------- setters --------
func set_action(action: Dictionary) -> void:
	if action.has("steering_delta"):
		car.steering_delta = action["steering_delta"]
	if action.has("acceleration_delta"):
		car.acceleration_delta = action["acceleration_delta"]
		
# -------- helpers --------
func _append_record_to_storage(storage: Dictionary, data: Dictionary) -> void:
	for key in data.keys():
		if storage.has(key):
			storage[key].append(data[key])
		else:
			storage[key] = [data[key]]

func clear_storage() -> void:
	rgb_cameras_data_storage.clear()
	parking_sensors_data_storage.clear()


