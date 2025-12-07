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
    GRASS: {'color': color.green, 'name': 'Grass'},
    DIRT:  {'color': color.orange.tint(-0.3), 'name': 'Dirt'},
    STONE: {'color': color.gray, 'name': 'Stone'},
    BEDROCK: {'color': color.black, 'name': 'Bedrock'},
}

# --- BG ---
BG_DIRT_COLOR = color.orange.tint(-0.8)
BG_STONE_COLOR = color.black

# --- LAYERS ---
BG_Z = 1
FG_Z = 0