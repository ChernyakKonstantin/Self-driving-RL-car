extends Spatial


onready var view = $CameraViews
onready var texture_left = $ViewportLeft.get_texture()
onready var texture = $ViewportRight.get_texture()



func _ready():
#	view.material.set_shader_param("viewport_left", viewport_left.get_texture())
#	view.material.set_shader_param("viewport_right", viewport_right.get_texture())
	view.texture = ViewportTexture.new()
	view.texture.blit(
		viewport_left.get_texture(),
		Vector2(0, 0))
	view.texture.blit(
		viewport_right.get_texture(), 
		Vector2(viewport_left.get_texture().get_width(), 0))
get_texture()
