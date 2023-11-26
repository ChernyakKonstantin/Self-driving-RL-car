# Make sure agent is called after PhysicsFramesTimer

extends RLAgent

enum Request {
	CAMERA = 1,
	IS_CRASHED = 2,
	STEERING = 3,
	SPEED = 4,
	PARKING_SENSORS = 5,
	LIDAR = 6,
	GLOBAL_COORDINATES = 7,
}

onready var car = $Car
onready var data_recorder = $DataRecorder
onready var lidar = $Sensors/LIDAR
onready var gps = $Sensors/GPS

# -------- built-ins --------
func _ready():
	car.set_sensors(get_node("Sensors").get_path())

func get_is_crashed() -> bool:
	return car.get_is_crashed()
#
func get_steering() -> float:
	return car.get_steering()
#
func get_speed() -> float:
	return car.get_speed()

func get_lidar_data() -> Array:
	return data_recorder.lidar_data_storage

func get_rgb_camera_data() -> Dictionary:
	return data_recorder.rgb_cameras_data_storage

func get_parking_sensors_data() -> Dictionary:
	return data_recorder.parking_sensors_data_storage

func get_gps_data() -> Dictionary:
	return gps.get_data()

func set_action(action: Dictionary) -> void:
	if action.has("steering_delta"):
		car.set_steering_delta(action["steering_delta"])
	if action.has("engine_force_delta"):
		car.set_engine_force_delta(action["engine_force_delta"])

func reset(arguments=null):
	var new_position: Spatial = arguments
	car.set_global_translation(new_position.get_global_translation())
	car.set_global_rotation(new_position.get_global_rotation())
	car.relative_steering = 0
	car.is_collided = false

func configure(agent_config: Dictionary):
	if "lidar" in agent_config.keys():
		lidar.configure(agent_config["lidar"])
	if "car" in agent_config.keys():
		car.configure(agent_config["car"])

func get_data(observation_request, storage) -> void:
	if Request.CAMERA in observation_request:
		var rgb_camera_data = get_rgb_camera_data()
		for key in rgb_camera_data.keys():
			var camera_frames_storage = storage.add_cameras(key)
			for frame in rgb_camera_data[key]:
				var frame_storage = camera_frames_storage.add_frame()
				frame_storage.set_height(int(frame.get_size().y))
				frame_storage.set_width(int(frame.get_size().x))
				frame_storage.set_format("rgb")
				frame_storage.set_data(frame.get_data())
	if Request.IS_CRASHED in observation_request:
		storage.set_is_crashed(get_is_crashed())
	if Request.STEERING in observation_request:
		storage.set_steering(get_steering())
	if Request.SPEED in observation_request:
		storage.set_speed(get_speed())
	if Request.PARKING_SENSORS in observation_request:
		var parking_sensors_data = get_parking_sensors_data()
		for key in parking_sensors_data.keys():
			var distances_storage = storage.add_parking_sensors(key)
			for distance in parking_sensors_data[key]:
				 distances_storage.add_distance(distance)
	if Request.LIDAR in observation_request:
		var lidar_data = get_lidar_data()
		for points in lidar_data:
			var points_storage = storage.add_lidar()
			for point in points:
				var point_storage = points_storage.add_point()
				point_storage.set_x(point["x"])
				point_storage.set_y(point["y"])
				point_storage.set_z(point["z"])
	if Request.GLOBAL_COORDINATES in observation_request:
		var global_coordinates_storage = storage.new_global_coordinates()
		var global_coordinates = get_gps_data()
		global_coordinates_storage.set_x(global_coordinates["x"])
		global_coordinates_storage.set_y(global_coordinates["y"])
		global_coordinates_storage.set_z(global_coordinates["z"])
		global_coordinates_storage.set_orientation(global_coordinates["orientation"])
