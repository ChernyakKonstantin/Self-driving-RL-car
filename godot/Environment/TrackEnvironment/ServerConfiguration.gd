extends Control

signal start_server

onready var address_input = $AddressInput
onready var port_input = $PortInput
onready var start_server_button = $StartServerButton

# Called when the node enters the scene tree for the first time.
func _ready():
	start_server_button.connect("pressed", self, "_emit_start_server_signal")
	start_server_button.set_toggle_mode(false)

func _emit_start_server_signal():
	emit_signal(
		"start_server", 
		int(port_input.get_text()),
		address_input.get_text()
		)
