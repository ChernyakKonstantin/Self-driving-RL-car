extends Node
# --------
export var viewport_storage_path: NodePath
# --------
onready var viewports: Array = []
# --------
func _ready():
	_set_viewports(get_node(viewport_storage_path))

func _recursive_search(source: Node, target_type, storage: Array) -> void:
	for node in source.get_children():
		if node is target_type:
			storage.append(node)
		if node.get_children().size() > 0:
			_recursive_search(node, target_type, storage)

func _set_viewports(viewport_storage: Node) -> void:
	_recursive_search(viewport_storage, Viewport, viewports)
# --------
func get_viewport_frame(viewport: Viewport) -> PoolByteArray:
	var texture_image: Image
	var frame_data: PoolByteArray

	texture_image = viewport.get_texture().get_data()
	texture_image.flip_y()
	texture_image.convert(Image.FORMAT_RGB8)
	frame_data = texture_image.get_data()
	return frame_data

func get_frame() -> Dictionary:
	var viewports_frame = {}
	for viewport in viewports:
		var frame: PoolByteArray = get_viewport_frame(viewport)
		viewports_frame[viewport.name] = frame
	return viewports_frame

#func get_frame() -> PoolByteArray:
#	var viewports_frame = PoolByteArray()
#	for viewport in viewports:
#		var frame: PoolByteArray = get_viewport_frame(viewport)
#		viewports_frame.append_array(frame)
#		print(viewports_frame.size())
#	print()
#	return viewports_frame

# TODO: implement getting of depthmaps
