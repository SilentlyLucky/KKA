from ursina import *
from config import *
from block import Block
import time

class Player(Entity):
    def __init__(self, world_instance, on_death=None, **kwargs):
        # --- INDUK (FISIK) ---
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

        self.spawn_x = int(self.x)
        self.spawn_y = int(self.y)
        
        # 1. Setting Fisik (Ramping biar gak nyangkut)
        self.collider = 'box' 
        self.scale = (0.9, 1.8) 
        
        # 2. Setting Visual (HARUS PAS 1x2)
        # Kita ingin tampilan akhirnya: Lebar 1.0, Tinggi 2.0
        # Karena parentnya 0.9 x 1.8, kita bagi target dengan parent.
        target_visual_width = 1.0
        target_visual_height = 2.0
        
        calc_scale_x = (target_visual_width / self.scale_x)# 1.0 / 0.9 = 1.111...
        calc_scale_y = (target_visual_height / self.scale_y)# 2.0 / 1.8 = 1.111...
        
        self.visual = Entity(
            parent=self,
            scale=(calc_scale_x, calc_scale_y), # Skala otomatis
            position=(0, 0, 0)
        )
        
        self.skin()

        # Cursor
        """ self.cursor = Entity(parent=camera, model='quad', color=color.red, scale=.05, rotation_z=45, z=-1) """
        self.cursor_highlight = Entity(
        parent=scene, 
        model='quad', 
        color=color.rgba(255, 0, 0, 100),
        scale=(1.1, 1.1), 
        z=FG_Z - 0.2, 
        enabled=False,
        double_sided=True
        )
        # Physics Stats
        self.walk_speed = 5
        self.jump_force = 12
        self.gravity = 30
        self.max_fall_speed = 20
        self.y_velocity = 0
        self.is_grounded = False

        # Health
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.health_bar_bg = Entity(parent=camera.ui, model='quad', color=color.red.tint(-0.2), scale=(0.5, 0.03), position=(-0.6, 0.45))
        self.health_bar = Entity(parent=camera.ui, model='quad', color=color.green, scale=(0.5, 0.03), position=(-0.6, 0.45))

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
            if self.current_anim_state != 'walk_right': # Check if state is different
                self.player_graphics.play_animation('walk_right')
                self.current_anim_state = 'walk_right' # Update state
            self.visual.scale_x = abs(self.visual.scale_x)
        elif dx < 0:
            if self.current_anim_state != 'walk_left': # Check if state is different
                self.player_graphics.play_animation('walk_left')
                self.current_anim_state = 'walk_left' # Update state
            self.visual.scale_x = abs(self.visual.scale_x)
        else:
            if self.current_anim_state != 'idle': # Check if state is different
                self.player_graphics.play_animation('idle')
                self.current_anim_state = 'idle' # Update state

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
        
        if hit_l.hit or hit_r.hit:
            self.is_grounded = True
            floor_y = -9999
            if hit_l.hit: floor_y = max(floor_y, hit_l.world_point.y)
            if hit_r.hit: floor_y = max(floor_y, hit_r.world_point.y)
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
            if hit_head.hit:
                self.y_velocity = 0 

        self.y += self.y_velocity * dt
        self.z = FG_Z 

    def skin(self):
        self.player_graphics = SpriteSheetAnimation('../Assets/Sprite/MC.png', parent=self.visual, tileset_size=(8,1), fps=8, animations={
            'idle' : ((0,0), (0,0)),        # makes an animation from (0,0) to (0,0), a single frame
            'walk_right' : ((1,0), (3,0)),
            'walk_left' : ((4,0), (7,0)),
            }
            )
        self.player_graphics.play_animation('idle')
        self.current_anim_state = 'idle'

    def input(self, key):
        if self.dead: return

        if key == 'space':
            if self.is_grounded:
                self.y_velocity = self.jump_force
                self.y += 0.1 
                self.is_grounded = False

        if key == 'left mouse down':
             if mouse.hovered_entity and isinstance(mouse.hovered_entity, Block): 
                if distance(self.position, mouse.hovered_entity.position) < 5:
                    self.world.remove_block(mouse.hovered_entity)
        if key == 'right mouse down':
            if mouse.world_point:
                mx, my = round(mouse.world_point.x), round(mouse.world_point.y)
                dx = abs(mx - self.x)
                dy = abs(my - self.y)
                safe_x = (self.scale_x/2) + 0.5 
                safe_y = (self.scale_y/2) + 0.5 
                if not (dx < safe_x and dy < safe_y):
                    if (mx, my) not in self.world.block_positions:
                        if distance((mx, my, 0), self.position) < 5:
                            self.world.place_block(mx, my, DIRT)
    def on_destroy(self):
        if hasattr(self, 'cursor_highlight') and self.cursor_highlight:
            destroy(self.cursor_highlight)

    def respawn(self):
        self.position = (self.spawn_x, self.spawn_y)
        self.velocity = (0,0)
        self.dead = False

    def die(self):
        if not self.dead:
            self.dead = True
            self.on_death()

    def update_health_ui(self):
        s = 0.5 * (self.health / self.max_health)
        self.health_bar.scale_x = max(0, s)
        self.health_bar.x = self.health_bar_bg.x - (0.5 - self.health_bar.scale_x) / 2

    def take_damage(self, amount):
        self.health -= amount
        self.visual.color = color.red
        invoke(setattr, self.visual, 'color', color.azure, delay=0.1)
        if self.health <= 0: self.respawn(); self.health = self.max_health

    def respawn(self):
        self.position = (int(WIDTH/2), self.world.surface_heights[int(WIDTH/2)] + 4)
        self.y_velocity = 0
