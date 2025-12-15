from ursina import *
from ursina.prefabs.platformer_controller_2d import PlatformerController2d
from config import *
from block import Block

class Player(PlatformerController2d):
    def __init__(self, world_instance, **kwargs):
        super().__init__(**kwargs)
        self.world = world_instance
        
        # --- 1. COLLIDER / FISIK (0.8 x 0.8) ---
        # Dibuat lebih kecil dari 1.0 agar tidak nyangkut gesekan di lorong 1 blok
        self.collider = 'box' 
        self.scale_x = 0.8
        self.scale_y = 0.8
        self.color = color.clear # Fisik transparan
        
        # --- 2. VISUAL (Kompensasi agar terlihat 1.0) ---
        # 0.8 (Fisik) * 1.25 (Visual) = 1.0 (Tampilan Blok Penuh)
        self.visual = Entity(
            parent=self,
            model='quad',
            color=color.azure,
            scale=(1.25, 1.25), 
            position=(0, 0, 0)
        )
        
        self.cursor = Entity(parent=camera, model='quad', color=color.red, scale=.05, rotation_z=45, z=-1)

        # PHYSICS & STATS (Disesuaikan untuk badan kecil)
        self.gravity = 0.65     
        self.jump_height = 1.2  # Lompatan pendek cukup untuk naik 1 blok
        self.walk_speed = 5
        self.max_fall_speed = 12

        # HEALTH SYSTEM
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        
        # UI
        self.health_bar_bg = Entity(parent=camera.ui, model='quad', color=color.red.tint(-0.2), scale=(0.5, 0.03), position=(-0.6, 0.45))
        self.health_bar = Entity(parent=camera.ui, model='quad', color=color.green, scale=(0.5, 0.03), position=(-0.6, 0.45))

    def update(self):
        super().update()
        self.z = FG_Z 
        
        # Respawn Logic
        if self.y < -10:
            self.take_damage(20) 
            center_x = int(WIDTH/2)
            spawn_y = self.world.surface_heights[center_x] + 4
            self.position = (center_x, spawn_y)
            self.velocity = (0, 0)
            
        # Update Health UI
        target_scale_x = 0.5 * (self.health / self.max_health)
        self.health_bar.scale_x = max(0, target_scale_x) 
        self.health_bar.x = self.health_bar_bg.x - (0.5 - self.health_bar.scale_x) / 2

    def take_damage(self, amount):
        self.health -= amount
        self.visual.color = color.red
        invoke(setattr, self.visual, 'color', color.azure, delay=0.1) # Flash Red di visual
        
        if self.health <= 0:
            print("GAME OVER")
            self.health = self.max_health
            self.position = (int(WIDTH/2), 30)

    def input(self, key):
        super().input(key)

        # BREAK BLOCK
        if key == 'left mouse down':
            if mouse.hovered_entity and isinstance(mouse.hovered_entity, Block):
                self.world.remove_block(mouse.hovered_entity)

        # PLACE BLOCK
        if key == 'right mouse down':
            if mouse.world_point:
                mx = round(mouse.world_point.x)
                my = round(mouse.world_point.y)
                
                # Cek jarak agar tidak menaruh block di dalam badan sendiri
                # Karena badan kecil (0.8), jarak aman build sekitar 1.0
                if abs(mx - self.x) < 1.0 and abs(my - self.y) < 1.0:
                    pass # Jangan taruh block di dalam badan
                else:
                    if (mx, my) not in self.world.block_positions:
                         # Place block logic
                         if distance((mx, my, 0), self.position) > 1.1: 
                            self.world.place_block(mx, my, DIRT)