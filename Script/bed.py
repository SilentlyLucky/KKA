from ursina import *
from config import *

def set_spawn_point(player, position):
    """Set spawn point pemain ke posisi ini"""
    print(f"Spawn point set to {position}")
    player.spawn_x = position[0]
    player.spawn_y = position[1] + 1
    
    if hasattr(player.world, "save_system"):
        player.world.save_system.save_spawn_point(
            (player.spawn_x, player.spawn_y)
        )
    
    t = Text(text="Spawn Point Set!", position=(0, 0), origin=(0,0), scale=2, color=color.green)
    destroy(t, delay=2)