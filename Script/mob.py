from ursina import *
from config import WIDTH, DEPTH, FG_Z
import heapq
from collections import deque
import random
import time


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def is_standable(world, x, y):
    return ((x, y) not in world.block_positions and
            (x, y + 1) not in world.block_positions and
            (x, y - 1) in world.block_positions)


def get_neighbors(world, pos):
    x, y = pos
    res = []
    for dx, dy in [(1,0), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < WIDTH and 0 <= ny < DEPTH):
            continue
        if is_standable(world, nx, ny):
            res.append((nx, ny))
    return res


def bfs(world, start, goal, max_steps=300):
    q = deque([(start, [start])])
    visited = {start}
    steps = 0

    print(f"[BFS] {start} -> {goal}")

    while q:
        steps += 1
        if steps > max_steps:
            print("[BFS] abort")
            return []

        curr, path = q.popleft()
        if curr == goal:
            print(f"[BFS] success len={len(path)-1}")
            return path[1:]

        for n in get_neighbors(world, curr):
            if n not in visited:
                visited.add(n)
                q.append((n, path + [n]))

    print("[BFS] failed")
    return []


def astar(world, start, goal, max_steps=300):
    def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    open_set = [(0, start)]
    came = {}
    g = {start: 0}
    steps = 0

    print(f"[A*] {start} -> {goal}")

    while open_set:
        steps += 1
        if steps > max_steps:
            print("[A*] abort")
            return []

        _, curr = heapq.heappop(open_set)
        if curr == goal:
            path = [curr]
            while curr in came:
                curr = came[curr]
                path.insert(0, curr)
            print(f"[A*] success len={len(path)-1}")
            return path[1:]

        for n in get_neighbors(world, curr):
            ng = g[curr] + 1
            if n not in g or ng < g[n]:
                g[n] = ng
                came[n] = curr
                heapq.heappush(open_set, (ng + h(n, goal), n))

    print("[A*] failed")
    return []


