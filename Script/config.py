from ursina import color

# --- WORLD SIZE ---
WIDTH = 384
DEPTH = 256
BASE_HEIGHT = 40
DIRT_LAYER_THICKNESS = 5

# --- RENDER SETTINGS ---
VIEW_DISTANCE_X = 22  
VIEW_DISTANCE_Y = 16 

# --- BLOCK ID ---
GRASS = 1
DIRT = 2
STONE = 3
BEDROCK = 4
SAND = 5
COAL = 6    
IRON = 7    
DIAMOND = 8 
GRASS_PLANT = 9
LOG = 10     
LEAVES = 11  
GLASS = 12
CRAFTING_TABLE = 13
PLANK = 14
BED_BLOCK = 15

# --- ITEM ID ---
STICK = 100
TORCH = 101
BED_ITEM = 102 
RAW_CHICKEN = 103
COOKED_CHICKEN = 104
FEATHER = 105

# MINING DROPS
COAL_ITEM = 150
IRON_INGOT = 151
DIAMOND_GEM = 152

# TOOLS - WOOD
WOODEN_SWORD = 210
WOODEN_SHOVEL = 211
WOODEN_PICKAXE = 212
WOODEN_AXE = 213

# TOOLS - IRON
IRON_SWORD = 220
IRON_SHOVEL = 221
IRON_PICKAXE = 222
IRON_AXE = 223

# TOOLS - DIAMOND
DIAMOND_SWORD = 230
DIAMOND_SHOVEL = 231
DIAMOND_PICKAXE = 232
DIAMOND_AXE = 2333

# ARMOR
IRON_HELMET = 300
IRON_CHESTPLATE = 301
IRON_LEGGINGS = 302
IRON_BOOTS = 303

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
    LEAVES: {'name': 'Oak Leaves', 'texture': '../Assets/Textures/leaves.png', 'double_sided': True, 'solid': True},
    CRAFTING_TABLE: {'name': 'Crafting Table', 'texture': '../Assets/Textures/crafting_table.png', 'solid': True},
    PLANK: {'name': 'Oak Plank', 'texture': '../Assets/Textures/plank.png', 'solid': True},
    BED_BLOCK: {'name': 'Bed', 'texture': '../Assets/Textures/bed_side.png', 'solid': True},
    STICK: {'name': 'Stick', 'texture': '../Assets/Icons/Materials/Stick.png', 'solid': False},
    BED_ITEM: {'name': 'Bed Item', 'texture': '../Assets/Icons/Furniture/Red_Bed.png', 'solid': False}, 
    RAW_CHICKEN: {'name': 'Raw Chicken', 'texture': '../Assets/Icons/Item/Raw_Chicken.png', 'solid': False},
    COOKED_CHICKEN: {'name': 'Cooked Chicken', 'texture': '../Assets/Icons/Item/Cooked_Chicken.png', 'solid': False},
    FEATHER: {'name': 'Feather', 'texture': '../Assets/Icons/Item/Feather.png', 'solid': False},

    DIAMOND_GEM: {'name': 'Diamond Gem', 'texture': '../Assets/Icons/Materials/Diamond.png', 'solid': False},
    COAL_ITEM: {'name': 'Coal Item', 'texture': '../Assets/Icons/Materials/Coal.png', 'solid': False},
    IRON_INGOT: {'name': 'Iron Ingot', 'texture': '../Assets/Icons/Materials/Iron_Ingot.png', 'solid': False},

    WOODEN_SWORD: {'name': 'Wooden Sword', 'texture': '../Assets/Icons/Equipments/Wooden_Sword.png', 'solid': False},
    WOODEN_SHOVEL: {'name': 'Wooden Shovel', 'texture': '../Assets/Icons/Equipments/Wooden_Shovel.png', 'solid': False},
    WOODEN_PICKAXE: {'name': 'Wooden Pickaxe', 'texture': '../Assets/Icons/Equipments/Wooden_Pickaxe.png', 'solid': False},
    WOODEN_AXE: {'name': 'Wooden Axe', 'texture': '../Assets/Icons/Equipments/Wooden_Axe.png', 'solid': False},
    IRON_PICKAXE: {'name': 'Iron Pickaxe', 'texture': '../Assets/Icons/Equipments/Iron_Pickaxe.png', 'solid': False},
    DIAMOND_PICKAXE: {'name': 'Diamond Pickaxe', 'texture': '../Assets/Icons/Equipments/Diamond_Pickaxe.png', 'solid': False},
}

PASSABLE_BLOCKS = (
    0,
    GRASS_PLANT,
    LOG,
    LEAVES,
    TORCH,
    BED_BLOCK,
)

# --- BG ---
BG_DIRT_COLOR = color.orange.tint(-0.8)
BG_STONE_COLOR = color.black
BG_SAND_COLOR = color.yellow.tint(-0.8)

# --- LAYERS (Z-Order) ---
BG_Z = 1.0       
PLANT_Z = 0.1    
FG_Z = 0.0       
PLAYER_VISUAL_Z = -0.1

# ==========================================
# PHYSICS & ENTITY CONFIGURATION
# ==========================================

# --- GLOBAL PHYSICS ---
GLOBAL_GRAVITY = 30
MAX_FALL_SPEED = 20

# --- PLAYER STATS ---
PLAYER_MAX_HEALTH = 100
PLAYER_WALK_SPEED = 5
PLAYER_JUMP_FORCE = 12
PLAYER_ATTACK_RANGE = 4.0

MOB_DESPAWN_RANGE = 40

# --- ZOMBIE STATS ---
ZOMBIE_MAX_HEALTH = 20
ZOMBIE_WALK_SPEED = 1.5
ZOMBIE_RUN_SPEED = 3.5
ZOMBIE_JUMP_FORCE = 8
ZOMBIE_ATTACK_RANGE = 1.2
ZOMBIE_ATTACK_COOLDOWN = 1.0
ZOMBIE_DAMAGE = 10
ZOMBIE_IDLE_MIN = 1.5       
ZOMBIE_IDLE_MAX = 3.5       
ZOMBIE_PATH_UPDATE_RATE = 0.3 
ZOMBIE_SPAWN_RATE = 3.0     

# --- CHICKEN STATS ---
CHICKEN_MAX_HEALTH = 4
CHICKEN_WALK_SPEED = 2.0
CHICKEN_RUN_SPEED = 4.0
CHICKEN_JUMP_FORCE = 8
CHICKEN_IDLE_MIN = 1.0
CHICKEN_IDLE_MAX = 3.0
CHICKEN_FLEE_DURATION = 4.0
CHICKEN_FLEE_DISTANCE = 8   # NEW: How far the chicken tries to run (blocks)
CHICKEN_SPAWN_RATE = 15.0

# --- TOOL DAMAGE VALUES ---
TOOL_DAMAGE = {
    WOODEN_SWORD: 4, 
    IRON_SWORD: 6,
    DIAMOND_SWORD: 7,
    
    WOODEN_AXE: 3, 
    IRON_AXE: 5, 
    DIAMOND_AXE: 6,
    
    WOODEN_PICKAXE: 2, 
    IRON_PICKAXE: 4, 
    DIAMOND_PICKAXE: 5,
    
    0: 1 
}