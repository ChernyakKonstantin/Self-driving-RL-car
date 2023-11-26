extends Spatial
class_name GPS, "../icons/custom_node_icon.png"

func get_data() -> Dictionary:
	var data = Dictionary()
	var global_translation = get_global_translation()
	data["x"] = global_translation.x
	data["y"] = global_translation.y
	data["z"] = global_translation.z
	var global_rotation = get_global_rotation()
	data["orientation"] = global_rotation.y
	return data
