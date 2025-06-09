import pygame
import sys
import random
from collections import deque
from time import time
import numpy as np


class ZombieShooter:
    def __init__(self, width=800, height=600, fps=60):
        pygame.init()
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self.PLAYER_SPEED = 5
        self.BULLET_SPEED = 7
        self.PLAYER_HEALTH = 3
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.CYAN = (0, 255, 255)
        self.BLACK = (50, 50, 50)
        self.DOUBLE_TAP_WINDOW = 0.3
        self.PHASES = [
            {"name": "Phase 1", "spawn_delay": 1500, "zombie_speed": 2, "duration": 30},
            {"name": "Phase 2", "spawn_delay": 1000, "zombie_speed": 3, "duration": 30},
            {
                "name": "Phase 3",
                "spawn_delay": 500,
                "zombie_speed": 4,
                "duration": float("inf"),
            },
        ]
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Zombie Shooter: Survival")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 30)
        self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.background.fill(self.BLACK)
        self.player_img = pygame.Surface((40, 40))
        self.player_img.fill(self.GREEN)
        self.zombie_img = pygame.Surface((40, 40))
        self.zombie_img.fill(self.RED)
        self.bullet_img = pygame.Surface((5, 10))
        self.bullet_img.fill(self.WHITE)
        self.arrow_img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.arrow_img, self.CYAN, [(10, 0), (5, 15), (15, 15)])
        self.reset()

    def reset(self):
        self.player = pygame.Rect(self.WIDTH // 2 - 20, self.HEIGHT // 2 - 20, 40, 40)
        self.bullets = []  # (rect, direction)
        self.zombies = []
        self.score = 0
        self.health = self.PLAYER_HEALTH
        self.phase = 0
        self.phase_start_time = time()
        self.last_spawn = pygame.time.get_ticks()
        self.aim_direction = (0, -1)  # Default up
        self.key_times = {
            pygame.K_UP: deque(maxlen=2),
            pygame.K_DOWN: deque(maxlen=2),
            pygame.K_LEFT: deque(maxlen=2),
            pygame.K_RIGHT: deque(maxlen=2),
        }
        self.game_over = False
        return self.get_state()

    def get_state(self):
        player_x = self.player.x / self.WIDTH
        player_y = self.player.y / self.HEIGHT
        health = self.health / self.PLAYER_HEALTH
        aim = [0, 0, 0, 0]  # up, down, left, right
        if self.aim_direction == (0, -1):
            aim[0] = 1
        elif self.aim_direction == (0, 1):
            aim[1] = 1
        elif self.aim_direction == (-1, 0):
            aim[2] = 1
        elif self.aim_direction == (1, 0):
            aim[3] = 1
        zombie_positions = np.zeros(20)  # 10 zombies, x/y each
        for i, zombie in enumerate(self.zombies[:10]):
            zombie_positions[2 * i] = zombie.x / self.WIDTH
            zombie_positions[2 * i + 1] = zombie.y / self.HEIGHT
        phase = self.phase / 2  # Normalize (0, 0.5, 1)
        state = np.array(
            [player_x, player_y, health] + aim + zombie_positions.tolist() + [phase],
            dtype=np.float32,
        )
        return state

    def step(self, action=None):
        reward = 0.1  # Survival reward
        done = False
        if self.game_over:
            return self.get_state(), -50, True, {}
        delta_time = self.clock.tick(self.FPS) / 1000.0
        # Handle action (for RL)
        if action is not None:
            if action == 0:  # Stay
                pass
            elif action == 1:  # Up
                if self.player.top > 0:
                    self.player.y -= self.PLAYER_SPEED
            elif action == 2:  # Down
                if self.player.bottom < self.HEIGHT:
                    self.player.y += self.PLAYER_SPEED
            elif action == 3:  # Left
                if self.player.left > 0:
                    self.player.x -= self.PLAYER_SPEED
            elif action == 4:  # Right
                if self.player.right < self.WIDTH:
                    self.player.x += self.PLAYER_SPEED
            elif action == 5:  # Shoot up
                self.aim_direction = (0, -1)
                bullet_rect = pygame.Rect(
                    self.player.centerx - 2.5, self.player.centery - 5, 5, 10
                )
                self.bullets.append((bullet_rect, self.aim_direction))
                reward -= 0.1  # Shooting penalty
            elif action == 6:  # Shoot down
                self.aim_direction = (0, 1)
                bullet_rect = pygame.Rect(
                    self.player.centerx - 2.5, self.player.centery - 5, 5, 10
                )
                self.bullets.append((bullet_rect, self.aim_direction))
                reward -= 0.1
            elif action == 7:  # Shoot left
                self.aim_direction = (-1, 0)
                bullet_rect = pygame.Rect(
                    self.player.centerx - 2.5, self.player.centery - 5, 5, 10
                )
                self.bullets.append((bullet_rect, self.aim_direction))
                reward -= 0.1
            elif action == 8:  # Shoot right
                self.aim_direction = (1, 0)
                bullet_rect = pygame.Rect(
                    self.player.centerx - 2.5, self.player.centery - 5, 5, 10
                )
                self.bullets.append((bullet_rect, self.aim_direction))
                reward -= 0.1
        # Update phase
        current_time = time()
        if (
            self.phase < len(self.PHASES) - 1
            and current_time - self.phase_start_time
            > self.PHASES[self.phase]["duration"]
        ):
            self.phase += 1
            self.phase_start_time = current_time
            self.last_spawn = pygame.time.get_ticks()
            reward += 5  # Phase transition reward
        # Spawn zombies
        now = pygame.time.get_ticks()
        if now - self.last_spawn > self.PHASES[self.phase]["spawn_delay"]:
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge == "top":
                zombie = pygame.Rect(random.randint(0, self.WIDTH - 40), 0, 40, 40)
            elif edge == "bottom":
                zombie = pygame.Rect(
                    random.randint(0, self.WIDTH - 40), self.HEIGHT - 40, 40, 40
                )
            elif edge == "left":
                zombie = pygame.Rect(0, random.randint(0, self.HEIGHT - 40), 40, 40)
            else:
                zombie = pygame.Rect(
                    self.WIDTH - 40, random.randint(0, self.HEIGHT - 40), 40, 40
                )
            self.zombies.append(zombie)
            self.last_spawn = now
        # Move zombies
        zombie_speed = self.PHASES[self.phase]["zombie_speed"]
        for zombie in self.zombies[:]:
            dx = self.player.centerx - zombie.centerx
            dy = self.player.centery - zombie.centery
            dist = (dx**2 + dy**2) ** 0.5
            if dist > 0:
                dx, dy = dx / dist, dy / dist
                zombie.x += dx * zombie_speed
                zombie.y += dy * zombie_speed
            if not (-40 <= zombie.x <= self.WIDTH and -40 <= zombie.y <= self.HEIGHT):
                self.zombies.remove(zombie)
        # Update bullets
        for bullet, direction in self.bullets[:]:
            bullet.x += direction[0] * self.BULLET_SPEED
            bullet.y += direction[1] * self.BULLET_SPEED
            if not (0 <= bullet.x <= self.WIDTH and 0 <= bullet.y <= self.HEIGHT):
                self.bullets.remove((bullet, direction))
        # Collisions
        for bullet, _ in self.bullets[:]:
            for zombie in self.zombies[:]:
                if bullet.colliderect(zombie):
                    self.bullets.remove((bullet, _))
                    self.zombies.remove(zombie)
                    self.score += 1
                    reward += 10  # Kill reward
                    break
        for zombie in self.zombies[:]:
            if self.player.colliderect(zombie):
                self.zombies.remove(zombie)
                self.health -= 1
                reward -= 20  # Damage penalty
                if self.health <= 0:
                    self.game_over = True
                    reward -= 50  # Game over penalty
                    done = True
        return self.get_state(), reward, done, {}

    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player_img, self.player)
        for zombie in self.zombies:
            self.screen.blit(self.zombie_img, zombie)
        for bullet, _ in self.bullets:
            self.screen.blit(self.bullet_img, bullet)
        arrow_rotated = pygame.transform.rotate(
            self.arrow_img,
            {(-1, 0): 90, (1, 0): -90, (0, 1): 180, (0, -1): 0}[self.aim_direction],
        )
        arrow_rect = arrow_rotated.get_rect(
            center=(self.player.centerx, self.player.top - 15)
        )
        self.screen.blit(arrow_rotated, arrow_rect)
        health_text = self.font.render(f"Health: {self.health}", True, self.WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        phase_text = self.font.render(self.PHASES[self.phase]["name"], True, self.WHITE)
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(score_text, (10, 40))
        self.screen.blit(phase_text, (10, 70))
        if self.game_over:
            game_over_text = self.font.render(
                f"Game Over! Score: {self.score} ({self.PHASES[self.phase]['name']})",
                True,
                self.WHITE,
            )
            self.screen.blit(game_over_text, (self.WIDTH // 2 - 150, self.HEIGHT // 2))
        pygame.display.flip()

    def handle_human_input(self):
        reward = 0
        done = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not self.game_over:
                if event.key in (
                    pygame.K_UP,
                    pygame.K_DOWN,
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                ):
                    self.key_times[event.key].append(time())
                    if (
                        len(self.key_times[event.key]) == 2
                        and self.key_times[event.key][1] - self.key_times[event.key][0]
                        <= self.DOUBLE_TAP_WINDOW
                    ):
                        bullet_rect = pygame.Rect(
                            self.player.centerx - 2.5, self.player.centery - 5, 5, 10
                        )
                        self.bullets.append((bullet_rect, self.aim_direction))
                        reward -= 0.1
                    if event.key == pygame.K_UP:
                        self.aim_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.aim_direction = (0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.aim_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.aim_direction = (1, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player.left > 0:
            self.player.x -= self.PLAYER_SPEED
        if keys[pygame.K_d] and self.player.right < self.WIDTH:
            self.player.x += self.PLAYER_SPEED
        if keys[pygame.K_w] and self.player.top > 0:
            self.player.y -= self.PLAYER_SPEED
        if keys[pygame.K_s] and self.player.bottom < self.HEIGHT:
            self.player.y += self.PLAYER_SPEED
        return reward, done


def main():
    game = ZombieShooter()
    running = True
    while running:
        reward, done = game.handle_human_input()
        state, step_reward, step_done, _ = game.step()
        reward += step_reward
        done = done or step_done
        game.render()
        if done:
            pygame.time.wait(3000)
            running = False
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
