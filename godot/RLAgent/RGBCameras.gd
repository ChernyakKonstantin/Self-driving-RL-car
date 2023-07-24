extends Spatial

# TODO: try not to use auxialary remote transofrm and use remote transform from the camera
func _ready():
	for camera_placeholder in get_children():
		var camera = camera_placeholder.get_child(0)
		camera.set_name(camera_placeholder.get_name())
		camera.set_remote_transform(camera_placeholder)
		
func get_data():
	var result = {}
	for camera_placeholder in get_children():
		var camera = camera_placeholder.get_child(0)
		result[camera.get_name()] = camera.get_data() 
	return result
