extends RLEnvironment

# --------
onready var server_configuration = $GUI/ServerConfiguration
onready var gui = $GUI

# -------- built-ins --------
func _ready():
	world = $World
	agent = $RLCarAgent
	server_configuration.connect("start_server", communication, "start_server")
	# GUI is not pausable
	gui.set_pause_mode(2)
	# Agent and World is pausable.
	world.set_pause_mode(1)
	agent.set_pause_mode(1)

func _reset():
	world.reset()
	agent.reset(world.sample_initial_position())
	for _i in range(repeat_action):
		agent.data_recorder.record()
	
func _step(action):
	yield(._step(action), "completed")
	gui.set_steering_wheel_angle(agent.car.relative_steering)

func _after_send_response():
	agent.data_recorder.clear_storage()
