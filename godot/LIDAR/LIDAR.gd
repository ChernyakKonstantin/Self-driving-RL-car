# LIDAR orientation is along X-axis.

extends Spatial

export var horizontal_resolution: float = 1 # Degrees
export var vertical_resolution: float = 1 # Degrees
export var horizontal_fov: float = 120 # Degrees
export var vertical_fov: float = 60 # Degrees
export var ray_max_len: float = 100 # Meters

func _ready():
	_create()

func _create() -> void:
	var start_h: float = -horizontal_fov / 2
	var start_v: float = -vertical_fov / 2
	var n_vertical_points = int(vertical_fov / vertical_resolution)
	var n_horizontal_points = int(horizontal_fov / horizontal_resolution)

#	assert(fmod(vertical_fov, vertical_resolution) == 0, str(vertical_fov / vertical_resolution))
#	assert(fmod(horizontal_fov, horizontal_resolution) == 0, str(horizontal_fov / horizontal_resolution))
	for j in range(n_vertical_points):
		for i in range(n_horizontal_points):
			var ray = RayCast.new()
			ray.set_enabled(true)
			ray.set_exclude_parent_body(true)
			ray.set_collide_with_bodies(true)
			ray.set_collide_with_areas(false)
			ray.set_cast_to(Vector3(0, 0, ray_max_len))
			var rotation = Vector3(
				start_v + j * vertical_resolution,
				start_h + i * horizontal_resolution,
				0
			)
			ray.set_rotation_degrees(rotation)
			add_child(ray)

func get_data() -> Array:
	var distances = []
	for ray in get_children():
		var rotation: Vector3 = ray.get_rotation_degrees()
		var distance: float = ray_max_len
		if ray.is_colliding():
			distance = ray.global_translation.distance_to(ray.get_collision_point())
		distances.append([float(rotation.y), float(rotation.x), float(distance)])
	return distances



