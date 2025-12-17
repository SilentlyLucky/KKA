from config import *

# --- RESEP 2x2 (Inventory Crafting) ---
RECIPES_2x2 = {
    # Oak Log -> 4 Planks
    ((LOG, None),
     (None, None)): (PLANK, 4),
     
    # 2 Planks (Vertical) -> 4 Sticks
    ((PLANK, None),
     (PLANK, None)): (STICK, 4),
     
    # Torch (Coal atas Stick)
    ((COAL, None),
     (STICK, None)): (TORCH, 4),
     
    # Crafting Table (4 Planks)
    ((PLANK, PLANK),
     (PLANK, PLANK)): (CRAFTING_TABLE, 1),
}

# --- RESEP 3x3 (Crafting Table) ---
RECIPES_3x3 = {
    # --- TOOLS (Wooden) ---
    # Sword (Stick, Plank, Plank vertical) - Minecraft 1.0 style
    ((None, PLANK, None),
     (None, PLANK, None),
     (None, STICK, None)): (WOODEN_SWORD, 1),
     
    # Pickaxe
    ((PLANK, PLANK, PLANK),
     (None, STICK, None),
     (None, STICK, None)): (WOODEN_PICKAXE, 1),
     
    # Shovel
    ((None, PLANK, None),
     (None, STICK, None),
     (None, STICK, None)): (WOODEN_SHOVEL, 1),
     
    # Axe
    ((PLANK, PLANK, None),
     (PLANK, STICK, None),
     (None, STICK, None)): (WOODEN_AXE, 1),
     
    # --- TOOLS (Wooden) ---
    ((None, PLANK, None), (None, PLANK, None), (None, STICK, None)): (WOODEN_SWORD, 1),
    ((PLANK, PLANK, PLANK), (None, STICK, None), (None, STICK, None)): (WOODEN_PICKAXE, 1),
    ((None, PLANK, None), (None, STICK, None), (None, STICK, None)): (WOODEN_SHOVEL, 1),
    ((PLANK, PLANK, None), (PLANK, STICK, None), (None, STICK, None)): (WOODEN_AXE, 1),

    # --- TOOLS (Wooden) ---
    ((None, PLANK, None), (None, PLANK, None), (None, STICK, None)): (WOODEN_SWORD, 1),
    ((PLANK, PLANK, PLANK), (None, STICK, None), (None, STICK, None)): (WOODEN_PICKAXE, 1),
    ((None, PLANK, None), (None, STICK, None), (None, STICK, None)): (WOODEN_SHOVEL, 1),
    ((PLANK, PLANK, None), (PLANK, STICK, None), (None, STICK, None)): (WOODEN_AXE, 1),

    # --- TOOLS (Diamond) ---
    ((None, DIAMOND, None), (None, DIAMOND, None), (None, STICK, None)): (DIAMOND_SWORD, 1),
    ((DIAMOND, DIAMOND, DIAMOND), (None, STICK, None), (None, STICK, None)): (DIAMOND_PICKAXE, 1),
    ((None, DIAMOND, None), (None, STICK, None), (None, STICK, None)): (DIAMOND_SHOVEL, 1),
    ((DIAMOND, DIAMOND, None), (DIAMOND, STICK, None), (None, STICK, None)): (DIAMOND_AXE, 1),

    # --- ARMOR (Iron) ---
    # Helmet
    ((IRON, IRON, IRON),
     (IRON, None, IRON),
     (None, None, None)): (IRON_HELMET, 1),
    # Chestplate
    ((IRON, None, IRON),
     (IRON, IRON, IRON),
     (IRON, IRON, IRON)): (IRON_CHESTPLATE, 1),
    # Leggings
    ((IRON, IRON, IRON),
     (IRON, None, IRON),
     (IRON, None, IRON)): (IRON_LEGGINGS, 1),
    # Boots
    ((None, None, None),
     (IRON, None, IRON),
     (IRON, None, IRON)): (IRON_BOOTS, 1),

    # --- ARMOR (Diamond) ---
    ((DIAMOND, DIAMOND, DIAMOND), (DIAMOND, None, DIAMOND), (None, None, None)): (DIAMOND_HELMET, 1),
    ((DIAMOND, None, DIAMOND), (DIAMOND, DIAMOND, DIAMOND), (DIAMOND, DIAMOND, DIAMOND)): (DIAMOND_CHESTPLATE, 1),
    ((DIAMOND, DIAMOND, DIAMOND), (DIAMOND, None, DIAMOND), (DIAMOND, None, DIAMOND)): (DIAMOND_LEGGINGS, 1),
    ((None, None, None), (DIAMOND, None, DIAMOND), (DIAMOND, None, DIAMOND)): (DIAMOND_BOOTS, 1),
    
    ((None, None, None),
     (PLANK, PLANK, PLANK),
     (PLANK, PLANK, PLANK)): (BED_ITEM, 1), 
}

