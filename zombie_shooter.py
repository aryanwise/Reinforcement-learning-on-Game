import pygame
import sys
import random
from collections import deque
from time import time

# Kick things off
pygame.init()

# Game constants
WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 7
PLAYER_HEALTH = 3
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLACK = (50, 50, 50)
FPS = 60
DOUBLE_TAP_WINDOW = 0.3  # Seconds for double-tap

# Phase settings
PHASES = [
    {"name": "Phase 1", "spawn_delay": 1500, "zombie_speed": 2, "duration": 30},
    {"name": "Phase 2", "spawn_delay": 1000, "zombie_speed": 3, "duration": 30},
    {
        "name": "Phase 3",
        "spawn_delay": 500,
        "zombie_speed": 4,
        "duration": float("inf"),
    },
]

# Setup window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter: Survival")

# Placeholder images
background = pygame.Surface((WIDTH, HEIGHT))
background.fill(BLACK)
player_img = pygame.Surface((40, 40))
player_img.fill(GREEN)
zombie_img = pygame.Surface((40, 40))
zombie_img.fill(RED)
bullet_img = pygame.Surface((5, 10))
bullet_img.fill(WHITE)
# Aim arrow (triangle shape)
arrow_img = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.polygon(arrow_img, CYAN, [(10, 0), (5, 15), (15, 15)])

# Player setup
player = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
bullets = []  # (rect, direction)
zombies = []
score = 0
health = PLAYER_HEALTH
phase = 0
phase_start_time = time()
last_spawn = pygame.time.get_ticks()
# Aim direction: (dx, dy), default up
aim_direction = (0, -1)
# Track key presses for double-tap
key_times = {
    pygame.K_UP: deque(maxlen=2),
    pygame.K_DOWN: deque(maxlen=2),
    pygame.K_LEFT: deque(maxlen=2),
    pygame.K_RIGHT: deque(maxlen=2),
}

# Font
font = pygame.font.SysFont("monospace", 30)

# Clock
clock = pygame.time.Clock()

# Main loop
running = True
game_over = False
while running:
    delta_time = clock.tick(FPS) / 1000.0  # Seconds per frame

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not game_over:
            # Update aim direction
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                key_times[event.key].append(time())
                # Check for double-tap
                if (
                    len(key_times[event.key]) == 2
                    and key_times[event.key][1] - key_times[event.key][0]
                    <= DOUBLE_TAP_WINDOW
                ):
                    # Shoot bullet in aim direction
                    bullet_rect = pygame.Rect(
                        player.centerx - 2.5, player.centery - 5, 5, 10
                    )
                    bullets.append((bullet_rect, aim_direction))
                # Set aim direction
                if event.key == pygame.K_UP:
                    aim_direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    aim_direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    aim_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    aim_direction = (1, 0)

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += PLAYER_SPEED
        if keys[pygame.K_w] and player.top > 0:
            player.y -= PLAYER_SPEED
        if keys[pygame.K_s] and player.bottom < HEIGHT:
            player.y += PLAYER_SPEED

        # Update phase
        current_time = time()
        if (
            phase < len(PHASES) - 1
            and current_time - phase_start_time > PHASES[phase]["duration"]
        ):
            phase += 1
            phase_start_time = current_time
            last_spawn = pygame.time.get_ticks()  # Reset spawn timer

        # Spawn zombies
        now = pygame.time.get_ticks()
        if now - last_spawn > PHASES[phase]["spawn_delay"]:
            # Spawn from random edge
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge == "top":
                zombie = pygame.Rect(random.randint(0, WIDTH - 40), 0, 40, 40)
            elif edge == "bottom":
                zombie = pygame.Rect(random.randint(0, WIDTH - 40), HEIGHT - 40, 40, 40)
            elif edge == "left":
                zombie = pygame.Rect(0, random.randint(0, HEIGHT - 40), 40, 40)
            else:  # right
                zombie = pygame.Rect(WIDTH - 40, random.randint(0, HEIGHT - 40), 40, 40)
            zombies.append(zombie)
            last_spawn = now

        # Move zombies toward player
        zombie_speed = PHASES[phase]["zombie_speed"]
        for zombie in zombies[:]:
            dx = player.centerx - zombie.centerx
            dy = player.centery - zombie.centery
            dist = (dx**2 + dy**2) ** 0.5
            if dist > 0:
                dx, dy = dx / dist, dy / dist
                zombie.x += dx * zombie_speed
                zombie.y += dy * zombie_speed
            # Remove if off-screen
            if not (-40 <= zombie.x <= WIDTH and -40 <= zombie.y <= HEIGHT):
                zombies.remove(zombie)

        # Update bullets
        for bullet, direction in bullets[:]:
            bullet.x += direction[0] * BULLET_SPEED
            bullet.y += direction[1] * BULLET_SPEED
            if not (0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT):
                bullets.remove((bullet, direction))

        # Collisions
        for bullet, _ in bullets[:]:
            for zombie in zombies[:]:
                if bullet.colliderect(zombie):
                    bullets.remove((bullet, _))
                    zombies.remove(zombie)
                    score += 1
                    break

        for zombie in zombies[:]:
            if player.colliderect(zombie):
                zombies.remove(zombie)
                health -= 1
                if health <= 0:
                    game_over = True

    # Draw
    screen.blit(background, (0, 0))
    screen.blit(player_img, player)
    for zombie in zombies:
        screen.blit(zombie_img, zombie)
    for bullet, _ in bullets:
        screen.blit(bullet_img, bullet)
    # Draw aim arrow
    arrow_rotated = pygame.transform.rotate(
        arrow_img, {(-1, 0): 90, (1, 0): -90, (0, 1): 180, (0, -1): 0}[aim_direction]
    )
    arrow_rect = arrow_rotated.get_rect(center=(player.centerx, player.top - 15))
    screen.blit(arrow_rotated, arrow_rect)

    # HUD
    health_text = font.render(f"Health: {health}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    phase_text = font.render(PHASES[phase]["name"], True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(phase_text, (10, 70))

    # Game over
    if game_over:
        game_over_text = font.render(
            f"Game Over! Score: {score} ({PHASES[phase]['name']})", True, WHITE
        )
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    pygame.display.flip()

# Clean up
pygame.quit()
sys.exit()
