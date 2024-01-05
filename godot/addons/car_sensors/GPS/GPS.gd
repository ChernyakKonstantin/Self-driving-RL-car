extends Spatial
class_name GPS, "../icons/custom_node_icon.png"

func get_data() -> Dictionary:
	var coordinates = Dictionary()
	var global_translation = get_global_translation()
	coordinates["location"] = Dictionary()
	coordinates["location"]["x"] = global_translation.x
	coordinates["location"]["y"] = global_translation.y
	coordinates["location"]["z"] = global_translation.z
	var global_rotation = get_global_rotation()
	coordinates["rotation"] = Dictionary()
	coordinates["rotation"]["x"] = global_rotation.x
	coordinates["rotation"]["y"] = global_rotation.y
	coordinates["rotation"]["z"] = global_rotation.z
	return coordinates
