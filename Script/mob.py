from ursina import *
from config import * # Mengambil MOB_DESPAWN_RANGE dari sini
import heapq
from collections import deque
import random
import time

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_neighbors(world, pos):
    x, y = pos
    res = []
    for dx, dy in [(1,0), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < WIDTH and 0 <= ny < DEPTH):
            continue
        # GUNAKAN 'world' YANG DIPASSING SEBAGAI ARGUMEN
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
            collider='box',
            z=FG_Z
        )
        self.world = world
        self.player = player
        
        # Stats
        self.scale = (0.9, 1.8) 
        self.max_health = ZOMBIE_MAX_HEALTH
        self.health = self.max_health
        self.walk_speed = ZOMBIE_WALK_SPEED
        self.run_speed = ZOMBIE_RUN_SPEED
        self.jump_force = ZOMBIE_JUMP_FORCE
        self.gravity = GLOBAL_GRAVITY
        self.max_fall = MAX_FALL_SPEED
        self.y_vel = 0
        self.grounded = False

        # AI
        self.state = 'idle'
        self.path = []
        self.idx = 0
        self.path_timer = 0
        self.idle_timer = 0.0
        self.attack_timer = 0.0
        self.walk_cd_min = ZOMBIE_IDLE_MIN
        self.walk_cd_max = ZOMBIE_IDLE_MAX
        self.path_update_rate = ZOMBIE_PATH_UPDATE_RATE
        self.attack_range = ZOMBIE_ATTACK_RANGE
        self.attack_cooldown = ZOMBIE_ATTACK_COOLDOWN
        self.damage = ZOMBIE_DAMAGE

        # Visual
        target_w, target_h = 1.0, 2.0
        self.visual_scale_relative = (target_w / self.scale_x, target_h / self.scale_y)
        self.visual = Entity(parent=self, scale=self.visual_scale_relative, position=(0, 0, -0.1), double_sided=True)
        self.skin()
        print(f"[SPAWN] Zombie at {self.position}")

    def skin(self):
        self.zombie_graphics = SpriteSheetAnimation('../Assets/Sprite/Zombie.png', parent=self.visual, tileset_size=(7,1), fps=6, animations={'idle':((0,0),(0,0)), 'walk_right':((1,0),(3,0)), 'walk_left':((4,0),(6,0))})
        self.zombie_graphics.play_animation('idle')
        self.current_anim_state = 'idle'

    def get_light_level(self):
        x, y = int(round(self.x)), int(round(self.y))
        if 0 <= x < WIDTH and 0 <= y < DEPTH:
            if self.world.map_data[x][y] == 0: return self.world.light_map[x][y]
            else: return self.world._light_for_solid(x, y)
        return 0
    
    def apply_lighting(self):
        lvl = max(0, min(14, self.get_light_level()))
        brightness = 0.1 + 0.9 * (lvl / 14.0) 
        if hasattr(self, 'zombie_graphics'): self.zombie_graphics.color = color.white * brightness

    def update(self):
        dt = time.dt
        
        # --- DESPAWN LOGIC (MENGGUNAKAN CONFIG) ---
        if distance(self.position, self.player.position) > MOB_DESPAWN_RANGE:
            destroy(self)
            return

        self.apply_lighting()
        self.ai(dt)
        self.move(dt)

    def take_damage(self, amount):
        self.health -= amount
        if hasattr(self, 'zombie_graphics'):
            self.zombie_graphics.color = color.red
            invoke(setattr, self.zombie_graphics, 'color', color.white, delay=0.2)
        
        print(f"[ZOMBIE] Hit! HP: {self.health}")
        dir_to_player = self.x - self.player.x
        if dir_to_player != 0: self.x += (dir_to_player / abs(dir_to_player)) * 0.5
        if self.health <= 0: self.die()

    def die(self):
        print("[ZOMBIE] Died")
        destroy(self)

    def attack_player(self):
        self.attack_timer = self.attack_cooldown
        print(f"[ZOMBIE] Attacking Player for {self.damage} dmg!")
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
            start = (round(self.x), round(self.y))
            if self.state == 'chase':
                tgt = (round(self.player.x), round(self.player.y))
                # FIX: Gunakan self.world
                if self.world.is_standable(tgt[0], tgt[1]):
                    p = astar(self.world, start, tgt)
                    if p: self.path = p; self.idx = 0
            elif self.state == 'idle':
                if self.idx >= len(self.path): self.path = []; self.idx = 0
                if not self.path and self.idle_timer <= 0:
                    rx = start[0] + random.randint(-8, 8)
                    for ry in range(start[1]+2, start[1]-3, -1):
                        # FIX: Gunakan self.world
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
        
        # VISUAL LOGIC
        if move_x > 0: # KANAN
            if self.current_anim_state != 'walk_right':
                self.zombie_graphics.play_animation('walk_right')
                self.current_anim_state = 'walk_right'
            self.visual.scale_x = abs(self.visual_scale_relative[0])
            
        elif move_x < 0: # KIRI
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
            color=color.red,
            origin_y=0,
            position=kwargs.get('position', (0,0)),
            scale=(0.8, 0.8),
            z=FG_Z
        )

        self.world = world
        self.player = player
        self.hp = CHICKEN_MAX_HEALTH
        self.walk_speed = CHICKEN_WALK_SPEED
        self.run_speed = CHICKEN_RUN_SPEED
        self.jump_force = CHICKEN_JUMP_FORCE
        self.gravity = GLOBAL_GRAVITY
        self.max_fall = MAX_FALL_SPEED
        self.y_vel = 0
        self.grounded = False
        self.state = 'idle'
        self.path = []
        self.idx = 0
        self.flee_timer = 0
        self.flee_duration = CHICKEN_FLEE_DURATION
        self.idle_timer = 0.0
        self.walk_cd_min = CHICKEN_IDLE_MIN
        self.walk_cd_max = CHICKEN_IDLE_MAX
            # Visual
        self.visual = Entity(
            parent=self, 
            scale=(0.8, 0.8), 
            position=(0, 0, 0), 
            double_sided=True)
        self.skin()
        print(f"[SPAWN] Chicken at {self.position}")

    def skin(self):
        self.chicken_graphics = SpriteSheetAnimation('../Assets/Sprite/Ayam.png', parent=self.visual, tileset_size=(6,1), fps=6, animations={
            'idle':((0,0),(0,0)), 
            'walk_right':((3,0),(5,0)), 
            'walk_left':((0,0),(2,0)),})
        self.chicken_graphics.play_animation('idle')
        self.current_anim_state = 'idle'

    def update(self):
        dt = time.dt
        
        # --- DESPAWN LOGIC (MENGGUNAKAN CONFIG) ---
        if distance(self.position, self.player.position) > MOB_DESPAWN_RANGE:
            if hasattr(self, 'chicken_graphics'):
                self.chicken_graphics.animations = []
                destroy(self)
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
        self.blink(color.red, duration=0.2)
        print(f"[CHICKEN] Ouch! HP: {self.hp}")
        if self.hp <= 0: destroy(self); return
        self.state = 'flee'
        self.flee_timer = self.flee_duration
        self.path = []; self.idx = 0
        self.run_away()

    def random_walk(self):
        start = (round(self.x), round(self.y))
        for _ in range(6):
            rx = start[0] + random.randint(-6, 6)
            for ry in range(start[1]+2, start[1]-3, -1):
                # FIX: Gunakan self.world
                if self.world.is_standable(rx, ry):
                    p = bfs(self.world, start, (rx, ry))
                    if p: self.path = p; self.idx = 0; self.state = 'walk'; return
        step = random.choice([-1,1])
        # FIX: Gunakan self.world
        if self.world.is_standable(start[0]+step, start[1]):
            self.path = [(start[0]+step, start[1])]; self.idx = 0; self.state = 'walk'

    def run_away(self):
        start = (round(self.x), round(self.y))
        
        primary_dir = 1 if self.player.x < self.x else -1
        directions_to_try = [primary_dir, -primary_dir]
        
        max_dist = CHICKEN_FLEE_DISTANCE
        min_dist = 2 
        
        for try_dir in directions_to_try:
            for dist in range(max_dist, min_dist - 1, -1):
                target_x = round(self.x + (try_dir * dist))
                
                if not (0 <= target_x < WIDTH): continue
                
                start_y_scan = round(self.y) + 8  
                end_y_scan = round(self.y) - 8
                
                for ty in range(start_y_scan, end_y_scan, -1):
                    if not (0 <= ty < DEPTH): continue
                    
                    # FIX: Gunakan self.world
                    if self.world.is_standable(target_x, ty):
                        path = bfs(self.world, start, (target_x, ty))
                        if path:
                            self.path = path
                            self.idx = 0
                            print(f"[CHICKEN] Fleeing to ({target_x}, {ty})")
                            return
                        
        print("[CHICKEN] Cornered! Panic random walk.")
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

        if move_x > 0: # KANAN
            if self.current_anim_state != 'walk_right':
                self.chicken_graphics.play_animation('walk_right')
                self.current_anim_state = 'walk_right'
            self.visual.scale_x = abs(0.8)
            
        elif move_x < 0: # KIRI
            if self.current_anim_state != 'walk_left':
                self.chicken_graphics.play_animation('walk_left')
                self.current_anim_state = 'walk_left'
            self.visual.scale_x = abs(0.8)
            
        else:
            if self.current_anim_state != 'idle':
                self.chicken_graphics.play_animation('idle')
                self.current_anim_state = 'idle'
            self.visual.scale_x = abs(0.8)
        
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
# SPAWNERS
# =====================================================
class ZombieSpawner:
    def __init__(self, world, player):
        self.world = world; self.player = player; self.timer = 0; self.spawn_rate = ZOMBIE_SPAWN_RATE
    def update(self):
        self.timer += time.dt
        if self.timer >= self.spawn_rate: self.timer = 0; self.spawn()
    def spawn(self):
        px, py = round(self.player.x), round(self.player.y)
        for _ in range(30):
            dx = random.randint(-12,12); dy = random.randint(-6,6)
            if abs(dx) < 6: continue
            x, y = px+dx, py+dy
            if not (0<=x<WIDTH and 0<=y<DEPTH): continue
            if self.world.light_map[x][y] > 4: continue
            # FIX: Gunakan self.world.is_standable
            if self.world.is_standable(x, y): Zombie(self.world, self.player, position=(x,y)); return

class ChickenSpawner:
    def __init__(self, world, player):
        self.world = world; self.player = player; self.timer = 0; self.spawn_rate = CHICKEN_SPAWN_RATE
    def update(self):
        self.timer += time.dt
        if self.timer >= self.spawn_rate: self.timer = 0; self.spawn()
    def spawn(self):
        px, py = round(self.player.x), round(self.player.y)
        for _ in range(20):
            dx = random.randint(-20,20); dy = random.randint(-6,6)
            if abs(dx) < 5: continue
            x, y = px+dx, py+dy
            if not (0<=x<WIDTH and 0<=y<DEPTH): continue
            if self.world.light_map[x][y] <= 11: continue
            # FIX: Gunakan self.world.is_standable
            if self.world.is_standable(x, y): Chicken(self.world, self.player, position=(x,y)); return