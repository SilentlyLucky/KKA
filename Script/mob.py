from ursina import *
import config
import heapq
from collections import deque
import random
import time

# --- Helper Functions (Logic Pathfinding Teman Anda) ---

def get_neighbors(world, pos):
    x, y = pos
    res = []
    # 8 Arah
    for dx, dy in [(1,0), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < config.WIDTH and 0 <= ny < config.DEPTH):
            continue
        if world.is_standable(nx, ny):
            res.append((nx, ny))
    return res

def bfs(world, start, goal, max_steps=300):
    q = deque([(start, [start])])
    visited = {start}
    steps = 0
    while q:
        steps += 1
        if steps > max_steps: return []
        curr, path = q.popleft()
        if curr == goal: return path[1:]
        
        for n in get_neighbors(world, curr):
            if n not in visited:
                visited.add(n)
                q.append((n, path + [n]))
    return []

def astar(world, start, goal, max_steps=300):
    def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    
    open_set = [(0, start)]
    came = {}
    g = {start: 0}
    steps = 0
    
    while open_set:
        steps += 1
        if steps > max_steps: return []
        
        _, curr = heapq.heappop(open_set)
        
        if curr == goal:
            path = [curr]
            while curr in came:
                curr = came[curr]
                path.insert(0, curr)
            return path[1:]
            
        for n in get_neighbors(world, curr):
            ng = g[curr] + 1
            if n not in g or ng < g[n]:
                g[n] = ng
                came[n] = curr
                heapq.heappush(open_set, (ng + h(n, goal), n))
    return []

# --- Dummy functions untuk menjaga kompatibilitas dengan main.py ---
# Karena kita kembali ke AI synchronous, kita tidak butuh executor, 
# tapi main.py masih memanggil fungsi ini.
def initialize_ai_executor():
    pass

def shutdown_ai_executor():
    pass

