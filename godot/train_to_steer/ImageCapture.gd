extends Node
# --------
onready var viewport = get_viewport()  # Get the current viewport
# --------
func get_current_frame() -> PoolByteArray:
	var texture_image: Image
	var frame_data: PoolByteArray

	texture_image = viewport.get_texture().get_data()
	texture_image.flip_y()
	texture_image.convert(Image.FORMAT_RGB8)
	frame_data = texture_image.get_data()
	return frame_data

# TODO: implement getting of depthmaps
