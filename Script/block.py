from ursina import *
from config import FG_Z, BLOCK_DATA

class Block(Entity):
    def __init__(self, position, block_type):
        data = BLOCK_DATA.get(block_type)
        self.my_color = data['color'] if data else color.white
        
        super().__init__(
            parent=scene,
            position=position,
            model='quad',
            color=self.my_color,
            scale=(1, 1),
            collider='box',
            z=FG_Z
        )
        
        self.block_type = block_type
        self.block_name = data['name'] if data else 'Unknown'

    def hancur(self): # ntar kudevelop sfx
        destroy(self)

    def set_light_level(self, lvl):
        if not isinstance(lvl, (int, float)):
            lvl = 0
        if lvl != lvl or lvl == float('inf'):
            lvl = 0

        lvl = max(0, min(15, int(lvl)))

        brightness = 0.2 + 0.8 * (lvl / 15.0)
        self.color = self.my_color * brightness