# =====================================================
# ZOMBIE
# =====================================================
class Zombie(Entity):
    def __init__(self, world, player, **kwargs):
        super().__init__(
            parent=scene,
            model='quad',
            color=color.clear, 
            origin_y=0,
            position=kwargs.get('position', (0,0)),
            z=config.FG_Z,
            collider='box'
        )
        self.world = world
        self.player = player
        self.collision = False
        
        self.scale = (0.9, 1.8) 
        self.max_health = config.ZOMBIE_MAX_HEALTH
        self.health = self.max_health
        self.walk_speed = config.ZOMBIE_WALK_SPEED
        self.run_speed = config.ZOMBIE_RUN_SPEED
        self.jump_force = config.ZOMBIE_JUMP_FORCE
        self.gravity = config.GLOBAL_GRAVITY
        self.max_fall = config.MAX_FALL_SPEED
        self.y_vel = 0
        self.grounded = False
        
        self.state = 'idle'
        self.path = []
        self.idx = 0
        self.path_timer = 0
        self.idle_timer = 0.0
        self.attack_timer = 0.0
        self.walk_cd_min = config.ZOMBIE_IDLE_MIN
        self.walk_cd_max = config.ZOMBIE_IDLE_MAX
        self.path_update_rate = config.ZOMBIE_PATH_UPDATE_RATE
        self.attack_range = config.ZOMBIE_ATTACK_RANGE
        self.attack_cooldown = config.ZOMBIE_ATTACK_COOLDOWN
        self.damage = config.ZOMBIE_DAMAGE
   
        target_w, target_h = 1.0, 2.0
        self.visual_scale_relative = (target_w / self.scale_x, target_h / self.scale_y)
        self.visual = Entity(parent=self, scale=self.visual_scale_relative, position=(0, 0, -0.1), double_sided=True)
        self.zombie_graphics = None
        self.skin()

    def skin(self):
        # Load texture aman
        tex = load_texture('Zombie.png') or load_texture('../Assets/Sprite/Zombie.png')
        if tex:
            self.zombie_graphics = SpriteSheetAnimation(tex, parent=self.visual, tileset_size=(8,1), fps=6, animations={'idle':((0,0),(0,0)), 'walk_right':((1,0),(3,0)), 'walk_left':((4,0),(7,0))})
            self.zombie_graphics.play_animation('idle')
            self.current_anim_state = 'idle'

    def get_light_level(self):
        x, y = int(round(self.x)), int(round(self.y))
        if 0 <= x < config.WIDTH and 0 <= y < config.DEPTH:
            if self.world.map_data[x][y] == 0: return self.world.light_map[x][y]
            else: return self.world._light_for_solid(x, y)
        return 0
    
    def apply_lighting(self):
        lvl = max(0, min(14, self.get_light_level()))
        brightness = 0.1 + 0.9 * (lvl / 14.0) 
        if hasattr(self, 'zombie_graphics') and self.zombie_graphics: 
            self.zombie_graphics.color = color.white * brightness

    def safe_destroy(self):
        if hasattr(self, 'zombie_graphics') and self.zombie_graphics:
            if hasattr(self.zombie_graphics, 'sequence') and self.zombie_graphics.sequence:
                try:
                    self.zombie_graphics.sequence.finish()
                    self.zombie_graphics.sequence.kill()
                except:
                    pass
                self.zombie_graphics.sequence = None
            
            # PENTING: Set ke list kosong [], bukan None. 
            # Ursina akan mencoba loop variable ini. Jika None -> Error. Jika [] -> Aman (loop 0 kali).
            if hasattr(self.zombie_graphics, 'animations'):
                self.zombie_graphics.animations = [] 
                  
        try:
            destroy(self)
        except:
            pass

    def update(self):
        dt = time.dt
        if distance(self.position, self.player.position) > config.MOB_DESPAWN_RANGE:
            self.safe_destroy()
            return

        self.apply_lighting()
        self.ai(dt)
        self.move(dt)

    def take_damage(self, amount):
        self.health -= amount
        if hasattr(self, 'zombie_graphics') and self.zombie_graphics:
            self.zombie_graphics.color = color.red
            invoke(setattr, self.zombie_graphics, 'color', color.white, delay=0.2)
        
        dir_to_player = self.x - self.player.x
        if dir_to_player != 0: self.x += (dir_to_player / abs(dir_to_player)) * 0.5
        if self.health <= 0: self.die()

    def die(self):
        self.safe_destroy()

    def attack_player(self):
        self.attack_timer = self.attack_cooldown
        if hasattr(self.player, 'take_damage'): self.player.take_damage(self.damage)

        push_dir = 1 if self.player.x > self.x else -1
        max_push_dist = 0.8
        check_offsets_y = [0.1, 0.9, 1.7] 
        safe_push_dist = max_push_dist
        
        for off_y in check_offsets_y:
            origin = self.player.position + Vec3(0, off_y, 0)
            hit = raycast(origin, Vec3(push_dir, 0, 0), distance=max_push_dist + 0.1, traverse_target=self.world, ignore=(self, self.player, self.player.visual))
            if hit.hit:
                dist_to_wall = hit.distance - 0.2
                if dist_to_wall < 0: dist_to_wall = 0
                if dist_to_wall < safe_push_dist: safe_push_dist = dist_to_wall

        if safe_push_dist > 0.1: self.player.x += push_dir * safe_push_dist
        head_hit = raycast(self.player.position + Vec3(0, 1.8, 0), Vec3(0,1,0), distance=0.5, traverse_target=self.world)
        if not head_hit.hit: self.player.y_velocity = 6; self.player.is_grounded = False

    def ai(self, dt):
        if self.idle_timer > 0: self.idle_timer -= dt
        if self.attack_timer > 0: self.attack_timer -= dt
        self.path_timer += dt
        dist = abs(self.player.x - self.x) + abs(self.player.y - self.y)

        if dist <= self.attack_range:
            self.path = [] 
            if self.attack_timer <= 0: self.attack_player()
            return

        self.state = 'chase' if dist < 10 else 'idle'
        if self.path_timer > self.path_update_rate:
            self.path_timer = 0
            start = (int(round(self.x)), int(round(self.y)))
            if self.state == 'chase':
                tgt = (int(round(self.player.x)), int(round(self.player.y)))
                if self.world.is_standable(tgt[0], tgt[1]):
                    p = astar(self.world, start, tgt)
                    if p: self.path = p; self.idx = 0
            elif self.state == 'idle':
                if self.idx >= len(self.path): self.path = []; self.idx = 0
                if not self.path and self.idle_timer <= 0:
                    rx = start[0] + random.randint(-8, 8)
                    for ry in range(start[1]+2, start[1]-3, -1):
                        if self.world.is_standable(rx, ry):
                            p = bfs(self.world, start, (rx, ry))
                            if p: self.path = p; self.idx = 0; break

    def move(self, dt):
        move_x = 0
        check_limit = 0
        while self.path and self.idx < len(self.path) and check_limit < 3:
            check_limit += 1
            tx, ty = self.path[self.idx]
            if ty > self.y + 0.1 and self.grounded: self.y_vel = self.jump_force
            dx = tx - self.x
            if abs(dx) > 0.15:
                move_x = 1 if dx > 0 else -1
                break 
            else:
                if abs(ty - self.y) < 0.5 or self.y > ty: self.idx += 1
                else: break

        if move_x != 0:
            spd = self.run_speed if self.state == 'chase' else self.walk_speed
            self.x += move_x * spd * dt
            
        if self.zombie_graphics:
            if move_x > 0: 
                if self.current_anim_state != 'walk_right':
                    self.zombie_graphics.play_animation('walk_right')
                    self.current_anim_state = 'walk_right'
                self.visual.scale_x = abs(self.visual_scale_relative[0])
            elif move_x < 0: 
                if self.current_anim_state != 'walk_left':
                    self.zombie_graphics.play_animation('walk_left')
                    self.current_anim_state = 'walk_left'
                self.visual.scale_x = abs(self.visual_scale_relative[0])
            else:
                if self.current_anim_state != 'idle':
                    self.zombie_graphics.play_animation('idle')
                    self.current_anim_state = 'idle'
                self.visual.scale_x = abs(self.visual_scale_relative[0])
        
        hit = raycast(self.position, Vec3(0,-1,0), distance=(self.scale_y/2)+0.1, traverse_target=self.world, ignore=(self,))
        is_ground = (hit.hit and hasattr(hit.entity, 'solid') and hit.entity.solid)
        if is_ground:
            self.grounded = True
            if self.y_vel <= 0: self.y = hit.world_point.y + self.scale_y/2; self.y_vel = 0
        else:
            self.grounded = False
            self.y_vel -= self.gravity * dt
            self.y_vel = max(self.y_vel, -self.max_fall)
        self.y += self.y_vel * dt

