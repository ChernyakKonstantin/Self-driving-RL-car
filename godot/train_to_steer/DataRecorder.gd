extends Node
# --------
var image_capture
var proxemity_capture
# --------
# Array of dictionaries
onready var image_storage: Array = Array() 
# Array of dictionaries
onready var obstacle_proxemity_storage: Array = Array()
# --------
func set_proxemity_capture(node: Node) -> void:
	proxemity_capture = node
	
func set_image_capture(node: Node) -> void:
	image_capture = node
# --------
func _on_Player_physics_processed() -> void:
	image_storage.append(image_capture.get_frame())
	obstacle_proxemity_storage.append(proxemity_capture.get_proxemity())

func clear_storage() -> void:
	image_storage.clear()
	obstacle_proxemity_storage.clear()
