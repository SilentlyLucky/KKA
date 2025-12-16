from ursina import color

# --- WORLD SIZE ---
WIDTH = 384
DEPTH = 256
BASE_HEIGHT = 40
DIRT_LAYER_THICKNESS = 5

# --- RENDER SETTINGS ---
VIEW_DISTANCE_X = 22  
VIEW_DISTANCE_Y = 16 

# --- BLOK ID (BLOCKS - PLACEABLE) ---
GRASS = 1
DIRT = 2
STONE = 3
BEDROCK = 4
SAND = 5
COAL_ORE = 6    # Ubah nama agar jelas ini ORE
IRON_ORE = 7    # Ubah nama agar jelas ini ORE
DIAMOND_ORE = 8 # Ubah nama agar jelas ini ORE
GRASS_PLANT = 9
LOG = 10     
LEAVES = 11  
GLASS = 12
CRAFTING_TABLE = 13
PLANK = 14
BED_BLOCK = 15 # Blok tempat tidur yang sudah ditaruh (Head/Foot bisa kompleks, kita simplifikasi 1 blok dulu atau item saja)

# Alias untuk kompatibilitas kode lama (sementara)
COAL = COAL_ORE
IRON = IRON_ORE
DIAMOND = DIAMOND_ORE

# --- ITEM ID (ITEMS - NON-PLACEABLE / SPECIAL) ---
STICK = 100
TORCH = 101
BED_ITEM = 102 # Item tempat tidur di tangan
RAW_CHICKEN = 103
COOKED_CHICKEN = 104
FEATHER = 105

# MINING DROPS (Non-placeable items)
COAL_ITEM = 150
IRON_INGOT = 151
DIAMOND_GEM = 152

# TOOLS - WOOD
WOODEN_SWORD = 200
WOODEN_SHOVEL = 201
WOODEN_PICKAXE = 202
WOODEN_AXE = 203

# TOOLS - STONE
STONE_SWORD = 210
STONE_SHOVEL = 211
STONE_PICKAXE = 212
STONE_AXE = 213

# TOOLS - IRON
IRON_SWORD = 220
IRON_SHOVEL = 221
IRON_PICKAXE = 222
IRON_AXE = 223

# TOOLS - DIAMOND
DIAMOND_SWORD = 230
DIAMOND_SHOVEL = 231
DIAMOND_PICKAXE = 232
DIAMOND_AXE = 233

# ARMOR - IRON
IRON_HELMET = 300
IRON_CHESTPLATE = 301
IRON_LEGGINGS = 302
IRON_BOOTS = 303

# ARMOR - DIAMOND
DIAMOND_HELMET = 310
DIAMOND_CHESTPLATE = 311
DIAMOND_LEGGINGS = 312
DIAMOND_BOOTS = 313


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
    CRAFTING_TABLE: {'name': 'Crafting Table'},
    PLANK: {'name': 'Oak Plank'},
    BED_BLOCK: {'name': 'Bed'}, # Visual di world
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
