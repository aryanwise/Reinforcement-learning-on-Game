import pygame
import sys
import random
import time
import math

# Start Pygame
pygame.init()

# Game settings
WIDTH = 800
HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
PLAYER_HEALTH = 3
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLACK = (50, 50, 50)
DOUBLE_TAP_TIME = 0.3

# Game phases
PHASES = [
    {"name": "Phase 1", "spawn_delay": 1500, "zombie_speed": 2, "time": 30},
    {"name": "Phase 2", "spawn_delay": 1000, "zombie_speed": 3, "time": 30},
    {"name": "Phase 3", "spawn_delay": 500, "zombie_speed": 4, "time": 999999},
]

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 30)

# Create images
background = pygame.Surface((WIDTH, HEIGHT))
background.fill(BLACK)
player_img = pygame.Surface((40, 40))
player_img.fill(GREEN)
zombie_img = pygame.Surface((40, 40))
zombie_img.fill(RED)
bullet_img = pygame.Surface((5, 10))
bullet_img.fill(WHITE)
arrow_img = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.polygon(arrow_img, CYAN, [(10, 0), (5, 15), (15, 15)])

# Game variables
player = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
bullets = []  # List of (rect, direction)
zombies = []
score = 0
health = PLAYER_HEALTH
phase = 0
phase_start = time.time()
last_spawn = pygame.time.get_ticks()
aim_direction = (0, -1)  # Up by default
game_over = False
last_key_time = 0
last_key = None


def reset_game():
    global player, bullets, zombies, health, game_over, last_spawn, score, phase, phase_start, aim_direction
    player = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
    bullets = []
    zombies = []
    health = PLAYER_HEALTH
    score = 0
    phase = 0
    phase_start = time.time()
    last_spawn = pygame.time.get_ticks()
    game_over = False
    aim_direction = (0, -1)


