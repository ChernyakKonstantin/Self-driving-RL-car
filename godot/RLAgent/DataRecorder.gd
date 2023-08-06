# Make sure the node is called after an object controllable by agent.

extends Node

onready var parking_sensors = $"../Sensors/ParkingSensors"
onready var rgb_cameras = $"../Sensors/RGBCameras"
onready var lidar = $"../Sensors/LIDAR"

onready var rgb_cameras_data_storage = Dictionary()
onready var parking_sensors_data_storage: = Dictionary()
onready var lidar_data_storage: = Array()

func _physics_process(_delta):
	record()

func record():
	_append_data_to_storage(
		rgb_cameras_data_storage, 
		rgb_cameras.get_data()
		)
	_append_data_to_storage(
		parking_sensors_data_storage, 
		parking_sensors.get_data()
	)
	lidar_data_storage.append((lidar.get_data()))

# -------- helpers --------
func _append_data_to_storage(storage: Dictionary, data: Dictionary) -> void:
	for key in data.keys():
		if storage.has(key):
			storage[key].append(data[key])
		else:
			storage[key] = [data[key]]

func clear_storage() -> void:
	rgb_cameras_data_storage.clear()
	parking_sensors_data_storage.clear()
	lidar_data_storage.clear()
