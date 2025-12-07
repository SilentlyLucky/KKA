from ursina import *
from world import World
from player import Player
from config import WIDTH

app = Ursina()
window.color = color.cyan
window.borderless = False
window.title = "Mineria"


# --- Debug ---
window.show_ursina_splash = True
Entity.default_shader = None

# --- Setup Camera ---
camera.orthographic = True
camera.fov = 20

game_world = World()

center_x = int(WIDTH / 2)
spawn_y = game_world.surface_heights[center_x] + 4

player = Player(
    world_instance=game_world, 
    position=(center_x, spawn_y)
)

camera.add_script(SmoothFollow(target=player, offset=[0, 1, -30], speed=5))

mouse_catcher = Entity(
    model='quad', 
    scale=999, 
    color=color.clear, 
    z=2, 
    collider='box'
)

app.run()