extends Node
# --------
export var address: String = "127.0.0.1"
export var port: int = 9090
export var agent_path: NodePath
# --------
enum {
	REQUEST_FRAME = 1, 
	REQUEST_DEPTH_MAP = 2,
	REQUEST_DISTANCE = 3,  # TODO: currently I think it will be distance the closest object;
	REQUEST_IS_CRASHED = 4, 
	REQUEST_WHEEL_POSITION = 5, 
	REQUEST_SPEED = 6, 
}
# --------
const FRAMES_PER_STEP = 4

const STATUS_KEY = "status"
const CONFIG_KEY = "config"
const RESET_KEY = "reset"
const ACTION_KEY = "action"
const OBSERVATION_KEY = "observation"
# --------
var counter: int = 0  # TODO: Probably delete
#var frame_counter: int = 0
#var active_physics_server: bool = false
# --------
onready var image_capture = $ImageCapture
onready var server = TCP_Server.new()
onready var agent = get_node(agent_path)
# --------
func _ready():
	print(agent_path)
#	PhysicsServer.set_active(false)
	server.listen(port, address)

func _process(delta):
	if server.is_connection_available():
		var connection: StreamPeerTCP = server.take_connection()
		handle_connection(connection)
		
#func _physics_process(delta):
#	if Input.is_action_just_pressed("move_forward"):
#		PhysicsServer.set_active(true)
#		active_physics_server = true
#
#	if active_physics_server == true:
#		counter += 1
#	if counter > FRAMES_PER_STEP:
#		PhysicsServer.set_active(false)
#		active_physics_server = false
#		counter = 0
# --------
func handle_connection(connection: StreamPeerTCP):
	var request_package_size = connection.get_available_bytes()
	print("Request size is: ", request_package_size)
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result
	var response: Dictionary = {}
	
	if request.has(STATUS_KEY):
		print("Status is requested")
		response[STATUS_KEY] = 1
	
	if request.has(ACTION_KEY):
		print("Action is requested")
		agent.perform_action(request[ACTION_KEY])
	
	if request.has(OBSERVATION_KEY):
		var observation_request = request[OBSERVATION_KEY]
		if REQUEST_FRAME in observation_request:
			response[REQUEST_FRAME] = get_frame()
		if REQUEST_DEPTH_MAP in observation_request:
			response[REQUEST_DEPTH_MAP] = get_depth_map()
		if REQUEST_DISTANCE in observation_request:
			response[REQUEST_DISTANCE] = agent.get_proxemity()
		if REQUEST_IS_CRASHED in observation_request:
			response[REQUEST_IS_CRASHED] = agent.get_is_crashed()
		if REQUEST_WHEEL_POSITION in observation_request:
			response[REQUEST_WHEEL_POSITION] = agent.get_wheel_position()
		if REQUEST_SPEED in observation_request:
			response[REQUEST_WHEEL_POSITION] = agent.get_speed()
	
	print(response)
	var json_str = JSON.print(response)
#	var response_package_size = json_str.length()
#	print("Response size is: ", request_package_size)
#	connection.put_32(response_package_size) 
	connection.put_data(json_str.to_utf8()) 

	connection.disconnect_from_host()
# --------
func perform_action(action):
	pass

func get_frame():
	return [1, ]
#	# TODO: I need to capture N frames
#	var frame_data: PoolByteArray = image_capture.get_current_frame_image_as_bytes()
#	# print(len(frame_data))
func get_depth_map():
	# TODO: implement in future
	return [2, ]



