from ursina import *
from config import *
from block import Block
import math
import random

class World(Entity):
    def __init__(self):
        super().__init__()
        self.blocks = [] 
        self.block_positions = set()
        self.map_data = [[0 for y in range(DEPTH)] for x in range(WIDTH)]
        self.surface_heights = []
        
        self.bg_parent = Entity(parent=self, name='Background_Layer')
        self.fg_parent = Entity(parent=self, name='Foreground_Layer')

        self.generate_data()
        self.render_world()

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
        b = Block(position=(x, y), block_type=block_type)
        b.parent = self.fg_parent
        self.blocks.append(b)
        self.block_positions.add((x, y))
        return b

    def remove_block(self, entity):
        if entity in self.blocks:
            self.blocks.remove(entity)
            pos = (int(entity.x), int(entity.y))
            if pos in self.block_positions:
                self.block_positions.remove(pos)
            destroy(entity)