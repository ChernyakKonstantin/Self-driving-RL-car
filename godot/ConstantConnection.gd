extends Node


onready var server = TCP_Server.new()
onready var have_connection: bool = false
onready var connection: StreamPeerTCP
onready var request_package_size: int

# Called when the node enters the scene tree for the first time.
func _ready():
	server.listen(9090, "127.0.0.1")


func _physics_process(_delta):
	if not have_connection:
		if server.is_connection_available():
			print("Got connection")
			connection = server.take_connection()
			have_connection = true
	elif connection.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		request_package_size = connection.get_available_bytes()
		if request_package_size > 0:
			print(request_package_size)
			print(connection.get_string(request_package_size))
		if Input.is_action_just_released("ui_down"):
			print("Put var")
			connection.put_data(PoolByteArray([10, 2, 3]))
	else:
		have_connection = false
		
