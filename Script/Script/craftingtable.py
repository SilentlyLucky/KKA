from ursina import *
from config import *
from craft import check_recipe
import math

class CraftingTableUI(Entity):
    def __init__(self, inventory_ref, **kwargs):
        super().__init__(parent=camera.ui, enabled=False)
        self.inventory_ref = inventory_ref
        
        self.bg = Entity(
            parent=self, 
            model='quad', 
            scale=(0.8, 0.8), 
            texture='../Assets/GUI/crafting_table.png',            
            color=color.white,
            z=1
        )
        
        self.tooltip = Text(parent=camera.ui, text="", origin=(0, 0), scale=1.5, color=color.white, z=-100, visible=False, background=True)
        self.tooltip.background.color = color.rgba(0,0,0,0.2)
        self.tooltip.background.scale_x = 0.15
        self.tooltip.background.scale_y = 0.05

        self.inv_slots_visual = [] 
        self.craft_slots_visual = []
        
        self.craft_items = [None] * 10 
        
        # Hotbar (0-8)
        for i in range(9):
            s = self._create_slot(index=i, x=(i - 4) * 0.09, y=-0.44)
            self.inv_slots_visual.append(s)

        # Main Storage (9-35)
        start_y = -0.042 # Turunkan sedikit agar masuk ke kotak inventory bawah
        for row in range(3):
            for col in range(9):
                idx = 9 + (row * 9) + col
                s = self._create_slot(
                    index=idx,
                    x=(col - 4) * 0.0816, # Jarak antar kolom lebih rapat (asumsi)
                    y=start_y - (row * 0.086) # Jarak antar baris
                )
                self.inv_slots_visual.append(s)

        """ self.crafting_label = Text(parent=self, text="Crafting", x=-0.3, y=0.35, scale=1.5, color=color.white) """

        grid_start_x = -0.23
        grid_start_y = 0.276
        craft_scale = 0.08    # Ukuran satu slot
        craft_spacing = 0.0035 
        
        for row in range(3):
            for col in range(3):
                internal_idx = (row * 3) + col

                s = self._create_slot(
                    index=100 + internal_idx, 
                    x=grid_start_x + (col * (craft_spacing + craft_scale)),
                    y=grid_start_y - (row * (craft_spacing + craft_scale)),
                    col=color.rgba(0,0,0,0.1)
                )
                self.craft_slots_visual.append(s)

        # Output Slot (Besar)
        self.output_slot = self._create_slot(
            index=109,
            x=0.198, 
            y=0.195,        
            scale=0.11,             
            col=color.rgba(0,0,0,0.1)
        )
        self.craft_slots_visual.append(self.output_slot)
        
        # Arrow Visual
        """ Text(parent=self, text="->", x=grid_start_x + (2.8 * craft_spacing), y=grid_start_y - craft_spacing, scale=2) """

        # Close Button
        Button(parent=self, text="x", color=color.red, scale=(0.05, 0.05), x=0.45, y=0.38, on_click=self.close)

    def _create_slot(self, index, x, y=0, scale=0.08, col=color.rgba(1,1,1,0.1)):
        slot = Button(
            parent=self,
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
        slot.item_count_text = Text(parent=slot, text="", origin=(0.5, -0.5), position=(0.45, -0.45), scale=2.5 * scale, color=color.white, z=-1)
        slot.item_count_shadow = Text(parent=slot, text="", origin=(0.5, -0.5), position=(0.46, -0.46), scale=2.6 * scale, color=color.black, z=-0.9)
        
        return slot

    def input(self, key):
        if not self.enabled: 
            self.tooltip.visible = False
            return

        hovered_slot = mouse.hovered_entity
        if hovered_slot and isinstance(hovered_slot, Button) and hasattr(hovered_slot, 'my_index'):
            index = hovered_slot.my_index
            self.show_tooltip(index)

            if key == 'left mouse down':
                if index == 109: # Output
                    self.on_craft_output_click()
                else:
                    self.on_slot_left_click(index)
            elif key == 'right mouse down':
                if index == 109: # Output
                    self.on_craft_output_click()
                else:
                    self.on_slot_right_click(index)
            
            # Update UI setelah interaksi
            self.update_ui()
            self.inventory_ref.update_ui()
        else:
            self.tooltip.visible = False

    # --- HELPER ACCESSORS ---
    def get_item_at(self, index):
        if index < 100:
            return self.inventory_ref.items[index]
        elif index < 109:
            return self.craft_items[index - 100]
        elif index == 109:
            return self.craft_items[9]
        return None

    def set_item_at(self, index, item):
        if index < 100:
            self.inventory_ref.items[index] = item
        elif index < 109:
            self.craft_items[index - 100] = item
        # Index 109 (Output) biasanya di-set otomatis oleh check_crafting

    def show_tooltip(self, index):
        item = self.get_item_at(index)
        if item:
            data = BLOCK_DATA.get(item['id'])
            if data:
                self.tooltip.text = data['name']
                self.tooltip.position = (mouse.x + 0.02, mouse.y + 0.02)
                self.tooltip.visible = True
                return
        self.tooltip.visible = False

    # --- LOGIC INTERACTIONS (Mirip inventory.py) ---
    
    def on_slot_left_click(self, index):
        clicked_item = self.get_item_at(index)
        cursor_item = self.inventory_ref.hand_item
        
        if cursor_item is None:
            if clicked_item is not None:
                self.inventory_ref.hand_item = clicked_item
                self.set_item_at(index, None)
        else:
            if clicked_item is None:
                self.set_item_at(index, cursor_item)
                self.inventory_ref.hand_item = None
            else:
                # Stack
                if clicked_item['id'] == cursor_item['id']:
                    space = 64 - clicked_item['count']
                    if space > 0:
                        to_add = min(space, cursor_item['count'])
                        clicked_item['count'] += to_add
                        cursor_item['count'] -= to_add
                        if cursor_item['count'] <= 0:
                            self.inventory_ref.hand_item = None
                else:
                    # Swap
                    self.set_item_at(index, cursor_item)
                    self.inventory_ref.hand_item = clicked_item
        
        # Cek crafting jika area crafting berubah
        if 100 <= index < 109:
            self.check_crafting()

    def on_slot_right_click(self, index):
        clicked_item = self.get_item_at(index)
        cursor_item = self.inventory_ref.hand_item

        if cursor_item is None:
            # Ambil setengah
            if clicked_item is not None:
                total = clicked_item['count']
                take_amount = math.floor(total / 2)
                leave_amount = total - take_amount
                
                if take_amount > 0:
                    self.inventory_ref.hand_item = {'id': clicked_item['id'], 'count': take_amount}
                    clicked_item['count'] = leave_amount
                    if clicked_item['count'] <= 0:
                        self.set_item_at(index, None)
                elif total == 1:
                    self.inventory_ref.hand_item = clicked_item
                    self.set_item_at(index, None)
        else:
            # Taruh 1 item
            if clicked_item is None:
                self.set_item_at(index, {'id': cursor_item['id'], 'count': 1})
                cursor_item['count'] -= 1
                if cursor_item['count'] <= 0:
                    self.inventory_ref.hand_item = None
            else:
                # Jika item sama, tambah 1
                if clicked_item['id'] == cursor_item['id']:
                    if clicked_item['count'] < 64:
                        clicked_item['count'] += 1
                        cursor_item['count'] -= 1
                        if cursor_item['count'] <= 0:
                            self.inventory_ref.hand_item = None
                else:
                    # Jika beda, swap
                    self.set_item_at(index, cursor_item)
                    self.inventory_ref.hand_item = clicked_item

        if 100 <= index < 109:
            self.check_crafting()

    def check_crafting(self):
        # Konversi list 1D (9 item) ke Grid 3x3 untuk checker
        grid = []
        for r in range(3):
            row = []
            for c in range(3):
                row.append(self.craft_items[r*3 + c])
            grid.append(row)
            
        result = check_recipe(grid, is_3x3=True)
        
        if result:
            out_id, out_count = result
            self.craft_items[9] = {'id': out_id, 'count': out_count}
        else:
            self.craft_items[9] = None

    def on_craft_output_click(self):
        out_item = self.craft_items[9]
        if out_item is None: return
        
        cursor_item = self.inventory_ref.hand_item
        
        can_take = False
        if cursor_item is None:
            can_take = True
        elif cursor_item['id'] == out_item['id'] and cursor_item['count'] + out_item['count'] <= 64:
            can_take = True
            
        if can_take:
            if cursor_item is None:
                self.inventory_ref.hand_item = out_item
            else:
                self.inventory_ref.hand_item['count'] += out_item['count']
            
            # Kurangi bahan (1 per slot)
            for i in range(9):
                if self.craft_items[i]:
                    self.craft_items[i]['count'] -= 1
                    if self.craft_items[i]['count'] <= 0:
                        self.craft_items[i] = None
            
            self.check_crafting()

    def update_ui(self):
        # 1. Update Inventory Slots Visuals (0-35)
        for i, slot in enumerate(self.inv_slots_visual):
            self._update_single_slot(slot, self.inventory_ref.items[i])
            
        # 2. Update Crafting Slots Visuals (0-8)
        for i in range(9):
            slot = self.craft_slots_visual[i]
            self._update_single_slot(slot, self.craft_items[i])
            
        # 3. Update Output Slot
        self._update_single_slot(self.output_slot, self.craft_items[9])

    def _update_single_slot(self, slot, item_data):
        if item_data:
            data = BLOCK_DATA.get(item_data['id'])

            if data and 'texture' in data:
                # Muat tekstur dari BLOCK_DATA dan pastikan warna ikon putih
                slot.item_icon.texture = data['texture']
                slot.item_icon.color = color.white 
            else:
                slot.item_icon.color = color.red

            slot.item_icon.visible = True
            
            if item_data['count'] > 1:
                slot.item_count_text.text = str(item_data['count'])
                slot.item_count_text.enabled = True
                slot.item_count_text.visible = True
                slot.item_count_shadow.text = str(item_data['count'])
                slot.item_count_shadow.enabled = True
                slot.item_count_shadow.visible = True
            else:
                slot.item_count_text.text = ""
                slot.item_count_text.enabled = False
                slot.item_count_shadow.text = ""
                slot.item_count_shadow.enabled = False

        else:
            slot.item_icon.visible = False
            slot.item_count_text.text = ""
            slot.item_count_text.enabled = False
            slot.item_count_shadow.text = ""
            slot.item_count_shadow.enabled = False

    def open(self):
        self.enabled = True
        
        if self.inventory_ref.is_open:
            self.inventory_ref.toggle() 
            
        self.update_ui()
        mouse.visible = True
        mouse.locked = False

    def close(self):
        self.enabled = False
        self.tooltip.visible = False
        
        for i in range(9):
            if self.craft_items[i]:
                self.inventory_ref.add_item_dict(self.craft_items[i])
                self.craft_items[i] = None
        
        self.craft_items[9] = None # Clear output
        
        if self.inventory_ref.hand_item:
            self.inventory_ref.add_item_dict(self.inventory_ref.hand_item)
            self.inventory_ref.hand_item = None
            
        mouse.visible = True
        mouse.locked = False
        self.inventory_ref.update_ui()