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

# --- ITEM ID (ITEMS - NON-PLACEABLE / SPECIAL) ---
STICK = 100
TORCH = 101
BED_ITEM = 102 # Item tempat tidur di tangan
CHICKEN = 103
COOKED_CHICKEN = 104
FEATHER = 105

# MINING DROPS (Non-placeable items)
COAL= 150
IRON = 151
DIAMOND = 152

# TOOLS - WOOD
WOODEN_SWORD = 200
WOODEN_SHOVEL = 201
WOODEN_PICKAXE = 202
WOODEN_AXE = 203

# TOOLS - WOODEN
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

# ARMOR - IRON
IRON_HELMET = 300
IRON_CHESTPLATE = 301
IRON_LEGGINGS = 302
IRON_BOOTS = 30

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
    COAL_ORE: {'name': 'Coal', 'texture': '../Assets/Textures/coal_ore.png', 'solid': True},
    IRON_ORE: {'name': 'Iron', 'texture': '../Assets/Textures/iron_ore.png', 'solid': True},
    DIAMOND_ORE: {'name': 'Diamond', 'texture': '../Assets/Textures/diamond_ore.png', 'solid': True},
    TORCH: {'name': 'Torch', 'texture': '../Assets/Icons/Furniture/Torch.png', 'emits_light': True, 'solid': False, 'light_level': 15},
    GRASS_PLANT: {'name': 'Grass Plant', 'texture': '../Assets/Icons/Block/Grass.png', 'double_sided': True, 'solid': True},
    LOG: {'name': 'Oak Log',  'texture': '../Assets/Textures/log.png', 'solid': True},           
    LEAVES: {'name': 'Oak Leaves', 'texture': '../Assets/Textures/leaves.png', 'double_sided': True, 'solid': True},
    CRAFTING_TABLE: {'name': 'Crafting Table', 'texture': '../Assets/Textures/crafting_table.png', 'solid': True},
    PLANK: {'name': 'Oak Plank', 'texture': '../Assets/Textures/plank.png', 'solid': True},
    BED_BLOCK: {'name': 'Bed', 'texture': '../Assets/Textures/bed_side.png', 'solid': True}, # Visual di world
    STICK: {'name': 'Stick', 'texture': '../Assets/Icons/Materials/Stick.png', 'solid': False},
    BED_ITEM: {'name': 'Bed Item', 'texture': '../Assets/Icons/Furniture/Red_Bed.png', 'solid': False}, # Item tempat tidur di tangan
    CHICKEN: {'name': 'Chicken', 'texture': '../Assets/Icons/Food/Chicken.png', 'solid': False},
    COOKED_CHICKEN: {'name': 'Cooked Chicken', 'texture': '../Assets/Icons/Item/Cooked_Chicken.png', 'solid': False},
    FEATHER: {'name': 'Feather', 'texture': '../Assets/Icons/Materials/Feather.png', 'solid': False},

    DIAMOND: {'name': 'Diamond Gem', 'texture': '../Assets/Icons/Materials/Diamond.png', 'solid': False},
    COAL: {'name': 'Coal Item', 'texture': '../Assets/Icons/Materials/Coal.png', 'solid': False},
    IRON: {'name': 'Iron Ingot', 'texture': '../Assets/Icons/Materials/Iron_Ingot.png', 'solid': False},

    DIAMOND_HELMET: {'name': 'Diamond Helmet', 'texture': '../Assets/Icons/Equipments/Diamond_Helmet.png', 'solid': False},
    DIAMOND_CHESTPLATE: {'name': 'Diamond Chestplate', 'texture': '../Assets/Icons/Equipments/Diamond_Chestplate.png', 'solid': False},
    DIAMOND_LEGGINGS: {'name': 'Diamond Leggings', 'texture': '../Assets/Icons/Equipments/Diamond_Leggings.png', 'solid': False},
    DIAMOND_BOOTS: {'name': 'Diamond Boots', 'texture': '../Assets/Icons/Equipments/Diamond_Boots.png', 'solid': False},
    IRON_HELMET: {'name': 'Iron Helmet', 'texture': '../Assets/Icons/Equipments/Iron_Helmet.png', 'solid': False},
    IRON_CHESTPLATE: {'name': 'Iron Chestplate', 'texture': '../Assets/Icons/Equipments/Iron_Chestplate.png', 'solid': False},
    IRON_LEGGINGS: {'name': 'Iron Leggings', 'texture': '../Assets/Icons/Equipments/Iron_Leggings.png', 'solid': False},
    IRON_BOOTS: {'name': 'Iron Boots', 'texture': '../Assets/Icons/Equipments/Iron_Boots.png', 'solid': False},
    DIAMOND_SWORD: {'name': 'Diamond Sword', 'texture': '../Assets/Icons/Equipments/Diamond_Sword.png', 'solid': False},
    DIAMOND_SHOVEL: {'name': 'Diamond Shovel', 'texture': '../Assets/Icons/Equipments/Diamond_Shovel.png', 'solid': False},
    DIAMOND_PICKAXE: {'name': 'Diamond Pickaxe', 'texture': '../Assets/Icons/Equipments/Diamond_Pickaxe.png', 'solid': False},
    DIAMOND_AXE: {'name': 'Diamond Axe', 'texture': '../Assets/Icons/Equipments/Diamond_Axe.png', 'solid': False},
    IRON_SWORD: {'name': 'Iron Sword', 'texture': '../Assets/Icons/Equipments/Iron_Sword.png', 'solid': False},
    IRON_SHOVEL: {'name': 'Iron Shovel', 'texture': '../Assets/Icons/Equipments/Iron_Shovel.png', 'solid': False},
    IRON_PICKAXE: {'name': 'Iron Pickaxe', 'texture': '../Assets/Icons/Equipments/Iron_Pickaxe.png', 'solid': False},
    IRON_AXE: {'name': 'Iron Axe', 'texture': '../Assets/Icons/Equipments/Iron_Axe.png', 'solid': False},
    WOODEN_SWORD: {'name': 'Wooden Sword', 'texture': '../Assets/Icons/Equipments/Wooden_Sword.png', 'solid': False},
    WOODEN_SHOVEL: {'name': 'Wooden Shovel', 'texture': '../Assets/Icons/Equipments/Wooden_Shovel.png', 'solid': False},
    WOODEN_PICKAXE: {'name': 'Wooden Pickaxe', 'texture': '../Assets/Icons/Equipments/Wooden_Pickaxe.png', 'solid': False},
    WOODEN_AXE: {'name': 'Wooden Axe', 'texture': '../Assets/Icons/Equipments/Wooden_Axe.png', 'solid': False},
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

