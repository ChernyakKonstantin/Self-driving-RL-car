extends Node
# --------
export var address: String = "127.0.0.1"
export var port: int = 9090
export var agent_path: NodePath
# --------
enum {
	REQUEST_FRAME = 1, 
	REQUEST_IS_CRASHED = 2, 
	REQUEST_WHEEL_POSITION = 3,
	REQUEST_SPEED = 4, 
	# Distance the closest object;
	REQUEST_OBSTACLE_PROXEMITY = 5,  
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
onready var data_recorder = $DataRecorder
onready var server = TCP_Server.new()
onready var agent = get_node(agent_path)
# --------
func _ready():
#	PhysicsServer.set_active(false)
	data_recorder.set_image_capture(image_capture)
	data_recorder.set_proxemity_capture(agent)
	server.listen(port, address)

func _process(delta):
	if server.is_connection_available():
		var connection: StreamPeerTCP = server.take_connection()
		handle_connection(connection)
		
# --------
func handle_connection(connection: StreamPeerTCP) -> void:
	# TODO: update code to send proxemitites and frames from DataRecorder
	# TODO: add datatype to begging of response
	var request_package_size = connection.get_available_bytes()
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result
	if request.has(STATUS_KEY):
		connection.put_32(1) # TODO: use enum for status
	elif request.has(ACTION_KEY):
		# TODO: data should be captured during action
		# TODO: I think PhysicsServer should be handled outside of player
		data_recorder.clear_storage()
		agent.perform_action(request[ACTION_KEY])  
		connection.put_32(1) # TODO: use enum for status
	elif request.has(OBSERVATION_KEY):
		var observation_request = request[OBSERVATION_KEY]
		if observation_request == REQUEST_FRAME:
			var frames: Array = data_recorder.image_storage
			print("Number of frames ", frames.size())
			for frame in frames:
				for key in frame.keys():
					connection.put_string(key)
					connection.put_u32(frame[key].size())
					connection.put_data(frame[key])
#		elif observation_request == REQUEST_DEPTH_MAP:
#			pass  # TODO
		elif observation_request == REQUEST_OBSTACLE_PROXEMITY:
			var response: Dictionary = agent.get_proxemity()
			print("Proxemity ", response)
			connection.put_data(JSON.print(response).to_utf8())
		elif observation_request == REQUEST_IS_CRASHED:
			var response: int = agent.get_is_crashed()
			print("Is crashed ", response)
			connection.put_32(response)  # int32
		elif observation_request == REQUEST_WHEEL_POSITION:
			var response: float = agent.get_wheel_position()
			print("Wheel position ", response)
			connection.put_float(response)  # float32
		elif observation_request == REQUEST_SPEED:
			var response: float = agent.get_speed()
			print("Speed ", response)
			connection.put_float(response)  # float32
	connection.disconnect_from_host()
# --------
func get_depth_map():
	# TODO: implement in future
	return [2, ]



