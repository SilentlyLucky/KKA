from ursina import *
import random
from config import WIDTH, DEPTH
from mob import Zombie

class ZombieSpawner:
    def __init__(self, world, player):
        self.world = world
        self.player = player
        self.timer = 0
        self.spawn_interval = 15.0
        self.min_light = 4
        self.spawn_radius = 10
        self.max_attempts = 30

    def update(self):
        self.timer += time.dt
        if self.timer >= self.spawn_interval:
            self.timer = 0
            self.try_spawn()

    def try_spawn(self):
        px, py = int(self.player.x), int(self.player.y)

        for _ in range(self.max_attempts):
            dx = random.randint(-self.spawn_radius, self.spawn_radius)
            dy = random.randint(-self.spawn_radius, self.spawn_radius)

            if abs(dx) + abs(dy) < self.spawn_radius - 2:
                continue

            x = px + dx
            y = py + dy

            if not (0 <= x < WIDTH and 0 <= y < DEPTH):
                continue

            # 1. Harus gelap
            if self.world.light_map[x][y] > self.min_light:
                continue

            # 2. Harus bisa berdiri
            if not self.world.is_standable(x, y):
                continue

            # 3. Spawn zombie
            Zombie(
                world=self.world,
                player=self.player,
                position=(x, y)
            )
            print(f"[SPAWN] Zombie at ({x},{y}) light={self.world.light_map[x][y]}")
            return
