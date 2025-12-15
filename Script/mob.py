from ursina import *
from config import *
import heapq
from collections import deque
import random
import time

class Zombie(Entity):
    def __init__(self, world, player, **kwargs):
        # ==========================================
        # 1. PARAMETER DINAMIS (SIZE 1x2)
        # ==========================================
        
        # --- Dimensi Fisik (Collider) ---
        # Lebar 0.8, Tinggi 1.8 (Standar 2 Blok)
        self.collider_width = 0.8
        self.collider_height = 1.8 
        
        # --- Dimensi Visual (Gambar) ---
        # Kompensasi visual agar pas
        self.visual_scale = (1.25, 1.11) 
        
        super().__init__(
            parent=scene,
            position=kwargs.get('position', (0,0)),
            scale=(self.collider_width, self.collider_height),
            collider='box',
            model=None,
            color=color.clear,
            z=FG_Z
        )

        self.world = world
        self.player = player

        # --- Visual ---
        self.visual = Entity(
            parent=self,
            model='quad',
            color=color.violet, 
            scale=self.visual_scale,
            position=(0, 0, -0.1),
            double_sided=True 
        )

        # --- Stats Fisik & Speed ---
        self.chase_speed = 3.5         
        self.idle_speed = 1.5          
        self.jump_force = 9.0          # Lompatan sedikit lebih kuat untuk badan berat
        self.gravity_force = 25
        
        # --- AI Behavior Settings ---
        self.vision_range = 8          
        self.vertical_vision = 4       # Vision vertikal lebih luas karena badan tinggi
        self.give_up_range = 15        
        self.wander_radius = 10        
        self.path_update_rate = 0.20   
        self.frustration_duration = 3.0 
        self.max_search_steps = 400
        self.idle_wait_duration = 5.0   

        # --- Internal State ---
        self.state = 'idle'
        self.path = []      
        self.path_timer = 0
        self.frustration_timer = 0     
        self.idle_wait_timer = 0        
        self.last_attack_time = 0
        self.y_velocity = 0
        self.is_grounded = False

    def update(self):
        try:
            dt = time.dt
            
            # 1. LOGIKA UTAMA
            self.attack_logic()
            
            if self.frustration_timer > 0: self.frustration_timer -= dt
            if self.idle_wait_timer > 0: self.idle_wait_timer -= dt 

            if self.y < -20:
                self.position = (self.player.x, self.player.y + 10)
                self.y_velocity = 0
                self.path = []

            # 2. VISUAL UPDATE
            if self.state == 'chase': self.visual.color = color.red
            else: self.visual.color = color.violet 

            if self.path:
                next_node = self.path[0]
                target_scale_x = abs(self.visual_scale[0])
                if next_node[0] > self.x: self.visual.scale_x = target_scale_x
                elif next_node[0] < self.x: self.visual.scale_x = -target_scale_x

            # 3. AI DECISION MAKING (PERSISTENCE)
            manhattan_dist = abs(self.player.x - self.x) + abs(self.player.y - self.y)
            can_see = self.check_vision()
            
            # Prioritas 1: Lihat Player -> KEJAR
            if can_see and self.frustration_timer <= 0:
                self.state = 'chase'
                self.idle_wait_timer = 0 
            
            # Prioritas 2: Player Hilang/Jauh TAPI Path Masih Ada -> SELESAIKAN JALAN
            elif self.state == 'chase' and len(self.path) > 0:
                self.state = 'chase'
                
            # Prioritas 3: Sisanya -> IDLE
            else:
                self.state = 'idle'
            
            # 4. PATHFINDING MANAGER
            self.path_timer += dt
            if self.path_timer > self.path_update_rate:
                self.path_timer = 0
                start_pos = (int(round(self.x)), int(round(self.y)))
                
                if self.is_grounded:
                    # --- KASUS: MENGEJAR PLAYER ---
                    if self.state == 'chase':
                        if manhattan_dist < (self.give_up_range + 10): 
                            target_pos = self.find_valid_target(self.player.x, self.player.y)
                            if target_pos and start_pos != target_pos:
                                found_path = self.astar(start_pos, target_pos)
                                if found_path: self.path = found_path
                                else:
                                    self.path = []
                                    self.state = 'idle'
                                    self.frustration_timer = self.frustration_duration
                        else:
                            pass

                    # --- KASUS: IDLE / WANDERING ---
                    elif self.state == 'idle' and not self.path:
                        
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
                                            path_found = True
                                        break
                                if path_found: break
                            
                            if not path_found:
                                self.idle_wait_timer = self.idle_wait_duration

            # 5. EKSEKUSI GERAKAN
            if self.path:
                next_step = self.path[0]
                
                is_jumping = next_step[1] > self.y + 0.1
                if is_jumping and self.is_grounded:
                    self.y_velocity = self.jump_force
                
                move_dir_x = next_step[0] - self.x
                dir_x = 0
                should_move_x = False
                
                if abs(move_dir_x) > 0.1:
                    dir_x = 1 if move_dir_x > 0 else -1
                    should_move_x = True
                    
                    sensor_dist = (self.collider_width / 2) + 0.1
                    wall_check = raycast(self.position, Vec3(dir_x, 0, 0), distance=sensor_dist, ignore=(self, self.visual), debug=False)
                    
                    if wall_check.hit:
                        if is_jumping: pass 
                        else: should_move_x = False
                
                if should_move_x:
                    current_speed = self.chase_speed if self.state == 'chase' else self.idle_speed
                    self.x += dir_x * current_speed * dt
                
                dist_sq = (self.x - next_step[0])**2 + (self.y - next_step[1])**2
                if dist_sq < 0.4:
                    self.path.pop(0)
                    if not self.path and self.state == 'idle':
                        self.idle_wait_timer = self.idle_wait_duration

            # 6. GRAVITASI
            self.apply_gravity_robust()

        except Exception as e:
            self.path = []

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def attack_logic(self):
        dist = distance(self.position, self.player.position)
        # Jarak serang disesuaikan
        if dist < (ZOMBIE_ATTACK_RANGE + 0.3): 
            import time as t_module
            current_time = t_module.time()
            if current_time - self.last_attack_time > ZOMBIE_ATTACK_COOLDOWN:
                self.last_attack_time = current_time
                self.player.take_damage(ZOMBIE_DAMAGE)
                direction = 1 if self.player.x > self.x else -1
                self.player.x += direction * 0.5
                self.player.y += 0.5

    def find_valid_target(self, px, py):
        tx, ty = int(round(px)), int(round(py))
        if self.is_standable(tx, ty): return (tx, ty)
        return None

    def apply_gravity_robust(self):
        foot_offset_x = (self.collider_width / 2) - 0.01
        left_foot = self.position + Vec3(-foot_offset_x, 0.1, 0)
        right_foot = self.position + Vec3(foot_offset_x, 0.1, 0)
        
        # Raycast sedikit lebih panjang karena badan tinggi
        hit_left = raycast(left_foot, Vec3(0, -1, 0), distance=0.8, ignore=(self, self.visual), debug=False)
        hit_right = raycast(right_foot, Vec3(0, -1, 0), distance=0.8, ignore=(self, self.visual), debug=False)

        if hit_left.hit or hit_right.hit:
            self.is_grounded = True
            if self.y_velocity < 0: self.y_velocity = 0
        else:
            self.is_grounded = False
            self.y_velocity -= self.gravity_force * time.dt
        
        self.y += self.y_velocity * time.dt

    def check_vision(self):
        dist = distance(self.position, self.player.position)
        if dist > self.vision_range: return False 
        if abs(self.player.y - self.y) > self.vertical_vision: return False
        
        # Mata di posisi kepala (lebih tinggi dari pusat)
        eye_pos = self.position + Vec3(0, 0.5, 0)
        target_eye = self.player.position + Vec3(0, 0.5, 0)
        direction = (target_eye - eye_pos).normalized()
        
        hit = raycast(eye_pos, direction, distance=self.vision_range, ignore=(self, self.visual), debug=False)
        if hit.hit:
            if distance(hit.world_point, target_eye) < 1.5: return True
            return False
        return True

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        x, y = pos
        moves = []
        potential_moves = [(1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for dx, dy in potential_moves:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < WIDTH and 0 <= ny < DEPTH): continue
            
            # --- CEK BADAN 2 BLOK ---
            # 1. Cek Kaki
            if (nx, ny) in self.world.block_positions: continue
            
            # 2. Cek Kepala (WAJIB UNTUK 1x2)
            if (nx, ny+1) in self.world.block_positions: continue
            
            # 3. Cek Lantai (Pijakan)
            has_floor = (nx, ny-1) in self.world.block_positions
            
            if dy <= 0 and not has_floor: continue
            
            # 4. Cek Langit-langit kalau lompat (y+2 harus kosong)
            if dy == 1 and (x, y+2) in self.world.block_positions: continue
            
            moves.append((nx, ny))
        return moves

    def is_standable(self, x, y):
        # Wajib 2 blok kosong vertikal (kaki & kepala) + ada lantai
        return ((x, y) not in self.world.block_positions) and \
               ((x, y+1) not in self.world.block_positions) and \
               ((x, y-1) in self.world.block_positions)

    def astar(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        steps = 0
        while open_set:
            steps += 1
            if steps > self.max_search_steps: return []
            current = heapq.heappop(open_set)[1]
            if current == goal: return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current):
                tg = g_score[current] + 1
                if neighbor not in g_score or tg < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tg
                    f_score[neighbor] = tg + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def bfs(self, start, goal):
        queue = deque([(start, [start])])
        visited = set([start])
        steps = 0
        while queue:
            steps += 1
            if steps > self.max_search_steps: return []
            (v, p) = queue.popleft()
            if v == goal: return p[1:]
            for n in self.get_neighbors(v):
                if n not in visited:
                    visited.add(n)
                    queue.append((n, p + [n]))
        return []

    def reconstruct_path(self, cf, cur):
        p = [cur]
        while cur in cf:
            cur = cf[cur]
            p.insert(0, cur)
        return p[1:]