# =====================================================
# ZOMBIE
# =====================================================
class Zombie(Entity):
    def __init__(self, world, player, **kwargs):
        super().__init__(
            parent=scene,
            model='quad',
            color=color.green,
            origin_y=0,
            position=kwargs.get('position', (0,0)),
            scale=(0.9, 1.8),
            z=FG_Z
        )

        self.world = world
        self.player = player

        # movement
        self.walk_speed = 1.5
        self.run_speed = 3.5
        self.jump_force = 12
        self.gravity = 30
        self.max_fall = 20

        # physics
        self.y_vel = 0
        self.grounded = False

        # AI
        self.state = 'idle'
        self.path = []
        self.idx = 0
        self.path_timer = 0

        # cooldown idle walk
        self.idle_timer = 0.0
        self.walk_cd_min = 1.5
        self.walk_cd_max = 3.5

        print(f"[SPAWN] Zombie at {self.position}")


    def update(self):
        dt = time.dt
        self.ai(dt)
        self.move(dt)


    def ai(self, dt):
        if self.idle_timer > 0:
            self.idle_timer -= dt

        self.path_timer += dt
        dist = abs(self.player.x - self.x) + abs(self.player.y - self.y)

        prev = self.state
        self.state = 'chase' if dist < 10 else 'idle'
        if prev != self.state:
            print(f"[ZOMBIE] {prev} -> {self.state}")

        if self.path_timer > 0.3:
            self.path_timer = 0
            start = (round(self.x), round(self.y))

            if self.state == 'chase':
                tgt = (round(self.player.x), round(self.player.y))
                if is_standable(self.world, *tgt):
                    p = astar(self.world, start, tgt)
                    if p:
                        self.path = p
                        self.idx = 0

            elif self.state == 'idle':
                if self.idx >= len(self.path):
                    self.path = []
                    self.idx = 0

                if not self.path and self.idle_timer <= 0:
                    rx = start[0] + random.randint(-8, 8)
                    for ry in range(start[1]+2, start[1]-3, -1):
                        if is_standable(self.world, rx, ry):
                            p = bfs(self.world, start, (rx, ry))
                            if p:
                                self.path = p
                                self.idx = 0
                                break


    def move(self, dt):
        move_x = 0

        if self.path and self.idx < len(self.path):
            tx, ty = self.path[self.idx]

            if ty > self.y + 0.1 and self.grounded:
                self.y_vel = self.jump_force

            dx = tx - self.x
            if abs(dx) > 0.15:
                move_x = 1 if dx > 0 else -1
            else:
                self.idx += 1
        else:
            if self.path:
                print("[ZOMBIE] path finished -> idle cooldown")
                self.idle_timer = random.uniform(self.walk_cd_min, self.walk_cd_max)
            self.path = []
            self.idx = 0

        if move_x != 0:
            spd = self.run_speed if self.state == 'chase' else self.walk_speed
            self.x += move_x * spd * dt

        hit = raycast(self.position, Vec3(0,-1,0),
                      distance=(self.scale_y/2)+0.1,
                      ignore=(self,))
        if hit.hit:
            self.grounded = True
            if self.y_vel <= 0:
                self.y = hit.world_point.y + self.scale_y/2
                self.y_vel = 0
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
            color=color.red,
            origin_y=0,
            position=kwargs.get('position', (0,0)),
            scale=(0.8, 0.8),
            z=FG_Z
        )

        self.world = world
        self.player = player

        # movement
        self.walk_speed = 2.0
        self.run_speed = 4.0
        self.jump_force = 8
        self.gravity = 30
        self.max_fall = 20

        # physics
        self.y_vel = 0
        self.grounded = False

        # AI
        self.state = 'idle'
        self.path = []
        self.idx = 0

        self.hp = 4
        self.flee_timer = 0

        # cooldown walk
        self.idle_timer = 0.0
        self.walk_cd_min = 1.0
        self.walk_cd_max = 3.0

        print(f"[SPAWN] Chicken at {self.position}")


    def update(self):
        dt = time.dt
        self.ai(dt)
        self.move(dt)


    def ai(self, dt):
        if self.idle_timer > 0:
            self.idle_timer -= dt

        if self.flee_timer > 0:
            self.flee_timer -= dt

        if self.path and self.idx >= len(self.path):
            self.path = []
            self.idx = 0

        if self.state == 'flee':
            if self.flee_timer <= 0:
                self.state = 'idle'
                self.idle_timer = random.uniform(self.walk_cd_min, self.walk_cd_max)
            elif not self.path:
                self.run_away()

        elif self.state == 'idle':
            if not self.path and self.idle_timer <= 0:
                self.random_walk()

        elif self.state == 'walk':
            if not self.path:
                self.state = 'idle'
                self.idle_timer = random.uniform(self.walk_cd_min, self.walk_cd_max)


    def take_damage(self, dmg):
        self.hp -= dmg
        print(f"[CHICKEN] damage={dmg}, hp={self.hp}")

        if self.hp <= 0:
            destroy(self)
            return

        self.state = 'flee'
        self.flee_timer = 4.0
        self.path = []
        self.idx = 0
        self.run_away()


    def random_walk(self):
        start = (round(self.x), round(self.y))
        for _ in range(6):
            rx = start[0] + random.randint(-6, 6)
            for ry in range(start[1]+2, start[1]-3, -1):
                if is_standable(self.world, rx, ry):
                    p = bfs(self.world, start, (rx, ry))
                    if p:
                        self.path = p
                        self.idx = 0
                        self.state = 'walk'
                        return

        step = random.choice([-1,1])
        if is_standable(self.world, start[0]+step, start[1]):
            self.path = [(start[0]+step, start[1])]
            self.idx = 0
            self.state = 'walk'


    def run_away(self):
        start = (round(self.x), round(self.y))
        dirx = 1 if self.x - self.player.x >= 0 else -1

        for d in range(6,2,-1):
            tx = start[0] + dirx*d
            for ty in range(start[1]+2, start[1]-3, -1):
                if is_standable(self.world, tx, ty):
                    p = bfs(self.world, start, (tx, ty))
                    if p:
                        self.path = p
                        self.idx = 0
                        return


    def move(self, dt):
        move_x = 0

        if self.path and self.idx < len(self.path):
            tx, ty = self.path[self.idx]

            if ty > self.y + 0.1 and self.grounded:
                self.y_vel = self.jump_force

            dx = tx - self.x
            if abs(dx) > 0.15:
                move_x = 1 if dx > 0 else -1
            else:
                self.idx += 1
        else:
            self.path = []
            self.idx = 0

        if move_x != 0:
            spd = self.run_speed if self.state == 'flee' else self.walk_speed
            self.x += move_x * spd * dt

        hit = raycast(self.position, Vec3(0,-1,0),
                      distance=(self.scale_y/2)+0.1,
                      ignore=(self,))
        if hit.hit:
            self.grounded = True
            if self.y_vel <= 0:
                self.y = hit.world_point.y + self.scale_y/2
                self.y_vel = 0
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
        self.world = world
        self.player = player
        self.timer = 0

    def update(self):
        self.timer += time.dt
        if self.timer >= 3.0:
            self.timer = 0
            self.spawn()

    def spawn(self):
        px, py = round(self.player.x), round(self.player.y)
        for _ in range(30):
            dx = random.randint(-12,12)
            dy = random.randint(-6,6)
            if abs(dx) < 6:
                continue

            x, y = px+dx, py+dy
            if not (0<=x<WIDTH and 0<=y<DEPTH):
                continue

            if self.world.light_map[x][y] > 4:
                continue

            if is_standable(self.world, x, y):
                Zombie(self.world, self.player, position=(x,y))
                return


class ChickenSpawner:
    def __init__(self, world, player):
        self.world = world
        self.player = player
        self.timer = 0

    def update(self):
        self.timer += time.dt
        if self.timer >= 15.0:
            self.timer = 0
            self.spawn()

    def spawn(self):
        px, py = round(self.player.x), round(self.player.y)
        for _ in range(20):
            dx = random.randint(-20,20)
            dy = random.randint(-6,6)
            if abs(dx) < 5:
                continue

            x, y = px+dx, py+dy
            if not (0<=x<WIDTH and 0<=y<DEPTH):
                continue

            if self.world.light_map[x][y] <= 11:
                continue

            if is_standable(self.world, x, y):
                Chicken(self.world, self.player, position=(x,y))
                return