# =====================================================
# CHICKEN
# =====================================================
class Chicken(Entity):
    def __init__(self, world, player, **kwargs):
        super().__init__(
            parent=scene,
            model='quad',
            collider='box',
            color=color.clear, 
            origin_y=0,
            position=kwargs.get('position', (0,0)),
            scale=(0.8, 0.8),
            z=config.FG_Z
        )
        self.world = world
        self.player = player
        self.collision = False
        
        self.hp = config.CHICKEN_MAX_HEALTH
        self.walk_speed = config.CHICKEN_WALK_SPEED
        self.run_speed = config.CHICKEN_RUN_SPEED
        self.jump_force = config.CHICKEN_JUMP_FORCE
        self.gravity = config.GLOBAL_GRAVITY
        self.max_fall = config.MAX_FALL_SPEED
        self.y_vel = 0
        self.grounded = False
        
        self.state = 'idle'
        self.path = []
        self.idx = 0
        self.flee_timer = 0
        
        self.flee_duration = config.CHICKEN_FLEE_DURATION
        self.idle_timer = 0.0
        self.walk_cd_min = config.CHICKEN_IDLE_MIN
        self.walk_cd_max = config.CHICKEN_IDLE_MAX
       
        target_w, target_h = 1.0, 1.0 
        self.visual_scale_relative = (target_w / self.scale_x, target_h / self.scale_y)
        
        self.visual = Entity(
            parent=self,
            scale=self.visual_scale_relative,
            position=(0, 0, -0.1),
            double_sided=True
        )
        self.chicken_graphics = None
        self.skin()

    def skin(self):
        tex = load_texture('Ayam.png') or load_texture('../Assets/Sprite/Ayam.png')
        if tex:
            self.chicken_graphics = SpriteSheetAnimation(
                tex, 
                parent=self.visual, 
                tileset_size=(6,1), 
                fps=6, 
                animations={
                    'idle': ((0,0), (0,0)),
                    'walk': ((1,0), (5,0)),
                    'run':  ((1,0), (5,0)),
                },
                double_sided=True
            )
            self.chicken_graphics.play_animation('idle')
            self.current_anim_state = 'idle'

    def safe_destroy(self):
        if hasattr(self, 'chicken_graphics') and self.chicken_graphics:
            if hasattr(self.chicken_graphics, 'sequence') and self.chicken_graphics.sequence:
                try:
                    self.chicken_graphics.sequence.finish() 
                    self.chicken_graphics.sequence.kill()
                except:
                    pass
                self.chicken_graphics.sequence = None
            
            if hasattr(self.chicken_graphics, 'animations'):
                self.chicken_graphics.animations = [] 
        
        try:
            destroy(self)
        except:
            pass

    def update(self):
        dt = time.dt
        if distance(self.position, self.player.position) > config.MOB_DESPAWN_RANGE:
            self.safe_destroy()
            return
        self.ai(dt)
        self.move(dt)

    def ai(self, dt):
        if self.idle_timer > 0: self.idle_timer -= dt
        if self.flee_timer > 0: self.flee_timer -= dt
        if self.path and self.idx >= len(self.path): self.path = []; self.idx = 0
        if self.state == 'flee':
            if self.flee_timer <= 0:
                self.state = 'idle'
                self.idle_timer = random.uniform(self.walk_cd_min, self.walk_cd_max)
            elif not self.path: self.run_away()
        elif self.state == 'idle':
            if not self.path and self.idle_timer <= 0: self.random_walk()
        elif self.state == 'walk':
            if not self.path:
                self.state = 'idle'
                self.idle_timer = random.uniform(self.walk_cd_min, self.walk_cd_max)

    def take_damage(self, dmg):
        self.hp -= dmg
        if hasattr(self, 'chicken_graphics') and self.chicken_graphics:
            self.chicken_graphics.color = color.red
            invoke(setattr, self.chicken_graphics, 'color', color.white, delay=0.2)

        if self.hp <= 0: self.die(); return
        self.state = 'flee'
        self.flee_timer = self.flee_duration
        self.path = []; self.idx = 0
        self.run_away()

    def die(self):
        if hasattr(self.player, 'inventory_system'):
            self.player.inventory_system.add_item(config.RAW_CHICKEN)
            self.player.inventory_system.add_item(config.FEATHER)
        self.safe_destroy()

    def random_walk(self):
        start = (int(round(self.x)), int(round(self.y)))
        for _ in range(6):
            rx = start[0] + random.randint(-6, 6)
            for ry in range(start[1]+2, start[1]-3, -1):
                if self.world.is_standable(rx, ry):
                    p = bfs(self.world, start, (rx, ry))
                    if p: self.path = p; self.idx = 0; self.state = 'walk'; return
        step = random.choice([-1,1])
        if self.world.is_standable(start[0]+step, start[1]):
            self.path = [(start[0]+step, start[1])]; self.idx = 0; self.state = 'walk'

    def run_away(self):
        start = (int(round(self.x)), int(round(self.y)))
        primary_dir = 1 if self.player.x < self.x else -1
        directions_to_try = [primary_dir, -primary_dir]
        
        max_dist = config.CHICKEN_FLEE_DISTANCE 
        min_dist = 2 
        
        for try_dir in directions_to_try:
            for dist in range(max_dist, min_dist - 1, -1):
                target_x = int(round(self.x + (try_dir * dist)))
                if not (0 <= target_x < config.WIDTH): continue
                start_y_scan = int(round(self.y)) + 8  
                end_y_scan = int(round(self.y)) - 8
                for ty in range(start_y_scan, end_y_scan, -1):
                    if not (0 <= ty < config.DEPTH): continue
                    if self.world.is_standable(target_x, ty):
                        path = bfs(self.world, start, (target_x, ty))
                        if path:
                            self.path = path; self.idx = 0
                            return
        self.random_walk()

    def move(self, dt):
        move_x = 0
        if self.path and self.idx < len(self.path):
            tx, ty = self.path[self.idx]
            if ty > self.y + 0.1 and self.grounded: self.y_vel = self.jump_force
            dx = tx - self.x
            if abs(dx) > 0.15: move_x = 1 if dx > 0 else -1
            else: self.idx += 1
        else: self.path = []; self.idx = 0
        
        if move_x != 0:
            spd = self.run_speed if self.state == 'flee' else self.walk_speed
            self.x += move_x * spd * dt
        
        anim_to_play = 'run' if self.state == 'flee' else 'walk'
        if self.chicken_graphics:
            if move_x > 0: 
                if self.current_anim_state != anim_to_play:
                    self.chicken_graphics.play_animation(anim_to_play)
                    self.current_anim_state = anim_to_play
                self.visual.scale_x = abs(self.visual_scale_relative[0])
            elif move_x < 0: 
                if self.current_anim_state != anim_to_play:
                    self.chicken_graphics.play_animation(anim_to_play)
                    self.current_anim_state = anim_to_play
                self.visual.scale_x = -abs(self.visual_scale_relative[0]) 
            else:
                if self.current_anim_state != 'idle':
                    self.chicken_graphics.play_animation('idle')
                    self.current_anim_state = 'idle'
                self.visual.scale_x = abs(self.visual_scale_relative[0])

        hit = raycast(self.position, Vec3(0,-1,0), distance=(self.scale_y/2)+0.1, traverse_target=self.world, ignore=(self,))
        is_ground = (hit.hit and hasattr(hit.entity, 'solid') and hit.entity.solid)
        if is_ground:
            self.grounded = True
            if self.y_vel <= 0: self.y = hit.world_point.y + self.scale_y/2; self.y_vel = 0
        else:
            self.grounded = False
            self.y_vel -= self.gravity * dt
            self.y_vel = max(self.y_vel, -self.max_fall)
        self.y += self.y_vel * dt

