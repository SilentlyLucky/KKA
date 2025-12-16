from ursina import *
from config import *
import heapq
from collections import deque
import random
import time

class Zombie(Entity):
    def __init__(self, world, player, **kwargs):
        super().__init__(
            parent=scene,
            origin_y=0,        # Pivot di tengah badan
            position=kwargs.get('position', (0,0)),
            z=FG_Z
        )

        self.world = world
        self.player = player

        # ==========================================
        # 1. PARAMETER DINAMIS (0.9 x 1.8)
        # ==========================================
        
        # --- FISIK (Hitbox) ---
        self.collider = 'box'
        self.scale = (0.9, 1.8) 
        
        # --- VISUAL (Tampilan 1.0 x 2.0) ---
        target_w, target_h = 1.0, 2.0
        # Hitung skala relatif: Target / Fisik
        self.visual_scale_relative = (target_w / self.scale_x, target_h / self.scale_y)
        
        self.visual = Entity(
            parent=self,
            scale=self.visual_scale_relative, 
            position=(0, 0, -0.1),
            double_sided=True 
        )

        # --- STATS ---
        self.chase_speed = 3.5         
        self.idle_speed = 1.5          
        self.jump_force = 12           # Kuat untuk badan tinggi
        self.gravity_force = 30 
        self.max_fall_speed = 20
        
        # --- AI SETTINGS ---
        self.vision_range = 8          
        self.vertical_vision = 4       
        self.give_up_range = 15        
        self.wander_radius = 10        
        self.path_update_rate = 0.20   
        self.frustration_duration = 3.0 
        self.max_search_steps = 400    # Batas langkah A* (Python)
        self.idle_wait_duration = 5.0   

        # --- STATE ---
        self.state = 'idle'
        self.path = []      
        self.current_path_index = 0     
        self.path_timer = 0
        self.frustration_timer = 0     
        self.idle_wait_timer = 0        
        self.last_attack_time = 0
        
        # Physics Vars
        self.y_velocity = 0
        self.is_grounded = False

        self.skin()

    def skin(self):
        self.zombie_graphics = SpriteSheetAnimation('../Assets/Sprite/Zombie.png', parent=self.visual, tileset_size=(8,1), fps=6, animations={
            'idle' : ((0,0), (0,0)),        # makes an animation from (0,0) to (0,0), a single frame
            'walk_right' : ((1,0), (3,0)),
            'walk_left' : ((4,0), (7,0)),
            }
            )
        self.zombie_graphics.play_animation('idle')
        self.current_anim_state = 'idle'

    def update(self):
        try:
            dt = time.dt
            
            # ----------------------------------
            # 1. LOGIKA UTAMA
            # ----------------------------------
            self.attack_logic()
            
            if self.frustration_timer > 0: self.frustration_timer -= dt
            if self.idle_wait_timer > 0: self.idle_wait_timer -= dt 

            # Respawn jika jatuh ke void
            if self.y < -20:
                self.position = (self.player.x, self.player.y + 10)
                self.y_velocity = 0
                self.path = []

            """ # ----------------------------------
            # 2. VISUAL UPDATE
            # ----------------------------------
            if self.state == 'chase': self.visual.color = color.red
            else: self.visual.color = color.violet 

            # Flip Visual
            if self.path and self.current_path_index < len(self.path):
                next_node = self.path[self.current_path_index]
                base_scale = self.visual_scale_relative[0]
                if next_node[0] > self.x: self.visual.scale_x = base_scale
                elif next_node[0] < self.x: self.visual.scale_x = -base_scale """

            # ----------------------------------
            # 3. AI DECISION MAKING
            # ----------------------------------
            manhattan_dist = abs(self.player.x - self.x) + abs(self.player.y - self.y)
            can_see = self.check_vision()
            
            # Prioritas 1: Lihat Player -> Chase
            if can_see and self.frustration_timer <= 0:
                self.state = 'chase'
                self.idle_wait_timer = 0
            
            # Prioritas 2: Player Hilang TAPI Path Masih Ada -> Lanjutkan (Persistence)
            elif self.state == 'chase' and self.path and self.current_path_index < len(self.path):
                self.state = 'chase'
            
            # Prioritas 3: Idle
            else:
                self.state = 'idle'
            
            # ----------------------------------
            # 4. PATHFINDING MANAGER
            # ----------------------------------
            self.path_timer += dt
            if self.path_timer > self.path_update_rate:
                self.path_timer = 0
                start_pos = (int(round(self.x)), int(round(self.y)))
                
                if self.is_grounded:
                    # KASUS CHASE
                    if self.state == 'chase':
                        if can_see:
                            if manhattan_dist < (self.give_up_range + 10): 
                                target_pos = self.find_valid_target(self.player.x, self.player.y)
                                if target_pos and start_pos != target_pos:
                                    found_path = self.astar(start_pos, target_pos)
                                    if found_path: 
                                        self.path = found_path
                                        self.current_path_index = 0 # Reset Path Index
                                    else:
                                        self.path = []
                                        self.state = 'idle'
                                        self.frustration_timer = self.frustration_duration
                        else:
                            pass # Lanjutkan sisa path lama

                    # KASUS IDLE / WANDER
                    elif self.state == 'idle' and (not self.path or self.current_path_index >= len(self.path)):
                        if self.idle_wait_timer <= 0:
                            radius = self.wander_radius
                            path_found = False
                            for _ in range(10): 
                                rx = start_pos[0] + random.randint(-radius, radius)
                                for ry in range(start_pos[1] + 2, start_pos[1] - 4, -1):
                                    if self.is_standable(rx, ry):
                                        new_path = self.bfs(start_pos, (rx, ry))
                                        if new_path:
                                            self.path = new_path
                                            self.current_path_index = 0
                                            path_found = True
                                        break
                                if path_found: break
                            if not path_found: self.idle_wait_timer = self.idle_wait_duration

            # ====================================================
            # 5. EKSEKUSI GERAKAN (PHYSICS)
            # ====================================================
            
            move_dir_x = 0
            is_jumping = False
            
            # A. Tentukan Arah Berdasarkan Path Node
            if self.path and self.current_path_index < len(self.path):
                next_step = self.path[self.current_path_index]
                
                # Logic Lompat
                if next_step[1] > self.y + 0.1:
                    is_jumping = True
                    if self.is_grounded: self.y_velocity = self.jump_force
                
                diff_x = next_step[0] - self.x
                
                # Toleransi agar tidak bergetar (0.15)
                if abs(diff_x) > 0.15: 
                    move_dir_x = 1 if diff_x > 0 else -1
                else:
                    # Cek apakah Y juga sudah sampai / sudah terlewati
                    if abs(next_step[1] - self.y) < 0.5 or self.y > next_step[1]:
                        self.current_path_index += 1 
            
            # Jika Path Habis
            elif self.path and self.current_path_index >= len(self.path):
                if self.state == 'idle':
                    self.idle_wait_timer = self.idle_wait_duration
                self.path = [] # Clear path

            # ----------------------------------
            # 5.1. ANIMATION CONTROL (NEW LOGIC)
            # ----------------------------------
            if move_dir_x > 0:
                # Moving Right
                if self.current_anim_state != 'walk_right':
                    self.zombie_graphics.play_animation('walk_right')
                    self.current_anim_state = 'walk_right'
                # Ensure visual scale is positive (facing right)
                self.visual.scale_x = abs(self.visual_scale_relative[0])
                
            elif move_dir_x < 0:
                # Moving Left
                if self.current_anim_state != 'walk_left':
                    self.zombie_graphics.play_animation('walk_left')
                    self.current_anim_state = 'walk_left'
                # Ensure visual scale is negative (facing left)
                self.visual.scale_x = abs(self.visual_scale_relative[0])
                
            else:
                # Not moving horizontally (Standing/Jumping up)
                if self.current_anim_state != 'idle':
                    self.zombie_graphics.play_animation('idle')
                    self.current_anim_state = 'idle'
            
            # B. Raycast Movement (Horizontal)
            if move_dir_x != 0:
                hit_wall = False
                dist_x = (self.scale_x / 2) + 0.1
                
                # Cek 3 titik (Bawah, Tengah, Atas)
                offsets_y = [-0.8, 0, 0.8] 
                
                for off_y in offsets_y:
                    # FIX: Abaikan kaki saat lompat biar bisa naik
                    if is_jumping and off_y < 0.5: continue 
                    
                    origin = self.position + Vec3(0, off_y, 0)
                    hit = raycast(origin, Vec3(move_dir_x, 0, 0), distance=dist_x, ignore=(self, self.visual), debug=False)
                    if hit.hit:
                        hit_wall = True
                        break
                
                if not hit_wall:
                    current_speed = self.chase_speed if self.state == 'chase' else self.idle_speed
                    self.x += move_dir_x * current_speed * dt

            # C. Gerak Vertikal & Gravitasi
            ray_origin_y = 0 
            ray_direction = Vec3(0, -1, 0)
            ray_dist = (self.scale_y / 2) + 0.1 
            margin_x = 0.05
            half_w = (self.scale_x / 2) - margin_x
            
            pos_left = self.position + Vec3(-half_w, ray_origin_y, 0)
            pos_right = self.position + Vec3(half_w, ray_origin_y, 0)
            
            hit_l = raycast(pos_left, ray_direction, distance=ray_dist, ignore=(self, self.visual))
            hit_r = raycast(pos_right, ray_direction, distance=ray_dist, ignore=(self, self.visual))
            
            if hit_l.hit or hit_r.hit:
                self.is_grounded = True
                
                # Logic Snap to Ground
                floor_y = -9999
                if hit_l.hit: floor_y = max(floor_y, hit_l.world_point.y)
                if hit_r.hit: floor_y = max(floor_y, hit_r.world_point.y)
                target_y = floor_y + (self.scale_y / 2)
                
                if self.y_velocity <= 0:
                    self.y = target_y
                    self.y_velocity = 0
            else:
                self.is_grounded = False
                self.y_velocity -= self.gravity_force * dt
                if self.y_velocity < -self.max_fall_speed: self.y_velocity = -self.max_fall_speed
            
            # Cek Kepala (Atap)
            if self.y_velocity > 0:
                head_origin = self.position + Vec3(0, self.scale_y/2 - 0.1, 0)
                hit_head = raycast(head_origin, Vec3(0,1,0), distance=0.2, ignore=(self, self.visual))
                if hit_head.hit: self.y_velocity = 0

            self.y += self.y_velocity * dt

        except Exception as e:
            self.path = []

    # ==========================================
    # HELPER METHODS (PURE PYTHON)
    # ==========================================

    def attack_logic(self):
        diff_x = abs(self.player.x - self.x)
        diff_y = abs(self.player.y - self.y)
        # Range attack 8 arah
        if diff_x < 1.6 and diff_y < 1.9: 
            import time as t_module
            current_time = t_module.time()
            if current_time - self.last_attack_time > ZOMBIE_ATTACK_COOLDOWN:
                self.last_attack_time = current_time
                self.player.take_damage(ZOMBIE_DAMAGE)
                
                direction = 1 if self.player.x > self.x else -1
                wall_behind = raycast(self.player.position, Vec3(direction,0,0), distance=1.0, ignore=(self, self.visual, self.player))
                
                if not wall_behind.hit: 
                    self.player.x += direction * 0.5
                self.player.y += 0.5

    def find_valid_target(self, px, py):
        tx, ty = int(round(px)), int(round(py))
        if self.is_standable(tx, ty): return (tx, ty)
        if self.is_standable(tx, ty-1): return (tx, ty-1)
        return None

    def check_vision(self):
        dist = distance(self.position, self.player.position)
        if dist > self.vision_range: return False 
        if abs(self.player.y - self.y) > self.vertical_vision: return False
        
        eye_pos = self.position + Vec3(0, 0.6, 0)
        target_eye = self.player.position + Vec3(0, 0.6, 0)
        direction = (target_eye - eye_pos).normalized()
        hit = raycast(eye_pos, direction, distance=self.vision_range, ignore=(self, self.visual), debug=False)
        if hit.hit:
            if distance(hit.world_point, target_eye) < 1.5: return True
            return False
        return True
    
    # --- PATHFINDING PYTHON STANDARD ---
    def is_standable(self, x, y):
        # Cek Kaki, Kepala, dan Lantai
        return ((x, y) not in self.world.block_positions) and \
               ((x, y+1) not in self.world.block_positions) and \
               ((x, y-1) in self.world.block_positions)

    def get_neighbors(self, pos):
        x, y = pos; moves = []
        for dx, dy in [(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nx, ny = x+dx, y+dy
            if not (0<=nx<WIDTH and 0<=ny<DEPTH): continue
            
            if (nx,ny) in self.world.block_positions: continue
            if (nx,ny+1) in self.world.block_positions: continue
            
            has_floor = (nx,ny-1) in self.world.block_positions
            if dy<=0 and not has_floor: continue
            if dy==1 and (x,y+2) in self.world.block_positions: continue
            
            moves.append((nx,ny))
        return moves

    def heuristic(self, a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def reconstruct_path(self, cf, cur):
        p = [cur]; 
        while cur in cf: cur = cf[cur]; p.insert(0, cur)
        return p[1:]
    
    def astar(self, start, goal):
        open_set = []; heapq.heappush(open_set, (0, start)); came_from = {}; g_score = {start:0}; f_score = {start:self.heuristic(start, goal)}; steps=0
        while open_set:
            steps+=1; 
            if steps>self.max_search_steps: return []
            current = heapq.heappop(open_set)[1]
            if current == goal: return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current):
                tg = g_score[current]+1
                if neighbor not in g_score or tg < g_score[neighbor]: came_from[neighbor]=current; g_score[neighbor]=tg; f_score[neighbor]=tg+self.heuristic(neighbor, goal); heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []
        
    def bfs(self, start, goal):
        q=deque([(start,[start])]); v=set([start]); steps=0
        while q:
            steps+=1; 
            if steps>self.max_search_steps: return []
            (curr, p) = q.popleft()
            if curr==goal: return p[1:]
            for n in self.get_neighbors(curr):
                if n not in v: v.add(n); q.append((n, p+[n]))
        return []
