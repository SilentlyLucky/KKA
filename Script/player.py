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
        
        calc_scale_x = (target_visual_width / self.scale_x)# 1.0 / 0.9 = 1.111...
        calc_scale_y = (target_visual_height / self.scale_y)# 2.0 / 1.8 = 1.111...
        
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
        self.max_hearts = 10  # 10 hearts = 20 health (each heart = 2 HP)

        # Load heart textures
        self.heart_empty_tex = load_texture('../Assets/Interface/Heart_Empty.png')
        self.heart_half_tex = load_texture('../Assets/Interface/Heart_Half.png')
        self.heart_full_tex = load_texture('../Assets/Interface/Heart_Full.png')

        heart_spacing = 0.04  # Spacing between hearts
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
        if self.y < -20: self.take_damage(20); self.respawn()

        # ====================================================
        # CUSTOM PHYSICS (0.9 x 1.8)
        # ====================================================

        # --- 1. HORIZONTAL ---
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

        # --- ANIMATION LOGIC (Moved to update) ---
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

        # --- 2. VERTICAL ---
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
            'idle' : ((0,0), (0,0)),        # makes an animation from (0,0) to (0,0), a single frame
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
                        
                        # --- LOGIKA DROP ITEM ---
                        item_to_give = block_type
                        if block_type == COAL_ORE: item_to_give = COAL
                        elif block_type == IRON_ORE: item_to_give = IRON
                        elif block_type == DIAMOND_ORE: item_to_give = DIAMOND
                        elif block_type == GLASS: item_to_give = None 
                        
                        if item_to_give:
                            self.inventory_system.add_item(item_to_give)
                    else:
                        # Opsional: Beri efek visual/suara kalau gagal break
                        print("Not strong enough!") 

        if key == 'right mouse down':
            print("=== RIGHT MOUSE CLICKED ===")
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
                
                print(f"Mouse screen pos: {mouse.position}")
                print(f"Calculated world pos: ({world_x}, {world_y})")
                print(f"Rounded target: ({mx}, {my})")
                print(f"Player position: ({self.x}, {self.y})")
                
                dx = abs(mx - self.x)
                dy = abs(my - self.y)
                
                safe_x = (self.scale_x/2) + 0.5 
                safe_y = (self.scale_y/2) + 0.5
                
                if not (dx < safe_x and dy < safe_y):
                    print("✓ Not inside player safe zone")
                    
                    dist = distance((mx, my, 0), self.position)
                    print(f"Distance to target: {dist}")
                    
                    if dist < 5:
                        print("✓ Within reach")
                        
                        if (mx, my) not in self.world.block_positions:
                            print("✓ Position is empty - PLACING BLOCK!")
                            block_to_place = self.inventory_system.get_active_block()
                            
                            if block_to_place:
                                real_block = block_to_place
                                if block_to_place == BED_ITEM: real_block = BED_BLOCK
                                if real_block < 100:
                                    self.world.place_block(mx, my, real_block)
                                    self.inventory_system.decrease_active_item()
                        else:
                            print("✗ Position already occupied")
                    else:
                        print("✗ Too far away")
                else:
                    print("✗ Too close to player")
            else:
                print("✗ No mouse position")
                            
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
        self.dead = False
        print(f"Respawned at: ({self.spawn_x}, {self.spawn_y})")

    def die(self):
        if not self.dead:
            self.dead = True
            self.on_death()

    def update_health_ui(self):
        """Update Minecraft-style hearts based on current health"""
        
        for i in range(self.max_hearts):
            heart_hp_threshold = (i + 1) * 2 
            heart_hp_min = i * 2  
            
            if self.health >= heart_hp_threshold:
                # Full heart
                self.hearts[i].texture = self.heart_full_tex
                self.hearts[i].enabled = True
            elif self.health > heart_hp_min:
                # Half heart
                self.hearts[i].texture = self.heart_half_tex
                self.hearts[i].enabled = True
            else:
                # Empty heart
                self.hearts[i].texture = self.heart_empty_tex
                self.hearts[i].enabled = True

    def take_damage(self, amount):
        self.health -= amount
        self.visual.color = color.red
        invoke(setattr, self.visual, 'color', color.azure, delay=0.1)
        if self.health <= 0: self.respawn(); self.health = self.max_health

    def respawn(self):
        print(f"[PLAYER] Respawn at ({self.spawn_x}, {self.spawn_y})")
        self.position = (self.spawn_x, self.spawn_y)
        self.y_velocity = 0
        self.health = self.max_health
        self.dead = False

