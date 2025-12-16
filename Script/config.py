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
