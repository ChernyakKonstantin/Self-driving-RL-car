extends Node
# --------
export var address: String = "127.0.0.1"
export var port: int = 9090
export var agent_path: NodePath
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
onready var image_capture = $ImageCapture
onready var data_recorder = $DataRecorder
onready var server = TCP_Server.new()
onready var agent = get_node(agent_path)
# --------
func _ready():
	data_recorder.set_image_capture(image_capture)
	data_recorder.set_proxemity_capture(agent)
	# Capture data on `agent.physics_processed` signal.
	agent.connect("physics_processed", data_recorder, "capture")
	# Listen for incoming connections
	server.listen(port, address)

func _process(delta):
	if server.is_connection_available():
		var connection: StreamPeerTCP = server.take_connection()
		_handle_connection(connection)
		
# --------
func _handle_connection(connection: StreamPeerTCP) -> void:
	var request = _get_request(connection)
	
	if request.has(ACTION_KEY):
		data_recorder.clear_storage()
		agent.perform_action(request[ACTION_KEY])
		
	# Wait for agent to perform action
	yield(agent, "action_done")
	
	if request.has(OBSERVATION_KEY):
		_get_response(request[OBSERVATION_KEY], connection)
	connection.disconnect_from_host()

func _get_request(connection: StreamPeerTCP) -> Dictionary:
	var request_package_size = connection.get_available_bytes()
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result
	return request

func _get_response(observation_request: Array, connection: StreamPeerTCP) -> void:
	connection.put_32(observation_request.size())
	if Request.FRAME in observation_request:
		var frames: Dictionary = data_recorder.image_storage
		_put_named_image("cameras", frames, connection)
	if Request.OBSTACLE_PROXEMITY in observation_request:
		var obstacle_proxemity: Dictionary = data_recorder.obstacle_proxemity_storage
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
			connection.put_string(name)  # Image name
			connection.put_32(value[key].size())  # Number of images
			for image in value[key]:
				connection.put_32(image.size()) # Image length in bytes
				connection.put_data(image)
