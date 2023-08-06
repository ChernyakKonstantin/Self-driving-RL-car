extends RLEnvironment
# --------
export var address: String = "127.0.0.1"
export var port: int = 9090

# --------
enum Request {
	FRAME = 1,
	IS_CRASHED = 2,
	STEERING = 3,
	SPEED = 4,
	PARKING_SENSORS = 5,  # Distance the closest object;
	LIDAR = 6,
}

onready var agent = $RLCarAgent
onready var world = $World
onready var server_configuration = $GUI/ServerConfiguration
onready var gui = $GUI

# -------- built-ins --------
func _ready():
	server_configuration.connect("start_server", communication, "_on_start_server")
	
	# Environment and server_configuration is not pausable 
	# while Agent and World is pausable.
	set_pause_mode(2)
	for child in get_children():
		if child.get_name() != "GUI":
			child.set_pause_mode(1)
	get_tree().set_pause(true)
	communication.set_pause_mode(2)

# -------- helpers --------

#func _configure(configuration: Dictionary):
#	if configuration.has("repeat_action"):
#		repeat_action = configuration["repeat_action"]

func _reset():
	world.reset()
	agent.reset(world.sample_initial_position())
	
func _step(action):
	agent.set_action(action)
	yield(._step(action), "completed")
	gui.set_steering_wheel_angle(agent.car.relative_steering)

func _after_send_response():
	agent.data_recorder.clear_storage()
	
func _send_response(observation_request: Array):
	communication.connection.put_32(observation_request.size()) # TODO: fix hardcode
	if Request.FRAME in observation_request:
		var frames: Dictionary = agent.get_rgb_camera_data()
		communication.put_named_image(frames, "cameras")
	if Request.PARKING_SENSORS in observation_request:
		var parking_sensors_data: Dictionary = agent.get_parking_sensors_data()
		communication.put_json(parking_sensors_data, "parking_sensor")
	if Request.LIDAR in observation_request:
		var lidar_data: Array = agent.get_lidar_data()
		communication.put_json(lidar_data, "lidar")
	if Request.IS_CRASHED in observation_request:
		var is_crashed: int = agent.get_is_crashed()
		communication.put_int32(is_crashed, "is_crashed")
	if Request.STEERING in observation_request:
		var steering: float = agent.get_steering()
		communication.put_float32(steering, "steering")
	if Request.SPEED in observation_request:
		var speed: float = agent.get_speed()
		communication.put_float32(speed, "speed")
