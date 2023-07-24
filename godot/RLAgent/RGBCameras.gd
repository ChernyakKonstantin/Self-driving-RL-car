extends Spatial
		
func get_data():
	var result = {}
	for camera in get_children():
		result[camera.get_name()] = camera.get_data() 
	return result
