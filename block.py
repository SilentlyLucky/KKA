from ursina import *
from config import FG_Z, BLOCK_DATA

class Block(Entity):
    def __init__(self, position, block_type):
        data = BLOCK_DATA.get(block_type)
        my_color = data['color'] if data else color.white
        
        super().__init__(
            parent=scene,
            position=position,
            model='quad',
            color=my_color,
            scale=(1, 1),
            collider='box',
            z=FG_Z
        )
        
        self.block_type = block_type
        self.block_name = data['name'] if data else 'Unknown'

    def hancur(self): # ntar kudevelop sfx
        destroy(self)