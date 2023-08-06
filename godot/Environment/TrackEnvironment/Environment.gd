extends RLEnvironment
# --------
export var address: String = "127.0.0.1"
export var port: int = 9090

# --------
enum Request {
	CAMERA = 1,
	IS_CRASHED = 2,
	STEERING = 3,
	SPEED = 4,
	PARKING_SENSORS = 5,
	LIDAR = 6,
}

onready var agent = $RLCarAgent
onready var world = $World
onready var server_configuration = $GUI/ServerConfiguration
onready var gui = $GUI

# -------- built-ins --------
func _ready():
	server_configuration.connect("start_server", communication, "_on_start_server")
	# GUI is not pausable
	gui.set_pause_mode(2)
	# Agent and World is pausable.
	world.set_pause_mode(1)
	agent.set_pause_mode(1)
	
#func _configure(configuration: Dictionary):
#	if configuration.has("repeat_action"):
#		repeat_action = configuration["repeat_action"]

func _reset():
	world.reset()
	agent.reset(world.sample_initial_position())
	for i in range(repeat_action):
		agent.data_recorder.record()
	
func _step(action):
	agent.step(action)
	yield(._step(action), "completed")
	gui.set_steering_wheel_angle(agent.car.relative_steering)

func _after_send_response():
	agent.data_recorder.clear_storage()
	
func _send_response(observation_request: Array):
	var response_json = Dictionary()
	var binary_data = PoolByteArray()
	if Request.IS_CRASHED in observation_request:
		response_json["is_crashed"] = agent.get_is_crashed()
	if Request.STEERING in observation_request:
		response_json["steering"] = agent.get_steering()
	if Request.SPEED in observation_request:
		response_json["speed"] = agent.get_speed()
	if Request.PARKING_SENSORS in observation_request:
		response_json["parking_sensor"] = agent.get_parking_sensors_data()
	if Request.LIDAR in observation_request:
		response_json["lidar"] = agent.get_lidar_data()
	if Request.CAMERA in observation_request:
		var rgb_camera_data: Dictionary = agent.get_rgb_camera_data()
		response_json["cameras"] = Array()
		for key in rgb_camera_data.keys():
			response_json["cameras"].append(key)
	communication.put_json(response_json)
#	communication.put_named_image(frames, "cameras")
	
	
	
	
