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
TORCH = 6
COAL = 7
IRON = 8
DIAMOND = 9
GRASS_PLANT = 10
LOG = 11     # <-- Baru
LEAVES = 12  # <-- Baru

# --- DATABASE BLOCK ---
BLOCK_DATA = {
    GRASS: {'name': 'Grass', 'texture': '../Assets/Textures/grass.png', 'solid': True},
    DIRT:  {'name': 'Dirt', 'texture': '../Assets/Textures/dirt.png', 'solid': True},
    STONE: {'name': 'Stone', 'texture': '../Assets/Textures/cobblestone.png', 'solid': True},
    BEDROCK: {'name': 'Bedrock', 'texture': '../Assets/Textures/bedrock.png', 'solid': True},
    SAND: {'name': 'Sand', 'texture': '../Assets/Textures/sand.png', 'solid': True},
    COAL: {'name': 'Coal', 'texture': '../Assets/Textures/coal_ore.png', 'solid': True},
    IRON: {'name': 'Iron', 'texture': '../Assets/Textures/iron_ore.png', 'solid': True},
    DIAMOND: {'name': 'Diamond', 'texture': '../Assets/Textures/diamond_ore.png', 'solid': True},
    TORCH: {'name': 'Torch', 'texture': '../Assets/Icons/Furniture/Torch.png', 'emits_light': True, 'solid': False, 'light_level': 15},
    GRASS_PLANT: {'name': 'Grass Plant', 'texture': '../Assets/Icons/Block/Grass.png', 'double_sided': True, 'solid': True},
    LOG: {'name': 'Oak Log',  'texture': '../Assets/Textures/log.png', 'solid': True},           
    LEAVES: {'name': 'Oak Leaves', 'texture': '../Assets/Textures/leaves.png', 'double_sided': True, 'solid': True}, # Daun juga double sided
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
