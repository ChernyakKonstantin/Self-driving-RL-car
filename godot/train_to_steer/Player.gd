extends VehicleBody

export var camera_storage_path: NodePath

# Flag whether the agent has colided
onready var is_collided = false 
# Flag whether to compute the agent movements
onready var enabled: bool = false
# Distance sensors proxemity
onready var max_distance_sensor_proxemity: float = 1.0  # TODO: make configurable

onready var DistanceSensors = $DistanceSensors
onready var CameraPlaceholders = $CameraPlaceholders
# --------
# Maximum wheel rotational speed in revolutions per minute
var max_rpm = 500
var max_torque = 200
# --------
func _ready():
	_configure_collision()
	_configure_distance_sensors()
	_configure_cameras()
	
func _physics_process(delta):

	# I think 0.4 is cosine value of angle the wheel turn at
	steering = lerp(steering, Input.get_axis("move_right", "move_left") * 0.8, 5*delta)
	var acceleration = Input.get_axis("move_backward", "move_forward")
	var rpm
	rpm = $back_left_wheel.get_rpm()
	$back_left_wheel.engine_force = acceleration * max_torque * (1 - rpm / max_rpm)
	rpm = $back_right_wheel.get_rpm()
	$back_right_wheel.engine_force = acceleration * max_torque * (1 - rpm / max_rpm)
	brake = Input.get_action_strength("break") * 200

# --------
func _configure_collision():
	set_contact_monitor(true)
	set_max_contacts_reported(4)

func _configure_distance_sensors():
	for ray in DistanceSensors.get_children():
		ray.set_enabled(true)
		ray.set_exclude_parent_body(true)
		ray.set_collide_with_bodies(true)
		ray.set_collide_with_areas(false)
		ray.set_cast_to(Vector3(0, -max_distance_sensor_proxemity, 0))

func _configure_cameras():
	var camera_storage = get_node(camera_storage_path)
	for placeholder in CameraPlaceholders.get_children():
		# TODO: remove hard-code with Camera keuword and use types
		var camera = camera_storage.find_node(placeholder.name + "Camera")
		placeholder.set_remote_node(camera.get_path())
#

# --------
func get_proxemity() -> Dictionary:
	# Return dictionary of distances from sensors
	var proxemities = {}
	for ray in DistanceSensors.get_children():
		var proxemity: float = max_distance_sensor_proxemity
		if ray.is_colliding():
			proxemity = ray.global_translation.distance_to(ray.get_collision_point())
		proxemities[ray.name] = proxemity 
	return proxemities
	
func get_is_crashed() -> bool:
	return is_collided

func get_wheel_position() -> float:
	return steering
	
func get_speed() -> float:
	return $back_left_wheel.engine_force
# --------
func _on_Player_body_entered(body):
	is_collided = true

