from ursina import color

# --- WORLD ---
WIDTH = 60
DEPTH = 40
BASE_HEIGHT = 20
DIRT_LAYER_THICKNESS = 4

# --- BLOK ID ---
GRASS = 1
DIRT = 2
STONE = 3
BEDROCK = 4
SAND = 5
COAL = 6
IRON = 7
DIAMOND = 8
TORCH = 9

# --- DATABASE BLOCK ---
# BLOCK_DATA = {
#     GRASS: {'color': color.green, 'solid': True, 'name': 'Grass'},
#     DIRT:  {'color': color.orange.tint(-0.3), 'solid': True, 'name': 'Dirt'},
#     STONE: {'color': color.gray, 'solid': True, 'name': 'Stone'},
#     BEDROCK: {'color': color.black, 'name': 'Bedrock', 'solid': True},
#     TORCH: {'color': color.pink, 'name': 'Torch', 'emits_light': True, 'solid': False, 'light_level': 15},
# }

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
}

# --- BG ---
BG_DIRT_COLOR = color.orange.tint(-0.8)
BG_STONE_COLOR = color.black

# --- LAYERS ---
BG_Z = 1
FG_Z = 0

# --- GAMEPLAY ---
PLAYER_MAX_HEALTH = 100
ZOMBIE_DAMAGE = 10
ZOMBIE_ATTACK_RANGE = 1.2
ZOMBIE_ATTACK_COOLDOWN = 1.0
