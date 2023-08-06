extends Node
class_name Communication, "icons/custom_node_icon.png"

signal got_connection
signal closed_connection

enum DataType {
	INT32 = 1
	FLOAT32 = 2
	JSON = 3
	NAMED_IMAGE = 4
}

var thread

onready var server = TCP_Server.new()
onready var connection: StreamPeerTCP
onready var have_connection: bool = false

func _init():
	_ready()

func _on_start_server(port: int, address: String):
	# Listen for incoming connections
	server.listen(port, address)
	print("Listen on address: ", address, ", port: ", port)
	
func _process(delta):
	_server_pool()

func _server_pool():
	if not have_connection and server.is_connection_available():
		connection = server.take_connection()
		var request = _read_request()
		if request != null and not request.empty():
			have_connection = true
			emit_signal("got_connection", request)
		
func _read_request() -> Dictionary:
	var request_package_size = connection.get_available_bytes()
	var request_data = connection.get_utf8_string(request_package_size)
	var request = JSON.parse(request_data).result
	return request

func put_float32(value: float, name: String) -> void:
	connection.put_string(name)  # Data name
	connection.put_32(DataType.FLOAT32)  # Data type
	connection.put_float(value)

func put_int32(value: int, name: String) -> void:
	connection.put_string(name)  # Data name
	connection.put_32(DataType.INT32)  # Data type
	connection.put_32(value)

func put_json(value, name: String) -> void:
	# value can be Array or Dictionary
	var value_: PoolByteArray = JSON.print(value).to_utf8() # Encode to bytes
	connection.put_string(name)  # Data name
	connection.put_32(DataType.JSON)  # Data type
	connection.put_32(value_.size())  # Data lenght in bytes
	connection.put_data(value_)

func put_named_image(value: Dictionary, name: String) -> void:
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

func close():
	have_connection = false
	connection.disconnect_from_host()
	emit_signal("closed_connection")
