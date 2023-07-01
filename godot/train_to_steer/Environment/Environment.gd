extends Node
# --------
export var address: String = "127.0.0.1"
export var port: int = 9090
export var repeat_action: int = 4
# --------
enum Request {
	FRAME = 1, 
	IS_CRASHED = 2, 
	STEERING = 3,
	SPEED = 4, 
	OBSTACLE_PROXEMITY = 5,  # Distance the closest object;
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
onready var step_counter: int = 0
onready var have_connection: bool = false
onready var connection: StreamPeerTCP
onready var request: Dictionary

# -------- built-ins --------
func _ready():
	# Listen for incoming connections
	server.listen(port, address)
	
	# Environment is not pausable while Agent and World is pausable.
	set_pause_mode(2)
	for child in get_children():
		child.set_pause_mode(1)
	
	get_tree().set_pause(true) 

func _physics_process(_delta):
	if not have_connection:
		if server.is_connection_available():
			connection = server.take_connection()
			request = _read_request(connection)
			if request.has(ACTION_KEY):
				agent.set_action(request[ACTION_KEY])
				# Enable physics
				get_tree().set_pause(false) 
				have_connection = true
	if have_connection:
		# Send observation if step is done
		step_counter += 1
		if step_counter % repeat_action == 0:
			# Disable physics
			get_tree().set_pause(true) 
			if request.has(OBSERVATION_KEY):
				_send_response(request[OBSERVATION_KEY], connection)
			request.clear()
			agent.clear_storage()
			connection.disconnect_from_host()
			have_connection = false
			

# -------- helpers --------
func _read_request(connection: StreamPeerTCP) -> Dictionary:
	var request_package_size = connection.get_available_bytes()
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result
	return request

func _send_response(observation_request: Array, connection: StreamPeerTCP) -> void:
	connection.put_32(observation_request.size())
	if Request.FRAME in observation_request:
		var frames: Dictionary = agent.rgb_cameras_data_storage
		_put_named_image("cameras", frames, connection)
	if Request.OBSTACLE_PROXEMITY in observation_request:
		var obstacle_proxemity: Dictionary = agent.parking_sensors_data_storage
		_put_json("obstacle_proxemity", obstacle_proxemity, connection)
	if Request.IS_CRASHED in observation_request:
		var is_crashed: int = agent.get_is_crashed()
		_put_int32("is_crashed", is_crashed, connection)
	if Request.STEERING in observation_request:
		var steering: float = agent.get_steering()
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

func _put_json(name: String, value: Dictionary, connection: StreamPeerTCP) -> void:
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