def get_state():
    # Discretize player position (10x10 grid)
    player_x = int(player.x // (WIDTH / 10))
    player_y = int(player.y // (HEIGHT / 10))
    # Normalize health
    health_norm = int(health)
    # Aim direction (0: up, 1: down, 2: left, 3: right)
    aim = (
        0
        if aim_direction == (0, -1)
        else 1 if aim_direction == (0, 1) else 2 if aim_direction == (-1, 0) else 3
    )
    # Nearest zombie position (discretized, or -1 if none)
    zombie_x, zombie_y = -1, -1
    if zombies:
        closest = min(
            zombies,
            key=lambda z: math.hypot(
                z.centerx - player.centerx, z.centery - player.centery
            ),
        )
        zombie_x = int(closest.x // (WIDTH / 4))
        zombie_y = int(closest.y // (HEIGHT / 4))
    # Phase (0, 1, 2)
    state = (player_x, player_y, health_norm, aim, zombie_x, zombie_y, phase)
    return state


def step(action):
    global player, health, score, game_over, aim_direction, phase, phase_start, last_spawn
    reward = 0.1  # Small reward for staying alive
    done = False
    if game_over:
        reset_game()
        reward -= 50  # Penalty for dying
        return get_state(), reward, True

    # Handle action (0: stay, 1-4: move, 5-8: shoot)
    if action == 0:  # Stay
        pass
    elif action == 1 and player.top > 0:  # Up
        player.y -= PLAYER_SPEED
    elif action == 2 and player.bottom < HEIGHT:  # Down
        player.y += PLAYER_SPEED
    elif action == 3 and player.left > 0:  # Left
        player.x -= PLAYER_SPEED
    elif action == 4 and player.right < WIDTH:  # Right
        player.x += PLAYER_SPEED
    elif action == 5:  # Shoot up
        aim_direction = (0, -1)
        bullet = pygame.Rect(player.centerx - 2.5, player.centery - 5, 5, 10)
        bullets.append((bullet, aim_direction))
        reward -= 0.1  # Small penalty for shooting
    elif action == 6:  # Shoot down
        aim_direction = (0, 1)
        bullet = pygame.Rect(player.centerx - 2.5, player.centery - 5, 5, 10)
        bullets.append((bullet, aim_direction))
        reward -= 0.1
    elif action == 7:  # Shoot left
        aim_direction = (-1, 0)
        bullet = pygame.Rect(player.centerx - 2.5, player.centery - 5, 5, 10)
        bullets.append((bullet, aim_direction))
        reward -= 0.1
    elif action == 8:  # Shoot right
        aim_direction = (1, 0)
        bullet = pygame.Rect(player.centerx - 2.5, player.centery - 5, 5, 10)
        bullets.append((bullet, aim_direction))
        reward -= 0.1

    # Update phase
    if phase < len(PHASES) - 1 and time.time() - phase_start > PHASES[phase]["time"]:
        phase += 1
        phase_start = time.time()
        last_spawn = pygame.time.get_ticks()
        reward += 5  # Reward for reaching new phase

    # Spawn zombies
    now = pygame.time.get_ticks()
    if now - last_spawn > PHASES[phase]["spawn_delay"]:
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            zombie = pygame.Rect(random.randint(0, WIDTH - 40), 0, 40, 40)
        elif edge == "bottom":
            zombie = pygame.Rect(random.randint(0, WIDTH - 40), HEIGHT - 40, 40, 40)
        elif edge == "left":
            zombie = pygame.Rect(0, random.randint(0, HEIGHT - 40), 40, 40)
        else:
            zombie = pygame.Rect(WIDTH - 40, random.randint(0, HEIGHT - 40), 40, 40)
        zombies.append(zombie)
        last_spawn = now

    # Move zombies
    zombie_speed = PHASES[phase]["zombie_speed"]
    for zombie in zombies[:]:
        dx = player.centerx - zombie.centerx
        dy = player.centery - zombie.centery
        dist = (dx**2 + dy**2) ** 0.5
        if dist > 0:
            zombie.x += (dx / dist) * zombie_speed
            zombie.y += (dy / dist) * zombie_speed
        if not (-40 <= zombie.x <= WIDTH and -40 <= zombie.y <= HEIGHT):
            zombies.remove(zombie)

    # Move bullets
    for bullet, direction in bullets[:]:
        bullet.x += direction[0] * BULLET_SPEED
        bullet.y += direction[1] * BULLET_SPEED
        if not (0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT):
            bullets.remove((bullet, direction))

    # Check collisions
    for bullet, _ in bullets[:]:
        for zombie in zombies[:]:
            if bullet.colliderect(zombie):
                bullets.remove((bullet, _))
                zombies.remove(zombie)
                score += 1
                reward += 10  # Reward for killing zombie
                break
    for zombie in zombies[:]:
        if player.colliderect(zombie):
            zombies.remove(zombie)
            health -= 1
            reward -= 20  # Penalty for taking damage
            if health <= 0:
                game_over = True
                reward -= 50  # Penalty for dying
                reset_game()
                return get_state(), reward, True

    return get_state(), reward, False


def move_player():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.left > 0:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_d] and player.right < WIDTH:
        player.x += PLAYER_SPEED
    if keys[pygame.K_w] and player.top > 0:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_s] and player.bottom < HEIGHT:
        player.y += PLAYER_SPEED


def handle_input():
    global aim_direction, last_key, last_key_time, bullets, game_over
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                current_time = time.time()
                if (
                    last_key == event.key
                    and current_time - last_key_time <= DOUBLE_TAP_TIME
                ):
                    bullet = pygame.Rect(
                        player.centerx - 2.5, player.centery - 5, 5, 10
                    )
                    bullets.append((bullet, aim_direction))
                last_key = event.key
                last_key_time = current_time
                if event.key == pygame.K_UP:
                    aim_direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    aim_direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    aim_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    aim_direction = (1, 0)


def draw_game():
    screen.blit(background, (0, 0))
    screen.blit(player_img, player)
    for zombie in zombies:
        screen.blit(zombie_img, zombie)
    for bullet, _ in bullets:
        screen.blit(bullet_img, bullet)
    angle = {(0, -1): 0, (0, 1): 180, (-1, 0): 90, (1, 0): -90}[aim_direction]
    arrow_rotated = pygame.transform.rotate(arrow_img, angle)
    arrow_rect = arrow_rotated.get_rect(center=(player.centerx, player.top - 15))
    screen.blit(arrow_rotated, arrow_rect)
    health_text = font.render(f"Health: {health}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    phase_text = font.render(PHASES[phase]["name"], True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(phase_text, (10, 70))
    if game_over:
        game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.flip()
        time.sleep(2)
    pygame.display.flip()


def update_game():
    global phase, phase_start, last_spawn, health, game_over, score
    # Update phase
    if phase < len(PHASES) - 1 and time.time() - phase_start > PHASES[phase]["time"]:
        phase += 1
        phase_start = time.time()
        last_spawn = pygame.time.get_ticks()
    # Spawn zombies
    now = pygame.time.get_ticks()
    if now - last_spawn > PHASES[phase]["spawn_delay"]:
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            zombie = pygame.Rect(random.randint(0, WIDTH - 40), 0, 40, 40)
        elif edge == "bottom":
            zombie = pygame.Rect(random.randint(0, WIDTH - 40), HEIGHT - 40, 40, 40)
        elif edge == "left":
            zombie = pygame.Rect(0, random.randint(0, HEIGHT - 40), 40, 40)
        else:
            zombie = pygame.Rect(WIDTH - 40, random.randint(0, HEIGHT - 40), 40, 40)
        zombies.append(zombie)
        last_spawn = now
    # Move zombies
    zombie_speed = PHASES[phase]["zombie_speed"]
    for zombie in zombies[:]:
        dx = player.centerx - zombie.centerx
        dy = player.centery - zombie.centery
        dist = (dx**2 + dy**2) ** 0.5
        if dist > 0:
            zombie.x += (dx / dist) * zombie_speed
            zombie.y += (dy / dist) * zombie_speed
        if not (-40 <= zombie.x <= WIDTH and -40 <= zombie.y <= HEIGHT):
            zombies.remove(zombie)
    # Move bullets
    for bullet, direction in bullets[:]:
        bullet.x += direction[0] * BULLET_SPEED
        bullet.y += direction[1] * BULLET_SPEED
        if not (0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT):
            bullets.remove((bullet, direction))
    # Check collisions
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
                reset_game()


def main(human=True):
    global game_over
    while True:
        if human:
            handle_input()
            move_player()
            update_game()
        else:
            # For RL, step is called externally
            pass
        draw_game()
        clock.tick(FPS)


if __name__ == "__main__":
    main(human=True)
