from ursina import *
from config import *
from ursina import Sprite
from ursina import camera as Camera
from ursina import time as Time
from config import WIDTH
from world import World

class Scene(Entity):
    def __init__(self):
        super().__init__()
        center = WIDTH / 2

        self.tile_width = 30 
        self.parallax_multiplier = -0.05 
        self.parallax_layers = []
        self.sky = Entity(
            parent=self,
            model='quad',
            texture='../Assets/Background/Layers/sky.png',
            scale=(100, 50),
            z=100,
            position=(center, 20)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_bg.png',
            z_depth=90,
            speed = 1,
            position_y=20,
            start_x=0,
            scale=(self.tile_width, 40)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/glacial_mountains_lightened.png',
            z_depth=80,
            speed = 3,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 30)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/cloud_lonely.png',
            z_depth=70,
            speed = 5,
            position_y=20,
            start_x=0,
            scale=(self.tile_width, 30)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_mg_3.png',
            z_depth=70,
            speed = 4,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 50)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_mg_2.png',
            z_depth=60,
            speed = 5,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 50)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_mg_1_lightened.png',
            z_depth=50,
            speed = 7,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 50)
        )
        
    def add_parallax_layer(self, texture, z_depth, speed, position_y, start_x, scale):
        initial_layer = Entity(
            parent=self,
            model='quad',
            texture=texture,
            z=z_depth,
            position=(start_x, position_y),
            speed=speed,
            start_x=start_x, # Crucial: Store the layer's initial center position
            scale=scale
        )
        
        # Add the initial tile to the master list
        self.parallax_layers.append(initial_layer)

        # Duplicate the tiles (e.g., 3 tiles total: 0, 1, 2)
        for m in range(1, 4): 
            new_tile = duplicate(initial_layer, x=start_x + m * self.tile_width)
            new_tile.start_x = start_x + m * self.tile_width 

            new_tile.start_x = new_tile.x 
            new_tile.speed = speed

            self.parallax_layers.append(new_tile)

    def update(self):
        camera_x = camera.world_position.x 
        loop_distance = self.tile_width * 4 

        for tile in self.parallax_layers:
            # --- 1. Parallax Movement ---
            tile_movement = camera_x * tile.speed * self.parallax_multiplier
            tile.x = tile.start_x + tile_movement
            
            # --- 2. Looping/Wrapping Logic ---
            if tile.x < camera_x - loop_distance:
                tile.x += loop_distance
            
            elif tile.x > camera_x + loop_distance:
                tile.x -= loop_distance
from ursina import *
from config import *
from ursina import Sprite
from ursina import camera as Camera
from ursina import time as Time
from config import WIDTH
from world import World

class Scene(Entity):
    def __init__(self):
        super().__init__()
        center = WIDTH / 2

        self.tile_width = 30 
        self.parallax_multiplier = -0.05 
        self.parallax_layers = []
        self.sky = Entity(
            parent=self,
            model='quad',
            texture='../Assets/Background/Layers/sky.png',
            scale=(100, 50),
            z=100,
            position=(center, 20)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_bg.png',
            z_depth=90,
            speed = 1,
            position_y=20,
            start_x=0,
            scale=(self.tile_width, 40)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/glacial_mountains_lightened.png',
            z_depth=80,
            speed = 3,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 30)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/cloud_lonely.png',
            z_depth=70,
            speed = 5,
            position_y=20,
            start_x=0,
            scale=(self.tile_width, 30)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_mg_3.png',
            z_depth=70,
            speed = 4,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 50)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_mg_2.png',
            z_depth=60,
            speed = 5,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 50)
        )
        self.add_parallax_layer(
            texture='../Assets/Background/Layers/clouds_mg_1_lightened.png',
            z_depth=50,
            speed = 7,
            position_y=25,
            start_x=0,
            scale=(self.tile_width, 50)
        )
        
    def add_parallax_layer(self, texture, z_depth, speed, position_y, start_x, scale):
        initial_layer = Entity(
            parent=self,
            model='quad',
            texture=texture,
            z=z_depth,
            position=(start_x, position_y),
            speed=speed,
            start_x=start_x, # Crucial: Store the layer's initial center position
            scale=scale
        )
        
        # Add the initial tile to the master list
        self.parallax_layers.append(initial_layer)

        # Duplicate the tiles (e.g., 3 tiles total: 0, 1, 2)
        for m in range(1, 4): 
            new_tile = duplicate(initial_layer, x=start_x + m * self.tile_width)
            new_tile.start_x = start_x + m * self.tile_width 

            new_tile.start_x = new_tile.x 
            new_tile.speed = speed

            self.parallax_layers.append(new_tile)

    def update(self):
        camera_x = camera.world_position.x 
        loop_distance = self.tile_width * 4 

        for tile in self.parallax_layers:
            # --- 1. Parallax Movement ---
            tile_movement = camera_x * tile.speed * self.parallax_multiplier
            tile.x = tile.start_x + tile_movement
            
            # --- 2. Looping/Wrapping Logic ---
            if tile.x < camera_x - loop_distance:
                tile.x += loop_distance
            
            elif tile.x > camera_x + loop_distance:
                tile.x -= loop_distance
