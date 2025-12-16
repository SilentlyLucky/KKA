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

# --- DATABASE BLOCK ---
BLOCK_DATA = {
    GRASS: {'name': 'Grass', 'texture': '../Assets/Texture/grass_block_side_1024x1024.png'},
    DIRT:  {'name': 'Dirt', 'texture': '../Assets/Texture/dirt_1024x1024.png'},
    STONE: {'name': 'Stone', 'texture': '../Assets/Texture/cobblestone_1024x1024.png'},
    BEDROCK: {'name': 'Bedrock', 'texture': '../Assets/Texture/bedrock_1024x1024.png'},
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