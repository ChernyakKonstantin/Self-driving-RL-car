extends VehicleBody

## How fast the player moves in meters per second.
#export var speed = 14
## The downward acceleration when in the air, in meters per second squared.
#export var fall_acceleration = 75
#
#var velocity = Vector3.ZERO
#
#var _x: int = 0
#var _z: int = 0

# Maximum wheel rotational speed in revolutions per minute
var max_rpm = 500
var max_torque = 200


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
#	if Input.is_action_pressed("move_right"):
#		direction.x += 1
#	if Input.is_action_pressed("move_left"):
#		direction.x -= 1
#	if Input.is_action_pressed("move_backward"):
#		direction.z += 1
#	if Input.is_action_pressed("move_forward"):
#		direction.z -= 1
#
#	direction.x += _x
#	direction.z += _z
#	_x = 0
#	_z = 0
#
#	if direction != Vector3.ZERO:
#		direction = direction.normalized()
#		$Pivot.look_at(translation + direction, Vector3.UP)
#
#	velocity.x = direction.x * speed
#	velocity.z = direction.z * speed
#	velocity.y -= fall_acceleration * delta
#	velocity = move_and_slide(velocity, Vector3.UP)


