extends Spatial

export var max_distance: float = 2.0  # TODO: make configurable

func _ready():
	for ray in get_children():
		ray.set_enabled(true)
		ray.set_exclude_parent_body(true)
		ray.set_collide_with_bodies(true)
		ray.set_collide_with_areas(false)
		ray.set_cast_to(Vector3(0, 0, max_distance))

func get_data() -> Dictionary:
	var result = {}
	for ray in get_children():
		if ray.is_colliding():
			var collison_point = ray.get_collision_point()
			result[ray.name] = ray.global_translation.distance_to(collison_point)
		else:
			 result[ray.name] = max_distance
	return result
