extends Node

const ACTION_REQUEST = 1
const GREETING_REQUEST = 2

# Set the address and port of the TCP server
export(String) var address = "127.0.0.1"
export(int) var port = 9090
var counter: int = 0

# Get the current viewport
onready var viewport = get_viewport()
onready var wait_for_response: bool
onready var player = $"../Player"
#func _ready():
#	server.listen(9000)
#	socket.connect_to_host(address, port)


func _process(delta):
	var socket = StreamPeerTCP.new()
	socket.connect_to_host(address, port)
	socket.put_32(ACTION_REQUEST) 
	var response = socket.get_32()
	if response != 0:
		if response == 1:
			player._x = 1
		elif response == 2:
			player._x = -1
		elif response == 3:
			player._z = 1
		elif response == 4:
			player._z = -1
	else:
		counter = counter + 1
		print("No response #", counter)
	socket.disconnect_from_host()
	
	
##	send_image(get_current_frame_image_as_bytes())
#	if not wait_for_response:
#		var dictionary = {
#			"name": "John",
#			"age": 30,
#			"is_male": true,
#			"scores": [80, 90, 95],
#			"data": PoolByteArray([0x01, 0x02, 0x03, 0x04])
#		}
#		var json_str = JSON.print(dictionary)
#		socket.connect_to_host(address, port)
#		socket.put_32(json_str.length()) 
#		socket.put_data(json_str.to_utf8()) 
#		socket.put_32(dictionary["data"].size()) 
#		socket.put_data(dictionary["data"])
#		socket.disconnect_from_host()
#		print("Data is sent")
#		wait_for_response = true
#	if wait_for_response:
#		var client = server.take_connection()
#		if client:
#			var action = client.get_32()
#			print(action)
#			wait_for_response = false
		
#func get_current_frame_image_as_bytes() -> PoolByteArray:
#	var texture_image: Image
#	var frame_data: PoolByteArray
#
#	texture_image = viewport.get_texture().get_data()
#	texture_image.flip_y()
#	texture_image.convert(Image.FORMAT_RGB8)
#	frame_data = texture_image.get_data()
#	return frame_data
#
#func send_image(frame_data: PoolByteArray) -> void:
#	socket.connect_to_host(address, port)
#	print(len(frame_data))
#	socket.put_var(frame_data)
#	socket.disconnect_from_host()