class ZombieSpawner:
    def __init__(self, world, player):
        self.world = world; self.player = player; self.timer = 0
        self.spawn_rate = config.ZOMBIE_SPAWN_RATE
    def update(self):
        self.spawn_rate = config.ZOMBIE_SPAWN_RATE
        self.timer += time.dt
        if self.timer >= self.spawn_rate: self.timer = 0; self.spawn()
    def spawn(self):
        if len([e for e in scene.entities if isinstance(e, Zombie)]) > 10: return
        px, py = int(round(self.player.x)), int(round(self.player.y))
        for _ in range(30):
            dx = random.randint(-12,12); dy = random.randint(-6,6)
            if abs(dx) < 6: continue
            x, y = px+dx, py+dy
            if not (0<=x<config.WIDTH and 0<=y<config.DEPTH): continue
            if self.world.light_map[x][y] > 4: continue
            if self.world.is_standable(x, y): Zombie(self.world, self.player, position=(x,y)); return

class ChickenSpawner:
    def __init__(self, world, player):
        self.world = world; self.player = player; self.timer = 0
        self.spawn_rate = config.CHICKEN_SPAWN_RATE
    def update(self):
        self.spawn_rate = config.CHICKEN_SPAWN_RATE
        self.timer += time.dt
        if self.timer >= self.spawn_rate: self.timer = 0; self.spawn()
    def spawn(self):
        if len([e for e in scene.entities if isinstance(e, Chicken)]) > 5: return
        px, py = int(round(self.player.x)), int(round(self.player.y))
        for _ in range(20):
            dx = random.randint(-20,20); dy = random.randint(-6,6)
            if abs(dx) < 5: continue
            x, y = px+dx, py+dy
            if not (0<=x<config.WIDTH and 0<=y<config.DEPTH): continue
            if self.world.light_map[x][y] <= 11: continue
            if self.world.is_standable(x, y): Chicken(self.world, self.player, position=(x,y)); return