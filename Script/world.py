from ursina import *
from config import *
from block import Block
import math
import random
from collections import deque


class World(Entity):
    def __init__(self, world_type="plains", save_data=None):
        super().__init__()
        self.world_type = world_type
        
        # Data Logika
        self.map_data = [[0 for y in range(DEPTH)] for x in range(WIDTH)]
        self.ore_map = {}
        self.surface_heights = []
        self.solid_map = [[False for _ in range(DEPTH)] for _ in range(WIDTH)]
        self.light_map = [[0 for y in range(DEPTH)] for x in range(WIDTH)]
        
        # Data Visual
        self.blocks = [] 
        self.block_dict = {} 
        self.bg_dict = {}    
        self.block_positions = set()
        
        self.falling_blocks = []

        self.bg_parent = Entity(parent=self, name='Background_Layer')
        self.fg_parent = Entity(parent=self, name='Foreground_Layer')
        self.plant_parent = Entity(parent=self, name='Plant_Layer')

        self.generating = True
        self.generate_data()
        self.generating = False
        self.compute_light()
        self.apply_light_to_blocks()
        
        # Rendering state
        self.prev_cam_x = -9999
        self.prev_cam_y = -9999

        # --- LOGIKA LOAD VS GENERATE ---
        if save_data:
            print("Loading World from Save Data...")
            self.load_from_data(save_data)
        else:
            print("Generating New World...")
            self.generate_data()
            self.generate_trees()
            self.generate_ores()
            
        # Kita panggil update manual sekali agar render awal jalan
        self.update_chunk()

    def get_save_data(self):
        """Mengembalikan data penting untuk disimpan"""
        return {
            "world_type": self.world_type,
            "map_data": self.map_data,
            "ore_map": self.ore_map
        }

    def load_from_data(self, data):
        """Memuat data dari save file"""
        self.world_type = data["world_type"]
        self.map_data = data["map_data"]
        self.ore_map = data["ore_map"]
        
        # Kita perlu regenerasi surface_heights untuk keperluan render background
        # (Background butuh tahu di mana permukaan tanahnya)
        self.surface_heights = []
        for x in range(WIDTH):
            h = BASE_HEIGHT + int(math.sin(x / 20) * 10 + math.cos(x / 10) * 5)
            h = clamp(h, 5, DEPTH-1)
            self.surface_heights.append(h)

    def generate_data(self):
        print("Generating Map Data...")
        self.surface_heights = []
        self.map_data = [[0 for y in range(DEPTH)] for x in range(WIDTH)]
        
        for x in range(WIDTH):
            h = BASE_HEIGHT + int(math.sin(x / 20) * 10 + math.cos(x / 10) * 5)
            h = clamp(h, 5, DEPTH-1)
            
            self.surface_heights.append(h)
            for y in range(DEPTH):
                if y < h:
                    self.map_data[x][y] = 1

        random.seed(42)
        for x in range(WIDTH):
            for y in range(DEPTH):
                if y == 0:
                    self.map_data[x][y] = 1 # Bedrock
                    continue
                
                stone_level = self.surface_heights[x] - DIRT_LAYER_THICKNESS
                if y < stone_level:
                    if self.world_type == "sand":
                        cave_value = (
                            math.sin(x * 0.1) * math.cos(y * 0.1) 
                            + math.sin(x * 0.05) * math.cos(y * 0.15)
                        )
                        threshold = 0.4
                    else:
                        cave_value = (
                            math.sin(x * 0.1) * math.cos(y * 0.1)
                            + math.sin(x * 0.05) * math.cos(y * 0.15)
                        )
                        threshold = 0.3

                    if cave_value > threshold:
                        self.map_data[x][y] = 0
        
        if self.world_type != "sand":
            for x in range(WIDTH):
                if not self._is_desert_biome(x):
                    h = self.surface_heights[x]
                    if h < DEPTH:
                        if self.map_data[x][h] == 0 and random.random() < 0.25:
                            self.map_data[x][h] = GRASS_PLANT

    def is_standable(self, x, y):
        """
        Mengecek apakah posisi (x, y) valid untuk entitas berdiri.
        Syarat:
        1. Badan (x, y) harus ada di PASSABLE_BLOCKS (kosong/tembus).
        2. Kepala (x, y+1) harus ada di PASSABLE_BLOCKS.
        3. Kaki (x, y-1) harus SOLID (TIDAK ada di PASSABLE_BLOCKS).
        """
        
        # Cek batas dunia
        if not (0 <= x < WIDTH and 0 <= y < DEPTH):
            return False

        # 1. Cek Badan (Posisi saat ini)
        if self.map_data[x][y] not in PASSABLE_BLOCKS:
            return False
            
        # 2. Cek Kepala (Posisi atas)
        if y + 1 < DEPTH:
            if self.map_data[x][y+1] not in PASSABLE_BLOCKS:
                return False
            
        # 3. Cek Pijakan (Posisi bawah)
        if y - 1 >= 0:
            ground_val = self.map_data[x][y-1]
            # Pijakan harus SOLID. Jadi ground_val TIDAK boleh ada di PASSABLE_BLOCKS.
            if ground_val in PASSABLE_BLOCKS: 
                return False
        else:
            return False # Void (y < 0) tidak bisa dipijak
            
        return True

    def generate_trees(self):
        print("Generating Trees...")
        tree_positions = [] 
        for x in range(3, WIDTH - 3):
            if self.world_type == "sand" and self._is_desert_biome(x): continue
            
            too_close = False
            for tx in tree_positions:
                if abs(x - tx) < 7:
                    too_close = True
                    break
            if too_close: continue
            
            if random.random() < 0.05:
                h = self.surface_heights[x]
                if h-1 < 0: continue
                
                tree_positions.append(x)
                self.map_data[x][h-1] = DIRT 
                
                trunk_height = 6
                for i in range(trunk_height):
                    y = h + i
                    if y < DEPTH:
                        self.map_data[x][y] = LOG
                
                leaf_base_y = h + trunk_height
                leaf_config = [(0, range(-2, 3)), (1, range(-1, 2)), (2, range(0, 1))]
                
                for y_offset, x_range in leaf_config:
                    curr_y = leaf_base_y + y_offset
                    if curr_y >= DEPTH: continue
                    for dx in x_range:
                        leaf_x = x + dx
                        if 0 <= leaf_x < WIDTH:
                            current_block = self.map_data[leaf_x][curr_y]
                            if current_block == 0 or current_block == GRASS_PLANT:
                                self.map_data[leaf_x][curr_y] = LEAVES

    def generate_ores(self):
        print("Generating Ores...")
        random.seed(100)
        for x in range(WIDTH):
            surface_h = self.surface_heights[x]
            stone_top = surface_h - DIRT_LAYER_THICKNESS
            if stone_top <= 1: continue

            for y in range(1, int(stone_top)):
                if self.map_data[x][y] != 1: continue

                if (DEPTH * 0.3) < y < (DEPTH * 0.7):
                    if self._touches_cave(x, y):
                        if random.random() < 0.20: self.ore_map[(x, y)] = COAL_ORE
                if y < (DEPTH * 0.5):
                    if random.random() < 0.03: 
                         self.ore_map[(x, y)] = IRON_ORE
                         if x + 1 < WIDTH: self.ore_map[(x+1, y)] = IRON_ORE
                if y < 10:
                    if random.random() < 0.05: self.ore_map[(x, y)] = DIAMOND

    def _touches_cave(self, x, y):
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for nx, ny in neighbors:
            if 0 <= nx < WIDTH and 0 <= ny < DEPTH:
                if self.map_data[nx][ny] == 0:
                    return True
        return False

    def update(self):
        self.update_chunk()

    def update_chunk(self):
        cam_x = int(camera.x)
        cam_y = int(camera.y)
        
        if abs(cam_x - self.prev_cam_x) < 1 and abs(cam_y - self.prev_cam_y) < 1:
            return

        self.prev_cam_x = cam_x
        self.prev_cam_y = cam_y

        min_x = max(0, cam_x - VIEW_DISTANCE_X)
        max_x = min(WIDTH, cam_x + VIEW_DISTANCE_X)
        min_y = max(0, cam_y - VIEW_DISTANCE_Y)
        max_y = min(DEPTH, cam_y + VIEW_DISTANCE_Y)

        # RENDER BLOK
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                pos = (x, y)
                if pos not in self.bg_dict:
                    self._render_single_bg(x, y)
                
                if pos not in self.block_dict and self.map_data[x][y] != 0:
                    self._render_single_block(x, y)

        # UNLOAD
        unload_dist_x = VIEW_DISTANCE_X + 5
        unload_dist_y = VIEW_DISTANCE_Y + 5
        
        to_remove_fg = []
        for pos, entity in self.block_dict.items():
            if (abs(pos[0] - cam_x) > unload_dist_x or 
                abs(pos[1] - cam_y) > unload_dist_y):
                to_remove_fg.append(pos)
        
        for pos in to_remove_fg:
            ent = self.block_dict.pop(pos)
            if ent in self.blocks: self.blocks.remove(ent)
            self.block_positions.discard(pos)
            destroy(ent)

        to_remove_bg = []
        for pos, entity in self.bg_dict.items():
            if (abs(pos[0] - cam_x) > unload_dist_x or 
                abs(pos[1] - cam_y) > unload_dist_y):
                to_remove_bg.append(pos)
                
        for pos in to_remove_bg:
            ent = self.bg_dict.pop(pos)
            destroy(ent)

    def _is_desert_biome(self, x):
        if self.world_type != "sand": return False
        segment = int((x * 12) / WIDTH)
        desert_segments = (1, 2, 4, 7, 9, 10)
        return segment in desert_segments

    def _render_single_bg(self, x, y):
        h = self.surface_heights[x]
        if y >= h: return 

        dirt_start_y = h - DIRT_LAYER_THICKNESS
        
        if y < dirt_start_y:
            bg_col = BG_STONE_COLOR
        else:
            if self._is_desert_biome(x):
                bg_col = BG_SAND_COLOR
            else:
                bg_col = BG_DIRT_COLOR

        bg = Entity(
            parent=self.bg_parent,
            model="quad",
            color=bg_col,
            position=(x, y, BG_Z),
            scale=(1, 1),
        )
        self.bg_dict[(x, y)] = bg

    def _render_single_block(self, x, y):
        block_val = self.map_data[x][y]
        
        target_parent = self.fg_parent
        tipe = STONE
        is_trigger = False
        z_pos = FG_Z

        if block_val in (GRASS_PLANT, LOG, LEAVES):
            tipe = block_val
            target_parent = self.plant_parent
            z_pos = PLANT_Z
            is_trigger = True
        
        elif block_val == DIRT: 
            tipe = DIRT
            
        elif block_val == 1: 
            h = self.surface_heights[x]
            dirt_start_y = h - DIRT_LAYER_THICKNESS
            is_desert = self._is_desert_biome(x)
            
            if y == 0:
                tipe = BEDROCK
            elif y == h - 1:
                tipe = SAND if is_desert else GRASS
            elif y >= dirt_start_y:
                tipe = SAND if is_desert else DIRT
            
            if tipe == STONE and (x, y) in self.ore_map:
                tipe = self.ore_map[(x, y)]

        b = Block(position=(x, y), block_type=tipe)
        b.parent = target_parent
        b.z = z_pos 
        
        if is_trigger:
            b.collider.is_trigger = True
        
        self.blocks.append(b)
        self.block_positions.add((x, y))
        self.block_dict[(x, y)] = b

    def place_block(self, x, y, block_type):
        if (x,y) in self.block_dict:
            return self.block_dict[(x,y)]
        
        is_passable = block_type in (GRASS_PLANT, LOG, LEAVES)
        
        target_parent = self.plant_parent if is_passable else self.fg_parent
        z_pos = PLANT_Z if is_passable else FG_Z
            
        b = Block(position=(x, y), block_type=block_type)
        b.parent = target_parent
        b.z = z_pos
        
        if is_passable:
            b.collider.is_trigger = True
        
        self.blocks.append(b)
        self.block_positions.add((x, y))
        self.block_dict[(x, y)] = b
        self.solid_map[x][y] = b.solid

        if not self.generating:
            self.compute_light()
            self.apply_light_to_blocks()
            return b
        
        self.map_data[x][y] = block_type 

        if block_type == SAND:
            self._convert_dirt_above_to_sand(x, y)
            if not self._has_support(x, y):
                self.trigger_sand_gravity(x, y + 0)
        return b

    def remove_block(self, entity):
        if not entity: return
        pos = (int(entity.x), int(entity.y))
        
        if getattr(entity, "block_type", None) == BEDROCK:
            return

        if entity in self.blocks: 
            self.blocks.remove(entity)
            pos = (int(entity.x), int(entity.y))
            self.map_data[pos[0]][pos[1]] = 0
            self.solid_map[pos[0]][pos[1]] = False
        if pos in self.block_positions: self.block_positions.remove(pos)
        if pos in self.block_dict: self.block_dict.pop(pos)
        if 0 <= pos[0] < WIDTH and 0 <= pos[1] < DEPTH:
            self.map_data[pos[0]][pos[1]] = 0
            
        destroy(entity)
        self.compute_light()
        self.apply_light_to_blocks()
        self.trigger_sand_gravity(pos[0], pos[1] + 1)

    # ... Helper sand logic (Sama, tidak berubah) ...
    def _set_block_type(self, block, new_type):
        data = BLOCK_DATA.get(new_type, {"color": color.white, "name": "Unknown"})
        block.block_type = new_type
        block.block_name = data["name"]
        block.color = data["color"]
        if new_type == SAND:
            x = int(round(block.x))
            y = int(round(block.y))
            self._convert_dirt_above_to_sand(x, y)

    def _convert_dirt_above_to_sand(self, x, y):
        current_y = y + 1
        while True:
            block = self.block_dict.get((x, current_y))
            if block and block.block_type == DIRT:
                self._set_block_type(block, SAND)
                current_y += 1
                continue
            break

    def _has_support(self, x, y):
        if y <= 0: return True
        if 0 <= x < WIDTH and 0 <= y-1 < DEPTH:
            val = self.map_data[x][y-1]
            return val not in (0, GRASS_PLANT, LOG, LEAVES)
        return False

    def _collect_sand_column(self, x, start_y):
        base_block = self.block_dict.get((x, start_y))
        if not base_block or base_block.block_type != SAND:
            return []

        column = [base_block]
        y = start_y + 1
        while True:
            block = self.block_dict.get((x, y))
            if not block: break
            if block.block_type == SAND:
                column.append(block)
                y += 1
                continue
            if block.block_type == DIRT:
                self._set_block_type(block, SAND)
                column.append(block)
                y += 1
                continue
            break
        column.sort(key=lambda b: b.y)
        return column

    def _compute_drop_distance(self, x, bottom_y):
        distance = 0
        check_y = bottom_y - 1
        while check_y >= 0:
            val = self.map_data[x][check_y]
            if val not in (0, GRASS_PLANT, LOG, LEAVES): 
                break
            distance += 1
            check_y -= 1
        return distance

    def trigger_sand_gravity(self, x, start_y):
        column = self._collect_sand_column(x, int(round(start_y)))
        if not column: return

        bottom_y = int(round(column[0].y))
        drop_distance = self._compute_drop_distance(x, bottom_y)
        if drop_distance <= 0: return

        for block in column:
            old_y = int(block.y)
            self.map_data[x][old_y] = 0 
            
        target_base_y = bottom_y - drop_distance
        
        for idx, block in enumerate(column):
            new_y = target_base_y + idx
            old_pos = (int(block.x), int(block.y))
            new_pos = (x, new_y)
            
            if old_pos in self.block_dict: self.block_dict.pop(old_pos)
            if old_pos in self.block_positions: self.block_positions.remove(old_pos)
            
            block.position = (x, new_y, FG_Z)
            self.block_dict[new_pos] = block
            self.block_positions.add(new_pos)
            self.map_data[x][new_y] = 1 

        self.falling_blocks = []

    def compute_light(self):
        self.light_map = [[0 for _ in range(DEPTH)] for _ in range(WIDTH)]
        q = deque()

        for x in range(WIDTH):
            top_solid = -1
            for y in range(DEPTH - 1, -1, -1):
                if self.map_data[x][y] == 1:
                    top_solid = y
                    break
            for y in range(top_solid + 1, DEPTH):
                if self.map_data[x][y] == 0:
                    self.light_map[x][y] = 15
                    q.append((x, y, 15))

        for b in self.blocks:
            if b.emits_light:
                x, y = int(b.x), int(b.y)
                self.light_map[x][y] = b.light_strength
                q.append((x, y, b.light_strength))
                
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        while q:
            x, y, level = q.popleft()
            if level <= 1:
                continue
            nl = level - 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < DEPTH:
                    if not self.is_light_blocking(nx, ny) and self.light_map[nx][ny] < nl:
                        self.light_map[nx][ny] = nl
                        q.append((nx, ny, nl))


    def apply_light_to_blocks(self):
        for b in self.blocks:
            x, y = int(b.x), int(b.y)
            if 0 <= x < WIDTH and 0 <= y < DEPTH:
                lvl = self.light_map[x][y] if self.map_data[x][y] == 0 else self._light_for_solid(x, y)
                b.set_light_level(lvl)

    def _light_for_solid(self, x, y):
        best = 0
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 0 <= ny < DEPTH:
                best = max(best, self.light_map[nx][ny])
        return max(0, best - 1)
    
    def is_light_blocking(self, x, y):
        return self.solid_map[x][y]