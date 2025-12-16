from ursina import *
from config import *
from block import Block
import math
import random
from collections import deque

class World(Entity):
    def __init__(self):
        super().__init__()
        self.blocks = [] 
        self.block_positions = set()
        self.map_data = [[0 for y in range(DEPTH)] for x in range(WIDTH)]
        self.surface_heights = []
        self.solid_map = [[False for _ in range(DEPTH)] for _ in range(WIDTH)]
        self.light_map = [[0 for y in range(DEPTH)] for x in range(WIDTH)]
        
        self.bg_parent = Entity(parent=self, name='Background_Layer')
        self.fg_parent = Entity(parent=self, name='Foreground_Layer')

        self.generating = True
        self.generate_data()
        self.render_world()
        self.generating = False
        self.compute_light()
        self.apply_light_to_blocks()

    def generate_data(self):
        for x in range(WIDTH):
            h = BASE_HEIGHT + int(math.sin(x / 5) * 4 + math.cos(x / 3) * 2)
            self.surface_heights.append(h)
            for y in range(DEPTH):
                if y < h:
                    self.map_data[x][y] = 1

        random.seed(42)
        for x in range(WIDTH):
            for y in range(DEPTH):
                stone_level = self.surface_heights[x] - DIRT_LAYER_THICKNESS
                if y < stone_level:
                    cave_value = math.sin(x * 0.3) * math.cos(y * 0.2) + math.sin(x * 0.1) * math.cos(y * 0.4)
                    if cave_value > 0.3:
                        self.map_data[x][y] = 0

    def render_world(self):
        print("Rendering World...")
        for x in range(WIDTH):
            h = self.surface_heights[x]
            dirt_start_y = h - DIRT_LAYER_THICKNESS
            
            for y in range(DEPTH):
                if y < h:
                    bg_col = BG_DIRT_COLOR if y >= dirt_start_y else BG_STONE_COLOR
                    Entity(
                        parent=self.bg_parent,
                        model='quad',
                        color=bg_col,
                        position=(x, y, BG_Z),
                        scale=(1, 1)
                    )

                if self.map_data[x][y] == 1:
                    if y == h - 1:
                        tipe = GRASS
                    elif y >= dirt_start_y:
                        tipe = DIRT
                    else:
                        tipe = STONE
                    self.place_block(x, y, tipe)

    def place_block(self, x, y, block_type):
        self.map_data[x][y] = 1
        b = Block(position=(x, y), block_type=block_type)
        b.parent = self.fg_parent
        self.blocks.append(b)
        self.block_positions.add((x, y))
        self.solid_map[x][y] = b.solid

        if not self.generating:
            self.compute_light()
            self.apply_light_to_blocks()
        return b

    def remove_block(self, entity):
        if entity in self.blocks:
            self.blocks.remove(entity)
            pos = (int(entity.x), int(entity.y))
            self.map_data[pos[0]][pos[1]] = 0
            self.solid_map[pos[0]][pos[1]] = False
            if pos in self.block_positions:
                self.block_positions.remove(pos)
            destroy(entity)
            self.compute_light()
            self.apply_light_to_blocks()

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
            if 0 <= nx < WIDTH and 0 <= ny < DEPTH and self.map_data[nx][ny] == 0:
                best = max(best, self.light_map[nx][ny])
        return best
    
    def is_light_blocking(self, x, y):
        return self.solid_map[x][y]