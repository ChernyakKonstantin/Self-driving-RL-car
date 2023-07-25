extends Node
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

enum DataType {
	INT32 = 1
	FLOAT32 = 2
	JSON = 3
	NAMED_IMAGE = 4
}

# --------
const STATUS_KEY = "status"
const CONFIG_KEY = "config"
const RESET_KEY = "reset"
const ACTION_KEY = "action"
const OBSERVATION_KEY = "observation"
# --------
onready var server = TCP_Server.new()
onready var agent = $RLCarAgent
onready var world = $World

onready var have_connection: bool = false
onready var connection: StreamPeerTCP
onready var request: Dictionary

# -------- built-ins --------
func _ready():
	agent.connect("done_action", self, "_on_done_action")
	# Listen for incoming connections
	server.listen(port, address)

	# Environment is not pausable while Agent and World is pausable.
	set_pause_mode(2)
	for child in get_children():
		child.set_pause_mode(1)

	get_tree().set_pause(true)

func _physics_process(_delta):
	if not have_connection and server.is_connection_available():
		connection = server.take_connection()
		request = _read_request(connection)
		have_connection = true
		if request.has(RESET_KEY):
			_on_reset(request, connection)
		elif request.has(ACTION_KEY):
			_on_action(request, connection)

# -------- helpers --------
func _read_request(connection: StreamPeerTCP) -> Dictionary:
	var request_package_size = connection.get_available_bytes()
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result
	return request
	
#func _configure(configuration: Dictionary):
#	if configuration.has("repeat_action"):
#		repeat_action = configuration["repeat_action"]

func _on_reset(request: Dictionary, connection: StreamPeerTCP):
	world.reset()
	agent.reset(world.sample_initial_position())
	_send_response(request[OBSERVATION_KEY], connection)
	_on_after_send_response(connection)
	
func _on_action(request: Dictionary, connection: StreamPeerTCP):
	agent.set_action(request[ACTION_KEY])
	if get_tree().is_paused():
			get_tree().set_pause(false)  # Enable physics

#func _on_done_action(request: Dictionary, connection: StreamPeerTCP):
func _on_done_action():
	get_tree().set_pause(true)
	_send_response(request[OBSERVATION_KEY], connection)
	_on_after_send_response(connection)

func _on_after_send_response(connection: StreamPeerTCP):
	request.clear()
	agent.data_recorder.clear_storage()
	connection.disconnect_from_host()
	have_connection = false

func _send_response(observation_request: Array, connection: StreamPeerTCP) -> void:
	connection.put_32(observation_request.size())
	if Request.FRAME in observation_request:
		var frames: Dictionary = agent.get_rgb_camera_data()
		_put_named_image("cameras", frames, connection)
	if Request.PARKING_SENSORS in observation_request:
		var parking_sensors_data: Dictionary = agent.get_parking_sensors_data()
		print("parking_sensors_data: ", parking_sensors_data)
		_put_json("parking_sensor", parking_sensors_data, connection)
	if Request.LIDAR in observation_request:
		var lidar_data: Array = agent.get_lidar_data()
		_put_json("lidar", lidar_data, connection)
	if Request.IS_CRASHED in observation_request:
		var is_crashed: int = agent.get_is_crashed()
		print("Is_crashed: ", is_crashed)
		_put_int32("is_crashed", is_crashed, connection)
	if Request.STEERING in observation_request:
		var steering: float = agent.get_steering()
		print("Steering: ", steering)
		_put_float32("steering", steering, connection)
	if Request.SPEED in observation_request:
		var speed: float = agent.get_speed()
		_put_float32("speed", speed, connection)

func _put_float32(name: String, value: float, connection: StreamPeerTCP) -> void:
	connection.put_string(name)  # Data name
	connection.put_32(DataType.FLOAT32)  # Data type
	connection.put_float(value)

func _put_int32(name: String, value: int, connection: StreamPeerTCP) -> void:
	connection.put_string(name)  # Data name
	connection.put_32(DataType.INT32)  # Data type
	connection.put_32(value)

func _put_json(name: String, value, connection: StreamPeerTCP) -> void:
	# value can be Array or Dictionary
	var value_: PoolByteArray = JSON.print(value).to_utf8() # Encode to bytes
	connection.put_string(name)  # Data name
	connection.put_32(DataType.JSON)  # Data type
	connection.put_32(value_.size())  # Data lenght in bytes
	connection.put_data(value_)

func _put_named_image(name: String, value: Dictionary, connection: StreamPeerTCP) -> void:
		connection.put_string(name)  # Data name
		connection.put_32(DataType.NAMED_IMAGE)  # Data type
		connection.put_32(value.size())  # Number of keys
		for key in value.keys():
			connection.put_string(key)  # Image name
			connection.put_32(value[key].size())  # Number of images
			for image in value[key]:
				image.convert(Image.FORMAT_RGB8)
				var image_data = image.get_data()
				connection.put_32(image_data.size()) # Image length in bytes
				connection.put_data(image_data)

