# LIDAR orientation is along X-axis.

extends Spatial

export var horizontal_resolution: float = 0.1 # Degrees
export var vertical_resolution: float = 0.1 # Degrees
export var horizontal_fov: float = 360 # Degrees
export var vertical_fov: float = 90 # Degrees
export var ray_max_len: int = 1000 # Meters

func _ready():
	_create()

func _create() -> void:
	var start_h = -horizontal_fov / 2
	var start_v = -horizontal_fov / 2
	
#	assert(fmod(vertical_fov, vertical_resolution) == 0, str(vertical_fov / vertical_resolution))
#	assert(fmod(horizontal_fov, horizontal_resolution) == 0, str(horizontal_fov / horizontal_resolution))
	for j in range(int(vertical_fov / vertical_resolution)):
		for i in range(int(horizontal_fov / horizontal_resolution)):
			var ray = RayCast.new()
			ray.set_enabled(true)
			ray.set_exclude_parent_body(true)
			ray.set_collide_with_bodies(true)
			ray.set_collide_with_areas(false)
			ray.set_cast_to(Vector3(ray_max_len, 0, 0))
			var rotation = Vector3(
				0,
				start_h + i * horizontal_resolution,
				start_v + i * vertical_resolution
			)
			ray.set_rotation_degrees(rotation)
			add_child(ray)

func get_distances() -> Array:
	var distances = []
	for ray in get_children():
		var distance: float = ray_max_len
		if ray.is_colliding():
			distance = ray.global_translation.distance_to(ray.get_collision_point())
		distances.append(distance)
	return distances



