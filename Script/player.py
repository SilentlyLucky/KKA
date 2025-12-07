from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d
from config import *
from block import Block

class Player(PlatformerController2d):
    def __init__(self, world_instance, **kwargs):
        super().__init__(**kwargs)
        self.world = world_instance
        
        # COLLISION
        self.collider = 'box' 
        self.scale_x = 0.7
        self.scale_y = 1.4
        
        self.color = color.azure
        self.cursor = Entity(parent=camera, model='quad', color=color.red, scale=.05, rotation_z=45, z=-1)

        # PHYSICS
        self.gravity = 0.6
        self.jump_height = 2.2
        self.walk_speed = 5
        self.max_fall_speed = 12

    def update(self):
        super().update()
        self.z = FG_Z 
        if self.y < -10:
            center_x = int(WIDTH/2)
            spawn_y = self.world.surface_heights[center_x] + 4
            self.position = (center_x, spawn_y)
            self.velocity = (0, 0)

    def input(self, key):
        super().input(key)

        # --- BREAK BLOCK ---
        if key == 'left mouse down':
            if mouse.hovered_entity and isinstance(mouse.hovered_entity, Block):
                self.world.remove_block(mouse.hovered_entity)

        # --- PLACE BLOCK ---
        if key == 'right mouse down':
            if mouse.world_point:
                mx = round(mouse.world_point.x)
                my = round(mouse.world_point.y)
                
                if abs(mx - self.x) < 2.5 and abs(my - self.y) < 2.5:
                    if (mx, my) not in self.world.block_positions:
                        if distance((mx, my, 0), self.position) > 0.7:
                            self.world.place_block(mx, my, DIRT)