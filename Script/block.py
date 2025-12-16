from ursina import *
from config import FG_Z, BLOCK_DATA

class Block(Entity):
    def __init__(self, position, block_type):
        data = BLOCK_DATA.get(block_type)
        # self.my_color = data['color'] if data else color.white
        self.block_type = block_type
        self.solid = data.get('solid', True)
        my_texture = data.get('texture')
        is_double_sided = data.get('double_sided', False) if data else False
        
        super().__init__(
            parent=scene,
            position=position,
            model='quad',
            texture=my_texture,
            scale=(1, 1),
            collider='box',
            z=FG_Z,
            double_sided=is_double_sided
        )
        
        self.block_name = data['name'] if data else 'Unknown'
        self.emits_light = data.get('emits_light', False)
        self.light_strength = data.get('light_level', 0)

    def hancur(self):
        destroy(self)

    def set_light_level(self, lvl):
        if not isinstance(lvl, (int, float)):
            lvl = 0
        if lvl != lvl or lvl == float('inf'):
            lvl = 0
        lvl = max(0, min(15, int(lvl)))
        brightness = 0.0 + 0.8 * (lvl / 15.0)
        self.color = color.white.tint(brightness - 1)