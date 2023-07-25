extends Spatial

onready var initial_positions: Array = $InitialPositions.get_children()

func sample_initial_position() -> Position3D:
	return initial_positions[randi() % initial_positions.size()]

func reset():
	pass
