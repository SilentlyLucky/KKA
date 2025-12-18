from ursina import *
from config import *
from block import Block
import time
from inventory import Inventory 
from craftingtable import CraftingTableUI
from bed import set_spawn_point

class Player(Entity):
    def __init__(self, world_instance, on_death=None, inventory_data=None, saved_spawn_point=None, **kwargs):
        if 'position' not in kwargs:
            kwargs['position'] = (WIDTH/2, 20)

        super().__init__(
            parent=scene,
            color=color.clear,
            origin_y=0, 
            traverse_target=world_instance.fg_parent,
            **kwargs
        )
        self.world = world_instance
        self.on_death = on_death or (lambda: None)
        self.dead = False

        if saved_spawn_point:
            self.spawn_x = saved_spawn_point[0]
            self.spawn_y = saved_spawn_point[1]
        else:
            self.spawn_x = int(self.x)
            self.spawn_y = int(self.y)
        
        self.collider = 'box' 
        self.scale = (0.9, 1.8) 
        
        target_visual_width = 1.0
        target_visual_height = 2.0
        
        calc_scale_x = (target_visual_width / self.scale_x)
        calc_scale_y = (target_visual_height / self.scale_y)
        
        self.visual = Entity(
            parent=self,
            scale=(calc_scale_x, calc_scale_y), 
            position=(0.015, 0.05, 0),
            color=color.white
        )

        mouse.ignore = (self, self.visual)
        
        self.skin()

        # Cursor
        self.cursor = Entity(parent=camera, model='quad', color=color.red, scale=.05, rotation_z=45, z=-1)

        self.mouse_plane = Entity(
            model='plane',
            scale=9999,
            collider='box',
            color=color.clear,
            z=0, 
            visible=False,
            enabled=True
        )

        # Physics Stats
        self.walk_speed = PLAYER_WALK_SPEED
        self.jump_force = PLAYER_JUMP_FORCE
        self.gravity = GLOBAL_GRAVITY
        self.max_fall_speed = MAX_FALL_SPEED
        self.attack_range = PLAYER_ATTACK_RANGE
        
        self.y_velocity = 0
        self.is_grounded = False

        # Inventory
        self.inventory_system = Inventory(load_data=inventory_data)
        
        # UI Crafting Table 3x3
        self.crafting_table_ui = CraftingTableUI(inventory_ref=self.inventory_system)

        # Health
        self.damage_flash_timer = 0
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.heart_container = Entity(parent=camera.ui, position=(-0.7, 0.45), scale=1)
        self.hearts = []
        self.max_hearts = 10

        # Load heart textures
        self.heart_empty_tex = load_texture('../Assets/Interface/Heart_Empty.png')
        self.heart_half_tex = load_texture('../Assets/Interface/Heart_Half.png')
        self.heart_full_tex = load_texture('../Assets/Interface/Heart_Full.png')

        heart_spacing = 0.04
        for i in range(self.max_hearts):
            heart = Entity(
                parent=self.heart_container,
                model='quad',
                texture=self.heart_full_tex,
                scale=(0.03, 0.03),
                position=(i * heart_spacing, 0, 0),
                color=color.white
            )
            self.hearts.append(heart)

        # === ARMOR SYSTEM ===
        self.equipped_armor = {
            'helmet': None,
            'chestplate': None,
            'leggings': None,
            'boots': None
        }
        
        self.max_armor = 20  # Max armor points (10 icons x 2 points each)
        self.armor = 0
        
        # Load Armor textures
        self.armor_full_tex = load_texture('../Assets/Interface/Armor_Full.png')
        self.armor_half_tex = load_texture('../Assets/Interface/Armor_Half.png')
        self.armor_empty_tex = load_texture('../Assets/Interface/Armor_Empty.png')

        self.armor_container = Entity(parent=camera.ui, position=(0.8, 0.45), scale=1)
        self.armor_icons = []
        
        armor_spacing = 0.04 
        for i in range(10):
            icon = Entity(
                parent=self.armor_container,
                model='quad',
                texture=self.armor_empty_tex,
                scale=(0.03, 0.03),
                position=(-i * armor_spacing, 0, 0),
                color=color.white
            )
            self.armor_icons.append(icon)

        # === HUNGER SYSTEM ===
        self.max_food = 20  # Max food points (10 icons x 2 points each)
        self.food = 20
        self.food_depletion_rate = 0.2  # Points per second
        self.food_timer = 0
        self.starving = False
        self.starvation_damage_rate = 2.0  # Seconds between damage when starving
        self.starvation_timer = 0
        
        # Load food textures
        self.food_full_tex = load_texture('../Assets/Interface/Food_Full.png')
        self.food_half_tex = load_texture('../Assets/Interface/Food_Half.png')
        self.food_empty_tex = load_texture('../Assets/Interface/Food_Empty.png')

        self.food_container = Entity(parent=camera.ui, position=(-0.34, 0.4), scale=1)
        self.food_icons = []
        
        food_spacing = 0.04 
        for i in range(10):
            icon = Entity(
                parent=self.food_container,
                model='quad',
                texture=self.food_full_tex,
                scale=(0.03, 0.03),
                position=(-i * food_spacing, 0, 0),
                color=color.white
            )
            self.food_icons.append(icon)

    def is_solid_hit(self, hit):
        return (
            hit.hit and
            hasattr(hit.entity, 'solid') and
            hit.entity.solid
        )
    
    def get_env_light(self):
        x = int(round(self.x))
        y = int(self.y - self.scale_y / 2) + 1

        if 0 <= x < WIDTH and 0 <= y < DEPTH:
            return self.world.light_map[x][y]
        return 14

    def apply_environment_light(self):
        lvl = self.get_env_light()
        lvl = max(0, min(14, lvl))

        brightness = 0.15 + 0.85 * (lvl / 14.0)
        base_color = color.white * brightness

        if self.damage_flash_timer > 0:
            self.visual.color = color.red
            self.damage_flash_timer -= time.dt
        else:
            self.player_graphics.color = color.white * brightness

    def calculate_armor(self):
        """Calculate total armor from equipped pieces"""
        total = 0
        for slot, item_id in self.equipped_armor.items():
            if item_id and item_id in TOOL_ARMOR:
                total += TOOL_ARMOR[item_id]
        return total

    def sync_armor_from_inventory(self):
        """Sync armor equipment from inventory armor slots (41-44)"""
        for inv_index, slot_name in self.armor_slot_mapping.items():
            item = self.inventory_system.items[inv_index]
            if item:
                self.equipped_armor[slot_name] = item['id']
            else:
                self.equipped_armor[slot_name] = None
        
        self.armor = self.calculate_armor()
        self.update_armor_ui()  # Update the visual armor bar
        print(f"[ARMOR SYNC] Total armor: {self.armor}")

    def on_armor_changed(self, slot_index):
        """Called by inventory when armor slot changes"""
        if slot_index in self.armor_slot_mapping:
            slot_name = self.armor_slot_mapping[slot_index]
            item = self.inventory_system.items[slot_index]
            
            if item:
                self.equipped_armor[slot_name] = item['id']
            else:
                self.equipped_armor[slot_name] = None
            
            self.armor = self.calculate_armor()
            self.update_armor_ui()  # Update the visual armor bar
            print(f"[ARMOR CHANGE] {slot_name}: {item['id'] if item else None} - Total armor: {self.armor}")

    def equip_armor(self, item_id):
        """Equip an armor piece"""
        armor_slot = None
        
        # Determine which slot this armor goes in
        if item_id in (IRON_HELMET, DIAMOND_HELMET):
            armor_slot = 'helmet'
        elif item_id in (IRON_CHESTPLATE, DIAMOND_CHESTPLATE):
            armor_slot = 'chestplate'
        elif item_id in (IRON_LEGGINGS, DIAMOND_LEGGINGS):
            armor_slot = 'leggings'
        elif item_id in (IRON_BOOTS, DIAMOND_BOOTS):
            armor_slot = 'boots'
        
        if armor_slot:
            # Return old armor to inventory if slot was occupied
            old_armor = self.equipped_armor[armor_slot]
            if old_armor:
                self.inventory_system.add_item(old_armor)
            
            # Equip new armor
            self.equipped_armor[armor_slot] = item_id
            self.armor = self.calculate_armor()
            print(f"Equipped {BLOCK_DATA[item_id]['name']} in {armor_slot} slot. Total armor: {self.armor}")
            return True
        return False

    def unequip_armor(self, slot_name):
        """Remove armor from a specific slot"""
        if slot_name in self.equipped_armor and self.equipped_armor[slot_name]:
            item_id = self.equipped_armor[slot_name]
            self.inventory_system.add_item(item_id)
            self.equipped_armor[slot_name] = None
            self.armor = self.calculate_armor()
            print(f"Unequipped {BLOCK_DATA[item_id]['name']}. Total armor: {self.armor}")
            return True
        return False

    def eat_food(self, item_id):
        """Consume food to restore hunger"""
        if item_id in FOOD:
            food_value = FOOD[item_id]
            old_food = self.food
            self.food = min(self.max_food, self.food + food_value)
            
            # Also restore small amount of health when eating
            if self.food >= self.max_food:
                self.health = min(self.max_health, self.health + 1)
            
            print(f"Ate {BLOCK_DATA[item_id]['name']}. Hunger: {old_food} -> {self.food}")
            return True
        return False

    def update_hunger(self, dt):
        """Update hunger system - depletes over time"""
        # Deplete food over time
        self.food_timer += dt
        if self.food_timer >= 1.0:  # Every second
            self.food = max(0, self.food - self.food_depletion_rate)
            self.food_timer = 0
        
        # Starvation damage when food reaches 0
        if self.food <= 0:
            if not self.starving:
                self.starving = True
                print("You are starving!")
            
            self.starvation_timer += dt
            if self.starvation_timer >= self.starvation_damage_rate:
                self.take_damage(1)
                self.starvation_timer = 0
                print("Starvation damage!")
        else:
            self.starving = False
            self.starvation_timer = 0

    def update(self):
        self.z = FG_Z 
        
        if mouse.world_point:
            mx = round(mouse.world_point.x)
            my = round(mouse.world_point.y)
            
            if hasattr(self, 'cursor_highlight') and self.cursor_highlight:
                self.cursor_highlight.position = (mx, my)
                self.cursor_highlight.enabled = True
        else:
            if hasattr(self, 'cursor_highlight') and self.cursor_highlight:
                self.cursor_highlight.enabled = False

        if self.y < -5 and not self.dead:
            self.die()
        
        dt = time.dt
        self.apply_environment_light()
        self.update_health_ui()
        self.update_armor_ui()
        self.update_food_ui()
        self.update_hunger(dt)  # Add hunger depletion
        
        if self.y < -20: 
            self.take_damage(20)
            self.respawn()

        # HORIZONTAL MOVEMENT
        dx = held_keys['d'] - held_keys['a']
        move_amount = dx * self.walk_speed * dt
        
        if dx != 0:
            hit_wall = False
            dist_x = (self.scale_x / 2) + 0.1 
            offsets_y = [-0.8, 0, 0.8]
            
            for off_y in offsets_y:
                origin = self.position + Vec3(0, off_y, 0)
                hit = raycast(origin, Vec3(dx, 0, 0), distance=dist_x, ignore=(self, self.visual), debug=False)
                if hit.hit:
                    hit_wall = True
                    break
            
            if not hit_wall:
                self.x += move_amount

        # ANIMATION
        if dx > 0:
            if self.current_anim_state != 'walk_right':
                self.player_graphics.play_animation('walk_right')
                self.current_anim_state = 'walk_right' 
            self.visual.scale_x = abs(self.visual.scale_x)
        elif dx < 0:
            if self.current_anim_state != 'walk_left':
                self.player_graphics.play_animation('walk_left')
                self.current_anim_state = 'walk_left' 
            self.visual.scale_x = abs(self.visual.scale_x)
        else:
            if self.current_anim_state != 'idle':
                self.player_graphics.play_animation('idle')
                self.current_anim_state = 'idle' 

        # VERTICAL PHYSICS
        ray_origin_y = 0 
        ray_direction = Vec3(0, -1, 0)
        ray_dist = (self.scale_y / 2) + 0.1
        
        margin_x = 0.05
        half_w = (self.scale_x / 2) - margin_x
        
        pos_left = self.position + Vec3(-half_w, ray_origin_y, 0)
        pos_right = self.position + Vec3(half_w, ray_origin_y, 0)
        
        hit_l = raycast(pos_left, ray_direction, distance=ray_dist, ignore=(self, self.visual), debug=False)
        hit_r = raycast(pos_right, ray_direction, distance=ray_dist, ignore=(self, self.visual), debug=False)
        
        if self.is_solid_hit(hit_l) or self.is_solid_hit(hit_r):
            self.is_grounded = True
            floor_y = -9999
            if self.is_solid_hit(hit_l): floor_y = max(floor_y, hit_l.world_point.y)
            if self.is_solid_hit(hit_r): floor_y = max(floor_y, hit_r.world_point.y)
            target_y = floor_y + (self.scale_y / 2)
            
            if self.y_velocity <= 0:
                self.y = target_y
                self.y_velocity = 0
        else:
            self.is_grounded = False
            self.y_velocity -= self.gravity * dt
            if self.y_velocity < -self.max_fall_speed: 
                self.y_velocity = -self.max_fall_speed

        if self.y_velocity > 0:
            head_origin = self.position + Vec3(0, self.scale_y/2 - 0.1, 0)
            hit_head = raycast(head_origin, Vec3(0,1,0), distance=0.2, ignore=(self, self.visual), debug=False)
            if self.is_solid_hit(hit_head):
                self.y_velocity = 0 

        self.y += self.y_velocity * dt
        self.z = FG_Z 

    def skin(self):
        self.player_graphics = SpriteSheetAnimation('../Assets/Sprite/MC.png', parent=self.visual, tileset_size=(7,1), fps=8, animations={
            'idle' : ((0,0), (0,0)),
            'walk_right' : ((1,0), (3,0)),
            'walk_left' : ((4,0), (6,0)),
            }
            )
        self.player_graphics.play_animation('idle')
        self.current_anim_state = 'idle'

    def input(self, key):
        if self.dead: return

        if key == 'e':
            if self.crafting_table_ui.enabled:
                self.crafting_table_ui.close()
            else:
                self.inventory_system.toggle()
            return
        
        # Handle armor equipping and food eating with right-click
        if key == 'f':  # Press F to equip armor or eat food from selected slot
            held_item_id = self.inventory_system.get_active_block()
            
            if held_item_id:
                # Try to equip armor
                if held_item_id in TOOL_ARMOR:
                    if self.equip_armor(held_item_id):
                        self.inventory_system.decrease_active_item()
                        return
                
                # Try to eat food
                if held_item_id in FOOD:
                    if self.eat_food(held_item_id):
                        self.inventory_system.decrease_active_item()
                        return
        
        if not self.inventory_system.is_open and not self.crafting_table_ui.enabled:
            if key in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                slot_idx = int(key) - 1
                self.inventory_system.select_slot(slot_idx)

        if key == 'space':
            if self.is_grounded:
                self.y_velocity = self.jump_force
                self.y += 0.1 
                self.is_grounded = False

        if key == 'left mouse down':
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'take_damage'):
                if distance(self.position, mouse.hovered_entity.position) <= self.attack_range:
                    held_item_id = self.inventory_system.get_active_block()
                    dmg = TOOL_DAMAGE.get(held_item_id, 1) 
                    mouse.hovered_entity.take_damage(dmg)
                    return 
                
            if mouse.hovered_entity and isinstance(mouse.hovered_entity, Block): 
                if distance(self.position, mouse.hovered_entity.position) < 5:
                    block_type = mouse.hovered_entity.block_type

                    held_item_id = self.inventory_system.get_active_block()
                    
                    tool_power = 0
                    
                    if held_item_id == WOODEN_PICKAXE: tool_power = 1
                    elif held_item_id == IRON_PICKAXE: tool_power = 3
                    elif held_item_id == DIAMOND_PICKAXE: tool_power = 4
                    
                    block_hardness = 0 
                    
                    if block_type in (STONE, COAL, IRON):
                        block_hardness = 1
                    elif block_type == DIAMOND:
                        block_hardness = 3
                    elif block_type == BEDROCK:
                        block_hardness = 999
                    
                    can_break = tool_power >= block_hardness
                    
                    if can_break:
                        self.world.remove_block(mouse.hovered_entity)
                        
                        item_to_give = block_type
                        if block_type == COAL_ORE: item_to_give = COAL
                        elif block_type == IRON_ORE: item_to_give = IRON
                        elif block_type == DIAMOND_ORE: item_to_give = DIAMOND
                        elif block_type == GLASS: item_to_give = None 
                        
                        if item_to_give:
                            self.inventory_system.add_item(item_to_give)
                    else:
                        print("Not strong enough!") 

        if key == 'right mouse down':
            if mouse.hovered_entity and isinstance(mouse.hovered_entity, Block):
                    if distance(self.position, mouse.hovered_entity.position) < 5:
                        if mouse.hovered_entity.block_type == CRAFTING_TABLE:
                            self.crafting_table_ui.open()
                            return
                        elif mouse.hovered_entity.block_type == BED_BLOCK:
                            set_spawn_point(self, mouse.hovered_entity.position)
                            return

            if mouse.position:
                fov = camera.fov
                world_x = camera.x + (mouse.x * fov)
                world_y = camera.y + (mouse.y * fov)
                
                mx, my = round(world_x), round(world_y)
                
                dx = abs(mx - self.x)
                dy = abs(my - self.y)
                
                safe_x = (self.scale_x/2) + 0.5 
                safe_y = (self.scale_y/2) + 0.5
                
                if not (dx < safe_x and dy < safe_y):
                    dist = distance((mx, my, 0), self.position)
                    
                    if dist < 5:
                        if (mx, my) not in self.world.block_positions:
                            block_to_place = self.inventory_system.get_active_block()
                            
                            if block_to_place:
                                real_block = block_to_place
                                if block_to_place == BED_ITEM: real_block = BED_BLOCK
                                if real_block < 100:
                                    self.world.place_block(mx, my, real_block)
                                    self.inventory_system.decrease_active_item()
                            
    def on_destroy(self):
        if hasattr(self, 'cursor_highlight') and self.cursor_highlight:
            destroy(self.cursor_highlight)
        if hasattr(self, 'inventory_system') and self.inventory_system:
            destroy(self.inventory_system)
        if hasattr(self, 'crafting_table_ui') and self.crafting_table_ui:
            destroy(self.crafting_table_ui)

    def respawn(self):
        self.position = (self.spawn_x, self.spawn_y)
        self.y_velocity = 0
        self.health = self.max_health
        self.food = self.max_food
        self.dead = False
        print(f"Respawned at: ({self.spawn_x}, {self.spawn_y})")

    def die(self):
        if not self.dead:
            self.dead = True
            self.on_death()

    def update_health_ui(self):
        """Update Minecraft-style hearts based on current health"""
        for i in range(self.max_hearts):
            heart_hp_threshold = (i + 1) * 10 
            heart_hp_min = i * 10

            if self.health >= heart_hp_threshold:
                self.hearts[i].texture = self.heart_full_tex
                self.hearts[i].enabled = True
            elif self.health > heart_hp_min:
                self.hearts[i].texture = self.heart_half_tex
                self.hearts[i].enabled = True
            else:
                self.hearts[i].texture = self.heart_empty_tex
                self.hearts[i].enabled = True

    def update_armor_ui(self):
        """Update Minecraft-style armor icons based on current armor"""
        for i in range(10):
            armor_hp_threshold = (i + 1) * 2 
            armor_hp_min = i * 2

            if self.armor >= armor_hp_threshold:
                self.armor_icons[i].texture = self.armor_full_tex
                self.armor_icons[i].enabled = True
            elif self.armor > armor_hp_min:
                self.armor_icons[i].texture = self.armor_half_tex
                self.armor_icons[i].enabled = True
            else:
                self.armor_icons[i].texture = self.armor_empty_tex
                self.armor_icons[i].enabled = True

    def update_food_ui(self):
        """Update Minecraft-style food icons based on current food"""
        for i in range(10):
            food_hp_threshold = (i + 1) * 2 
            food_hp_min = i * 2

            if self.food >= food_hp_threshold:
                self.food_icons[i].texture = self.food_full_tex
                self.food_icons[i].enabled = True
            elif self.food > food_hp_min:
                self.food_icons[i].texture = self.food_half_tex
                self.food_icons[i].enabled = True
            else:
                self.food_icons[i].texture = self.food_empty_tex
                self.food_icons[i].enabled = True

    def take_damage(self, amount):
        """Take damage with armor reduction"""
        # Calculate damage reduction from armor
        # Armor reduces damage by (armor / (armor + 10)) * 100%
        if self.armor > 0:
            reduction = self.armor / (self.armor + 10)
            actual_damage = amount * (1 - reduction)
            print(f"Damage reduced from {amount} to {actual_damage:.1f} by armor ({self.armor} points)")
        else:
            actual_damage = amount
        
        self.health -= actual_damage
        self.visual.color = color.red
        invoke(setattr, self.visual, 'color', color.white, delay=0.1)
        
        if self.health <= 0:

            self.die()
