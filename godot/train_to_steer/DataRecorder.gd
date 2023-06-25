extends Node
# --------
var image_capture
var proxemity_capture
# --------
# Array of dictionaries
onready var image_storage = Dictionary() 
# Array of dictionaries
onready var obstacle_proxemity_storage: = Dictionary()
# --------
func set_proxemity_capture(node: Node) -> void:
	proxemity_capture = node
	
func set_image_capture(node: Node) -> void:
	image_capture = node
	
# --------
func capture() -> void:
	_append_record(image_storage, image_capture.get_frame())
	_append_record(obstacle_proxemity_storage, proxemity_capture.get_proxemity())

func _append_record(storage: Dictionary, data: Dictionary) -> void:
	for key in data.keys():
		if storage.has(key):
			storage[key].append(data[key])
		else:
			storage[key] = [data[key]]

func clear_storage() -> void:
	image_storage.clear()
	obstacle_proxemity_storage.clear()