# --- GAMEPLAY ---
# --- GLOBAL PHYSICS ---
GLOBAL_GRAVITY = 30
MAX_FALL_SPEED = 20

# --- PLAYER STATS (DEFAULT) ---
PLAYER_WALK_SPEED = 5
PLAYER_JUMP_FORCE = 12
PLAYER_ATTACK_RANGE = 4.0
PLAYER_MAX_HEALTH = 100

# --- ZOMBIE STATS (DEFAULT) ---
ZOMBIE_MAX_HEALTH = 20
ZOMBIE_WALK_SPEED = 1.5
ZOMBIE_RUN_SPEED = 3.5
ZOMBIE_JUMP_FORCE = 12
ZOMBIE_ATTACK_RANGE = 1.2
ZOMBIE_ATTACK_COOLDOWN = 1.0
ZOMBIE_DAMAGE = 10
ZOMBIE_IDLE_MIN = 1.5       
ZOMBIE_IDLE_MAX = 3.5       
ZOMBIE_PATH_UPDATE_RATE = 0.3 
ZOMBIE_SPAWN_RATE = 3.0     

# --- CHICKEN STATS (DEFAULT) ---
CHICKEN_MAX_HEALTH = 4
CHICKEN_WALK_SPEED = 2.0
CHICKEN_RUN_SPEED = 4.0
CHICKEN_JUMP_FORCE = 8
CHICKEN_IDLE_MIN = 1.0
CHICKEN_IDLE_MAX = 3.0
CHICKEN_FLEE_DURATION = 4.0
CHICKEN_FLEE_DISTANCE = 8   
CHICKEN_SPAWN_RATE = 15.0
MOB_DESPAWN_RANGE = 60

