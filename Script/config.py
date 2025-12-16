from ursina import color

# --- WORLD SIZE ---
WIDTH = 384
DEPTH = 256
BASE_HEIGHT = 40
DIRT_LAYER_THICKNESS = 5

# --- RENDER SETTINGS ---
VIEW_DISTANCE_X = 22  
VIEW_DISTANCE_Y = 16 

# --- BLOK ID ---
GRASS = 1
DIRT = 2
STONE = 3
BEDROCK = 4
SAND = 5
COAL = 6
IRON = 7
DIAMOND = 8
GRASS_PLANT = 9
LOG = 10     # <-- Baru
LEAVES = 11  # <-- Baru

# --- DATABASE BLOCK ---
BLOCK_DATA = {
    GRASS: {'name': 'Grass', 'texture': '../Assets/Textures/grass.png'},
    DIRT:  {'name': 'Dirt', 'texture': '../Assets/Textures/dirt.png'},
    STONE: {'name': 'Stone', 'texture': '../Assets/Textures/cobblestone.png'},
    BEDROCK: {'name': 'Bedrock', 'texture': '../Assets/Textures/bedrock.png'},
    SAND: {'name': 'Sand', 'texture': '../Assets/Textures/sand.png'},
    COAL: {'name': 'Coal', 'texture': '../Assets/Textures/coal_ore.png'},
    IRON: {'name': 'Iron', 'texture': '../Assets/Textures/iron_ore.png'},
    DIAMOND: {'name': 'Diamond', 'texture': '../Assets/Textures/diamond_ore.png'},
    GRASS_PLANT: {'name': 'Grass Plant', 'texture': '../Assets/Icons/Block/Grass.png', 'double_sided': True},
    LOG: {'name': 'Oak Log',  'texture': '../Assets/Textures/log.png'},           
    LEAVES: {'name': 'Oak Leaves', 'texture': '../Assets/Textures/leaves.png', 'double_sided': True}, # Daun juga double sided
}

# --- BG ---
BG_DIRT_COLOR = color.orange.tint(-0.8)
BG_STONE_COLOR = color.black
BG_SAND_COLOR = color.yellow.tint(-0.8)

# --- LAYERS (Z-Order) ---
BG_Z = 1.0       
PLANT_Z = 0.1    
FG_Z = 0.0       
PLAYER_VISUAL_Z = -0.1

# --- GAMEPLAY ---
PLAYER_MAX_HEALTH = 100
ZOMBIE_DAMAGE = 10
ZOMBIE_ATTACK_RANGE = 1.2
ZOMBIE_ATTACK_COOLDOWN = 1.0
