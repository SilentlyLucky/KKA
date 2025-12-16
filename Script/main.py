from ursina import *
from world import World
from player import Player
from mob import Zombie  # <--- IMPORT ZOMBIE
from config import WIDTH
from zombie_spawner import ZombieSpawner

# --- Setup App ---
app = Ursina()
window.color = color.cyan
window.borderless = False
window.title = "Minecraft 2D - Zombie AI"

# --- Setup Camera ---
camera.orthographic = True
camera.fov = 20

# --- Load Modules ---
game_world = World()

center_x = int(WIDTH / 2)
spawn_y = game_world.surface_heights[center_x] + 4

player = Player(
    world_instance=game_world, 
    position=(center_x, spawn_y)
)

zombie_spawner = ZombieSpawner(game_world, player)

def update():
    zombie_spawner.update()

# --- SPAWN ZOMBIE ---
# We spawn him slightly to the right of the player
# zombie = Zombie(
#     world=game_world, 
#     player=player, 
#     position=(center_x + 5, spawn_y + 5)
# )

# --- Camera Follow ---
camera.add_script(SmoothFollow(target=player, offset=[0, 1, -30], speed=5))

# --- Mouse Catcher ---
mouse_catcher = Entity(
    model='quad', 
    scale=999, 
    color=color.clear, 
    z=2, 
    collider='box'
)

# --- Run Game ---
app.run()