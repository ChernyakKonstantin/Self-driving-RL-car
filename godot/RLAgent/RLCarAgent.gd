extends Spatial

onready var car = $Car
onready var data_recorder = $DataRecorder

# -------- built-ins --------
func _ready():
	car.set_sensors(get_node("Sensors").get_path())

func _physics_process(_delta):
	data_recorder.record()

# -------- getters --------
func get_is_crashed() -> bool:
	return car.get_is_crashed()
#
func get_steering() -> float:
	return car.get_steering()
#
func get_speed() -> float:
	return car.get_speed()
	
func get_lidar_data() -> Dictionary:
	return data_recorder.lidar_data_storage
	
func get_rgb_camera_data() -> Dictionary:
	return data_recorder.rgb_cameras_data_storage
	
func get_parking_sensors_data() -> Dictionary:
	return data_recorder.parking_sensors_data_storage

# -------- setters --------
func set_action(action: Dictionary) -> void:
	if action.has("steering_delta"):
		car.set_steering_delta(action["steering_delta"])
	if action.has("engine_force_delta"):
		car.set_engine_force_delta(action["engine_force_delta"])

# --------
func reset(new_position: Spatial):
	car.set_global_translation(new_position.get_global_translation())
	car.set_global_rotation(new_position.get_global_rotation())
	car.is_collided = false
