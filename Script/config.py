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
TORCH = 9

# --- DATABASE BLOCK ---
BLOCK_DATA = {
    GRASS: {'color': color.green, 'solid': True, 'name': 'Grass'},
    DIRT:  {'color': color.orange.tint(-0.3), 'solid': True, 'name': 'Dirt'},
    STONE: {'color': color.gray, 'solid': True, 'name': 'Stone'},
    BEDROCK: {'color': color.black, 'name': 'Bedrock', 'solid': True},
    TORCH: {'color': color.pink, 'name': 'Torch', 'emits_light': True, 'solid': False, 'light_level': 15},
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