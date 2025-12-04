from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d
import random
import math
from math import floor

app = Ursina()

# --- Visual Setup ---
window.color = color.cyan.tint(-0.2)
window.borderless = False
camera.orthographic = True
camera.fov = 20

# --- World Config ---
width = 60
depth = 40
base_height = 20
dirt_layer_thickness = 4

# --- Color Definitions ---
grass_top_color = color.rgb(34, 139, 34)    
dirt_color = color.rgb(101, 67, 33)         
stone_color = color.rgb(100, 100, 100)      
bg_dirt_color = color.rgb(60, 40, 20)       
bg_stone_color = color.black                

world_map = [[0 for y in range(depth)] for x in range(width)]

# --- Generate Static Terrain ---
surface_heights = []
for x in range(width):
    h = base_height + int(math.sin(x / 5) * 4 + math.cos(x / 3) * 2)
    surface_heights.append(h)
    for y in range(depth):
        if y < h:
            world_map[x][y] = 1

# --- Generate Static Caves ---
random.seed(42) 
for x in range(width):
    for y in range(depth):
        stone_level = surface_heights[x] - dirt_layer_thickness
        if y < stone_level: 
            cave_value = math.sin(x * 0.3) * math.cos(y * 0.2) + math.sin(x * 0.1) * math.cos(y * 0.4)
            if cave_value > 0.3:
                world_map[x][y] = 0

# --- Rendering ---
blocks = []
terrain_parent = Entity()

print("Generating World...")

background_batch = Entity(parent=terrain_parent)
foreground_batch = Entity(parent=terrain_parent)

for x in range(width):
    h = surface_heights[x]
    dirt_start_y = h - dirt_layer_thickness
    
    for y in range(depth):
        
        # --- BACKGROUND LAYER (Z = 1) ---
        if y < h:
            if y >= dirt_start_y:
                bg_col = bg_dirt_color
            else:
                bg_col = bg_stone_color
                
            Entity(
                parent=background_batch,
                model='quad',
                color=bg_col,
                position=(x, y, 1),
                scale=(1, 1)
                # TANPA texture - biarkan warna solid terlihat
            )

        # --- FOREGROUND LAYER (Z = 0) ---
        if world_map[x][y] == 1:
            if y == h - 1:
                col = grass_top_color
            elif y >= dirt_start_y:
                col = dirt_color
            else:
                col = stone_color

            b = Entity(
                parent=foreground_batch,
                model='quad', 
                color=col,
                position=(x, y, 0),
                scale=(1, 1),
                collider='box'
                # TANPA texture - biarkan warna solid terlihat
            )
            blocks.append(b)

# --- Player Setup ---
player = PlatformerController2d(scale_x=0.8, scale_y=1.4, scale_z=1) 
center_x = int(width/2)
spawn_y = surface_heights[center_x] + 4
player.position = (center_x, spawn_y)
player.color = color.orange

# Physics
player.gravity = 0.5
player.jump_height = 2
player.walk_speed = 4
player.max_fall_speed = 10

camera.add_script(SmoothFollow(target=player, offset=[0, 1, -30], speed=5))

# --- Spatial Hash ---
block_positions = set()
for block in blocks:
    block_positions.add(block.position)

# --- Game Loop ---
def update():
    player.z = 0
    
    if player.y < -10:
        player.position = (center_x, spawn_y)
        player.velocity = (0, 0)

# --- Input Handling ---
input_handler.bind('right arrow', 'd')
input_handler.bind('left arrow', 'a')
input_handler.bind('up arrow', 'space')

def input(key):
    if key == 'left mouse down':
        hit_info = mouse.hovered_entity
        if hit_info and hit_info in blocks:
            if hit_info.position in block_positions:
                block_positions.remove(hit_info.position)
            blocks.remove(hit_info)
            destroy(hit_info)
            
    if key == 'right mouse down':
        hit_info = mouse.hovered_entity
        if hit_info: 
            target_pos = hit_info.position + mouse.normal
            target_pos = (floor(target_pos.x + 0.5), floor(target_pos.y + 0.5), 0)
            
            if distance(target_pos, player.position) > 1.2:
                if target_pos not in block_positions:
                    adjacent_positions = [
                        (target_pos[0] + 1, target_pos[1], 0),
                        (target_pos[0] - 1, target_pos[1], 0),
                        (target_pos[0], target_pos[1] + 1, 0),
                        (target_pos[0], target_pos[1] - 1, 0)
                    ]
                    can_place = any(adj in block_positions for adj in adjacent_positions)
                    
                    if can_place:
                        b = Entity(
                            parent=foreground_batch,
                            model='quad',
                            color=dirt_color,
                            position=target_pos,
                            collider='box'
                            # TANPA texture
                        )
                        blocks.append(b)
                        block_positions.add(target_pos)

app.run()