def check_shapeless_recipe(grid_items):
    """
    Mengecek resep yang tidak butuh bentuk spesifik (1 item -> 1 item).
    Digunakan untuk Sand -> Glass, Raw Chicken -> Cooked Chicken.
    """
    # Hitung total item yang ada di grid
    items_present = []
    for row in grid_items:
        for item in row:
            if item is not None:
                items_present.append(item)
    
    # Jika hanya ada 1 item
    if len(items_present) == 1:
        item_id = items_present[0]
        if item_id == SAND:
            return (GLASS, 1)
        if item_id == RAW_CHICKEN:
            return (COOKED_CHICKEN, 1)
        # Log -> 4 Planks (Shapeless version for convenience)
        if item_id == LOG:
            return (PLANK, 4)
            
    return None

def normalize_input_grid(grid):
    """
    Mengubah grid input (bisa berisi dict atau None) menjadi tuple of tuples berisi ID atau None.
    """
    normalized_grid = []
    for row in grid:
        norm_row = []
        for item in row:
            # Item bisa berupa None atau dict {'id': 1, ...} atau int ID langsung (jika dari test)
            if item is None:
                norm_row.append(None)
            elif isinstance(item, dict):
                norm_row.append(item['id'])
            else:
                norm_row.append(item)
        normalized_grid.append(tuple(norm_row))
    return tuple(normalized_grid)

def extract_2x2_from_3x3(grid_3x3, start_row, start_col):
    """
    Mengambil potongan 2x2 dari grid 3x3 mulai dari start_row, start_col.
    Mengembalikan tuple of tuples 2x2.
    """
    sub_grid = []
    for r in range(2):
        row = []
        for c in range(2):
            row.append(grid_3x3[start_row + r][start_col + c])
        sub_grid.append(tuple(row))
    return tuple(sub_grid)

def is_grid_empty(grid):
    """Cek apakah grid sepenuhnya kosong (None semua)"""
    for row in grid:
        for item in row:
            if item is not None:
                return False
    return True

def check_recipe(grid, is_3x3=False):
    """
    Mencocokkan grid saat ini dengan database resep.
    Grid adalah list of lists berisi ID item atau None.
    """
    
    norm_grid = normalize_input_grid(grid)
    shapeless_result = check_shapeless_recipe(norm_grid)
    if shapeless_result:
        return shapeless_result

    if is_3x3:
        if norm_grid in RECIPES_3x3:
            return RECIPES_3x3[norm_grid]
        
        possible_positions = [(0,0), (0,1), (1,0), (1,1)]
        
        for start_r, start_c in possible_positions:
            sub_grid = extract_2x2_from_3x3(norm_grid, start_r, start_c)
            
            if sub_grid in RECIPES_2x2:                
                is_clean = True
                for r in range(3):
                    for c in range(3):
                        if start_r <= r < start_r + 2 and start_c <= c < start_c + 2:
                            continue 
                        if norm_grid[r][c] is not None:
                            is_clean = False
                            break
                    if not is_clean: break
                
                if is_clean:
                    return RECIPES_2x2[sub_grid]

    else:
        if norm_grid in RECIPES_2x2:
            return RECIPES_2x2[norm_grid]
        
    return None