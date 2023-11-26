# This module enables of several cameras located at a car.
# Put RGBCameras from GodotGymAPI framework as the `RGBCameras` children.

extends Spatial
class_name RGBCameras, "../icons/custom_node_icon.png"

func get_data():
	var result = {}
	for camera in get_children():
		result[camera.get_name()] = camera.get_data() 
	return result
