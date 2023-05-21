extends Node
# --------
export(String) var address = "127.0.0.1"
export(int) var port = 9090
# --------
enum {
	REQUEST_FRAME = 1, 
	REQUEST_DEPTH_MAP = 2,
	REQUEST_DISTANCE = 3,  # TODO: currently I think it will be distance the closest object;
	REQUEST_IS_CRASHED = 4, 
	REQUEST_WHEEL_POSITION = 5, 
}
# --------
var counter: int = 0  # TODO: Probably delete
# --------
onready var image_capture = $ImageCapture
onready var server = TCP_Server.new()
onready var player = $"../Player"
# --------
func _ready():
	server.listen(port, address)
	

func _process(delta):
	if server.is_connection_available():
		var connection: StreamPeerTCP = server.take_connection()
		handle_connection(connection)

# --------
func handle_connection(connection: StreamPeerTCP):
	var request_package_size = connection.get_available_bytes()
	print("Request size is: ", request_package_size)
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result

	if request.has("action"):
		perform_action(request["action"])
	
	var response: Dictionary = {}
	
	if request.has("observation"):
		var observation_requests = request["observation"]
		if REQUEST_FRAME in observation_requests:
			response[REQUEST_FRAME] = get_frame()
		if REQUEST_DEPTH_MAP in observation_requests:
			response[REQUEST_DEPTH_MAP] = get_depth_map()
		if REQUEST_DISTANCE in observation_requests:
			response[REQUEST_DISTANCE] = get_distance()
		if REQUEST_IS_CRASHED in observation_requests:
			response[REQUEST_IS_CRASHED] = get_is_crashed()
		if REQUEST_WHEEL_POSITION in observation_requests:
			response[REQUEST_WHEEL_POSITION] = get_wheel_position()
	
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
func get_distance():
	return [3, ]
func get_is_crashed():
	return [4, ]
func get_wheel_position():
	return [5, ]	


