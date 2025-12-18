from ursina import *
from config import *
from craft import check_recipe
import math

class Inventory(Entity):
    def __init__(self, load_data=None, player_ref=None, **kwargs):
        super().__init__(parent=camera.ui)
        
        self.player_ref = player_ref
        
        self.items = [None] * 45
        
        self.selected_index = 0
        self.is_open = False  
        
        self.hand_item = None 
        self.hand_icon = Entity(parent=camera.ui, model='quad', scale=0.07, z=-99, visible=False, color=color.white)
        self.hand_text = Text(parent=self.hand_icon, text="", origin=(0, 0), color=color.white, scale=10, z=-1)

        self.tooltip = Text(parent=camera.ui, text="", origin=(0, 0), scale=1, color=color.white, z=-100, visible=False, background=True)
        self.tooltip.background.color = color.rgba(0,0,0,0.2)
        self.tooltip.background.scale_x = 0.15
        self.tooltip.background.scale_y = 0.05

        self.slots = [] 
        
        self.hotbar_parent = Entity(parent=self, y=-0.44)
        self.hotbar_slots = []
        
        for i in range(9):
            s = self._create_slot(
                parent=self.hotbar_parent, 
                index=i, 
                x=(i - 4) * 0.082,
                y=0.12
            )
            self.hotbar_slots.append(s)
            self.slots.append(s)


        self.main_panel = Entity(parent=self, enabled=False)
        

        self.bg = Entity(
            parent=self.main_panel, 
            model='quad', 
            scale=(0.8, 0.8), 
            texture='../Assets/GUI/inventory.png',
            color=color.white, 
            z=10
        )
        

        start_y = -0.042
        for row in range(3):
            for col in range(9):
                idx = 9 + (row * 9) + col
                s = self._create_slot(
                    parent=self.main_panel,
                    index=idx,
                    x=(col - 4) * 0.0816,
                    y=start_y - (row * 0.086)
                )
                self.slots.append(s)


        armor_x = -0.323
        armor_start_y = 0.323
        
        for i in range(4):
            idx = 41 + i
            s = self._create_slot(
                parent=self.main_panel,
                index=idx, 
                x=armor_x,
                y=armor_start_y - (i * 0.084),
                scale=0.08, 
                col=color.rgba(0, 0, 0, 0.2)
            )
            self.slots.append(s)


        craft_indices = [[36, 37], [38, 39]]
        craft_x_start = 0.08
        craft_y_start = 0.275
        
        slot_size = 0.08
        gap = 0.004

        for row in range(2):
            for col in range(2):
                idx = craft_indices[row][col]
                s = self._create_slot(
                    parent=self.main_panel,
                    index=idx, 
                    x=craft_x_start + (col * (slot_size + gap)),
                    y=craft_y_start - (row * (slot_size + gap)),
                    col=color.rgba(0,0,0,0.1) 
                )
                s.scale = slot_size 
                self.slots.append(s)
        

        self.craft_out_slot = self._create_slot(parent=self.main_panel, index=40, x=0.336, y=0.225, scale=0.08, col=color.rgba(0,0,0,0.1))
        self.slots.append(self.craft_out_slot)


        if load_data:
            self.load_from_data(load_data)


        self.update_ui()
        self.highlight_selected_hotbar()

    def get_save_data(self):
        return self.items

    def load_from_data(self, data):

        if len(data) < 45:
            for i, item in enumerate(data):
                if i < 45: self.items[i] = item
        else:
            self.items = data
        self.update_ui()

    def _create_slot(self, parent, index, x, y=0, scale=0.08, col=color.rgba(1,1,1,0.1)):
        slot = Button(
            parent=parent,
            model='quad',
            color=col,
            scale=scale,
            position=(x, y)
        )
        slot.my_index = index 
        
        slot.item_icon = Entity(
            parent=slot,
            model='quad',
            scale=0.8,
            color=color.white,
            z=-0.1,
            visible=False
        )
        
        slot.item_count_text = Text(
            parent=slot,
            text="",
            origin=(0.5, -0.5), 
            position=(0.45, -0.45), 
            scale=2.5 * scale, 
            color=color.white,
            z=-1
        )
        
        slot.item_count_shadow = Text(
            parent=slot,
            text="",
            origin=(0.5, -0.5),
            position=(0.46, -0.46), 
            scale=1.5 * scale, 
            color=color.black,
            z=-0.9 
        )
        
        return slot

    def input(self, key):
        if not self.is_open:
            return

        hovered_slot = mouse.hovered_entity
        if hovered_slot and isinstance(hovered_slot, Button) and hasattr(hovered_slot, 'my_index'):
            index = hovered_slot.my_index
            self.show_tooltip(index)

            if key == 'left mouse down':
                if index == 40: self.on_craft_output_click()
                elif 41 <= index <= 44: self.on_armor_slot_click(index)
                else: self.on_slot_left_click(index)
            elif key == 'right mouse down':
                if index == 40: self.on_craft_output_click()
                elif 41 <= index <= 44: self.on_armor_slot_click(index)
                else: self.on_slot_right_click(index)
        else:
            self.tooltip.visible = False

    def show_tooltip(self, index):
        item = self.items[index]
        if item:
            data = BLOCK_DATA.get(item['id'])
            if data:
                self.tooltip.text = data['name']
                self.tooltip.position = (mouse.x + 0.02, mouse.y + 0.02)
                self.tooltip.visible = True
                return
        self.tooltip.visible = False

    def update_ui(self):
        for slot in self.slots:
            if slot.my_index != -1: 
                item = self.items[slot.my_index]
                if item:
                    block_id = item['id']
                    count = item['count']
                    data = BLOCK_DATA.get(block_id)
                    
                    if data and 'texture' in data:
                        slot.item_icon.texture = data['texture']
                        slot.item_icon.color = color.white
                    else:
                        slot.item_icon.color = color.red
                    
                    slot.item_icon.visible = True
                    
                    if count > 1:
                        slot.item_count_text.text = str(count)
                        slot.item_count_text.visible = True
                        slot.item_count_shadow.text = str(count)
                        slot.item_count_shadow.visible = True
                    else:
                        slot.item_count_text.text = "" 
                        slot.item_count_text.visible = False
                        slot.item_count_shadow.text = ""
                        slot.item_count_shadow.visible = False
                else:
                    slot.item_icon.visible = False
                    slot.item_count_text.text = ""
                    slot.item_count_text.visible = False
                    slot.item_count_shadow.text = ""
                    slot.item_count_shadow.visible = False
        

        if self.hand_item:
            block_id = self.hand_item['id']
            count = self.hand_item['count']
            data = BLOCK_DATA.get(block_id)
            
            if data and 'texture' in data:
                self.hand_icon.texture = data['texture']
                self.hand_icon.color = color.white 
            else:
                self.hand_icon.color = color.red

            self.hand_icon.visible = True
            
            if count > 1:
                self.hand_text.text = str(count)
                self.hand_text.visible = True
            else:
                self.hand_text.text = ""
                self.hand_text.visible = False
        else:
            self.hand_icon.visible = False
            self.hand_text.text = ""
            self.hand_text.visible = False

    def on_slot_left_click(self, index):
        clicked_item = self.items[index]
        cursor_item = self.hand_item
        
        if cursor_item is None:
            if clicked_item is not None:
                self.hand_item = clicked_item
                self.items[index] = None
        else:
            if clicked_item is None:
                self.items[index] = cursor_item
                self.hand_item = None
            else:
                if clicked_item['id'] == cursor_item['id']:
                    space = 64 - clicked_item['count']
                    if space > 0:
                        to_add = min(space, cursor_item['count'])
                        clicked_item['count'] += to_add
                        cursor_item['count'] -= to_add
                        if cursor_item['count'] <= 0:
                            self.hand_item = None
                else:
                    self.items[index] = cursor_item
                    self.hand_item = clicked_item
        

        if 41 <= index <= 44 and self.player_ref:
            self.player_ref.on_armor_changed(index)
        
        if 36 <= index <= 39: self.check_crafting()
        self.update_ui()

    def on_slot_right_click(self, index):
        clicked_item = self.items[index]
        cursor_item = self.hand_item

        if cursor_item is None:
            if clicked_item is not None:
                total = clicked_item['count']
                take_amount = math.floor(total / 2) 
                leave_amount = total - take_amount
                
                if take_amount > 0:
                    self.hand_item = {'id': clicked_item['id'], 'count': take_amount}
                    clicked_item['count'] = leave_amount
                elif total == 1:
                    self.hand_item = clicked_item
                    self.items[index] = None
        else:
            if clicked_item is None:
                self.items[index] = {'id': cursor_item['id'], 'count': 1}
                cursor_item['count'] -= 1
                if cursor_item['count'] <= 0:
                    self.hand_item = None
            else:
                if clicked_item['id'] == cursor_item['id']:
                    if clicked_item['count'] < 64:
                        clicked_item['count'] += 1
                        cursor_item['count'] -= 1
                        if cursor_item['count'] <= 0:
                            self.hand_item = None
                else:
                    self.items[index] = cursor_item
                    self.hand_item = clicked_item


        if 41 <= index <= 44 and self.player_ref:
            self.player_ref.on_armor_changed(index)
            
        if 36 <= index <= 39: self.check_crafting()
        self.update_ui()

    def on_armor_slot_click(self, index):
        """Handle armor slot clicks with validation"""
        valid_items = []
        if index == 41: valid_items = [IRON_HELMET, DIAMOND_HELMET]
        elif index == 42: valid_items = [IRON_CHESTPLATE, DIAMOND_CHESTPLATE]
        elif index == 43: valid_items = [IRON_LEGGINGS, DIAMOND_LEGGINGS]
        elif index == 44: valid_items = [IRON_BOOTS, DIAMOND_BOOTS]
        
        cursor_item = self.hand_item
        

        if cursor_item is None:
            self.on_slot_left_click(index)
            return
        

        if cursor_item['id'] in valid_items:
            self.on_slot_left_click(index)
        else:
            print(f"Cannot place {BLOCK_DATA.get(cursor_item['id'], {}).get('name', 'item')} in this armor slot!")

    def check_crafting(self):
        grid = [
            [self.items[36], self.items[37]],
            [self.items[38], self.items[39]]
        ]
        result = check_recipe(grid, is_3x3=False)
        if result:
            out_id, out_count = result
            self.items[40] = {'id': out_id, 'count': out_count}
        else:
            self.items[40] = None

    def on_craft_output_click(self):
        out_item = self.items[40]
        if out_item is None: return
        cursor_item = self.hand_item
        can_take = False
        if cursor_item is None: can_take = True
        elif cursor_item['id'] == out_item['id'] and cursor_item['count'] + out_item['count'] <= 64: can_take = True
            
        if can_take:
            if cursor_item is None:
                self.hand_item = out_item
            else:
                self.hand_item['count'] += out_item['count']
            
            for i in range(36, 40):
                if self.items[i]:
                    self.items[i]['count'] -= 1
                    if self.items[i]['count'] <= 0:
                        self.items[i] = None
            
            self.check_crafting()
            self.update_ui()

    def add_item_dict(self, item_dict):
        """Menambahkan item (dict) ke inventory"""
        if not item_dict: return
        self.add_item(item_dict['id'], item_dict['count'])

    def add_item(self, block_id, count=1):

        for i in range(36):
            item = self.items[i]
            if item and item['id'] == block_id and item['count'] < 64:
                space = 64 - item['count']
                to_add = min(space, count)
                item['count'] += to_add
                count -= to_add
                if count <= 0:
                    self.update_ui()
                    return


        while count > 0:
            new_item = {'id': block_id, 'count': min(count, 64)}
            placed = False
            
    
            sel_idx = self.selected_index
            if 0 <= sel_idx < 9 and self.items[sel_idx] is None:
                self.items[sel_idx] = new_item
                placed = True
            else:
        
                for i in range(9):
                    if self.items[i] is None:
                        self.items[i] = new_item
                        placed = True
                        break
                
        
                if not placed:
                    for i in range(9, 36):
                        if self.items[i] is None:
                            self.items[i] = new_item
                            placed = True
                            break
            
            if placed:
                count -= new_item['count']
            else:
                print("Inventory Penuh!")
                break
        
        self.update_ui()

    def decrease_active_item(self):
        item = self.items[self.selected_index]
        if item:
            item['count'] -= 1
            if item['count'] <= 0:
                self.items[self.selected_index] = None
            self.update_ui()

    def update(self):
        if self.hand_item:
            self.hand_icon.position = (mouse.x, mouse.y)
            self.hand_icon.z = -100 
        if not self.is_open:
            self.tooltip.visible = False

    def select_slot(self, index):
        if 0 <= index < 9:
            self.selected_index = index
            self.highlight_selected_hotbar()

    def highlight_selected_hotbar(self):
        for i, slot in enumerate(self.hotbar_slots):
            if i == self.selected_index:
                slot.color = color.rgba(1,1,1,0.5)
                slot.scale = 0.08 
            else:
                slot.color = color.rgba(1,1,1,0.2)
                slot.scale = 0.08

    def get_active_block(self):
        item = self.items[self.selected_index]
        return item['id'] if item else None

    def toggle(self):
        self.is_open = not self.is_open
        self.main_panel.enabled = self.is_open
        
        if self.is_open:
            mouse.visible = True
            mouse.locked = False
        else:
            mouse.visible = True
            mouse.locked = False
            
            if self.hand_item:
                self.add_item_dict(self.hand_item)
                self.hand_item = None
                
        
                for i in range(36, 40):
                    if self.items[i]:
                        self.add_item_dict(self.items[i])
                        self.items[i] = None
                
                self.items[40] = None
                self.update_ui()
