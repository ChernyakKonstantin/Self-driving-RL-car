extends VehicleBody

# -------- states --------
# Flag whether the agent has colided
onready var is_collided = false 
# Actions
onready var steering_delta: float
onready var acceleration_delta: float

# -------- parameters --------
# Maximum wheel rotational speed in revolutions per minute
var max_rpm = 500
var max_torque = 200

# -------- built-ins --------
func _ready():
	_configure_collision()
	
func _physics_process(delta):
	# I think 0.8 is cosine value of angle the wheel turn at
#	steering = lerp(steering, Input.get_axis("move_right", "move_left") * 0.8, 5*delta)
	steering = lerp(steering, steering_delta * 0.8, 5*delta)
#	var acceleration = Input.get_axis("move_backward", "move_forward")
	var acceleration = acceleration_delta
	var rpm
	rpm = $back_left_wheel.get_rpm()
	$back_left_wheel.engine_force = acceleration * max_torque * (1 - rpm / max_rpm)
	rpm = $back_right_wheel.get_rpm()
	$back_right_wheel.engine_force = acceleration * max_torque * (1 - rpm / max_rpm)
	brake = Input.get_action_strength("break") * 200
		
	steering_delta = 0
	acceleration_delta = 0

# -------- configurators --------
func _configure_collision():
	set_contact_monitor(true)
	set_max_contacts_reported(4)
	connect("body_entered", self, "_on_collision")
	
# -------- getters --------
func get_is_crashed() -> bool:
	return is_collided

func get_steering() -> float:
	return steering
	
func get_speed() -> float:
	return $back_left_wheel.engine_force
	
# -------- events --------
func _on_collision(_body):
	is_collided = true