# --- TOOL DAMAGE VALUES ---
TOOL_DAMAGE = {
    WOODEN_SWORD: 4, IRON_SWORD: 6, DIAMOND_SWORD: 7,
    WOODEN_AXE: 3, IRON_AXE: 5, DIAMOND_AXE: 6,
    WOODEN_PICKAXE: 2, IRON_PICKAXE: 4, DIAMOND_PICKAXE: 5,
    0: 1 
}

# --- TOOL ARMOR VALUES ---
TOOL_ARMOR = {
    IRON_HELMET: 2, IRON_CHESTPLATE: 6, IRON_LEGGINGS: 5, IRON_BOOTS: 2,
    DIAMOND_HELMET: 3, DIAMOND_CHESTPLATE: 8, DIAMOND_LEGGINGS: 6, DIAMOND_BOOTS: 3
}

# --- FOOD VALUES ---
FOOD = {
    CHICKEN:2, COOKED_CHICKEN:6
}

def set_difficulty(difficulty):
    global PLAYER_MAX_HEALTH
    global ZOMBIE_MAX_HEALTH, ZOMBIE_WALK_SPEED, ZOMBIE_RUN_SPEED, ZOMBIE_JUMP_FORCE
    global ZOMBIE_DAMAGE, ZOMBIE_ATTACK_COOLDOWN, ZOMBIE_SPAWN_RATE
    global ZOMBIE_ATTACK_RANGE, ZOMBIE_IDLE_MIN, ZOMBIE_IDLE_MAX, ZOMBIE_PATH_UPDATE_RATE
    global CHICKEN_SPAWN_RATE

    print(f"[CONFIG] Applying Difficulty: {difficulty}")

    if difficulty == 'EASY':
        # Player Buff
        PLAYER_MAX_HEALTH = 150
        
        # Zombie Nerf
        ZOMBIE_MAX_HEALTH = 15          # Empuk
        ZOMBIE_WALK_SPEED = 1.0         # Lambat
        ZOMBIE_RUN_SPEED = 2.5          # Mudah dikejar/kabur
        ZOMBIE_JUMP_FORCE = 8
        ZOMBIE_DAMAGE = 5               # Damage kecil
        ZOMBIE_ATTACK_COOLDOWN = 1.5    # Serangan lambat
        ZOMBIE_SPAWN_RATE = 10.0         # Jarang muncul
        
        # Zombie AI Dumbed Down
        ZOMBIE_ATTACK_RANGE = 1.2
        ZOMBIE_IDLE_MIN = 2.0
        ZOMBIE_IDLE_MAX = 5.0
        ZOMBIE_PATH_UPDATE_RATE = 0.5 

        # Chicken Buff (More Food)
        CHICKEN_SPAWN_RATE = 10.0       

    elif difficulty == 'HARD':
        # Player Standard
        PLAYER_MAX_HEALTH = 100
        
        # Zombie Buff (Horde Mode)
        ZOMBIE_MAX_HEALTH = 30          # Keras
        ZOMBIE_WALK_SPEED = 1.8         # Cepat
        ZOMBIE_RUN_SPEED = 3.5          # Sangat cepat (hampir secepat player)
        ZOMBIE_JUMP_FORCE = 12
        ZOMBIE_DAMAGE = 15              # Sakit
        ZOMBIE_ATTACK_COOLDOWN = 0.8    # Serangan cepat
        ZOMBIE_SPAWN_RATE = 8.0         # Muncul sangat sering
        
        # Zombie AI Aggressive
        ZOMBIE_ATTACK_RANGE = 1.5
        ZOMBIE_IDLE_MIN = 0.5
        ZOMBIE_IDLE_MAX = 2.0
        ZOMBIE_PATH_UPDATE_RATE = 0.2 

        # Chicken Nerf (Food Scarcity)
        CHICKEN_SPAWN_RATE = 20.0       # Makanan langka