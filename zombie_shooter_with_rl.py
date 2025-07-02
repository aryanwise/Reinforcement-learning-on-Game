"""
This game environment is the enhanced version of the zombie_shooter.py incorporating the Q-learning components like state, actions and rewards to train the Q-learning model
"""

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
    {"name": "Phase 1", "spawn_delay": 1500, "zombie_speed": 2, "time": 60},
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
    """
    Resets the game to its initial state.

    This function reinitializes key game variables to their starting values,
    positioning the player at the center of the screen, clearing bullets and
    zombies, resetting health, score, and phase, and setting the game_over flag
    to False. It also records the current time for phase management and updates
    the time of the last zombie spawn.
    """
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
    """
    Returns the current state of the game as a tuple representing:
    1. Player's position relative to the walls (0: not near, 1: near top, 2: near bottom, 3: near left, 4: near right).
    2. Player's health as an integer.
    3. Current game phase as an integer.
    4. Direction of the nearest zombie relative to the player (0: no zombie, 1: up, 2: up-right, 3: right, 4: down-right,
       5: down, 6: down-left, 7: left, 8: up-left).

    The state provides a simplified representation of the game's condition used for decision-making
    in reinforcement learning.
    """
    # 1. Player position (near wall or not)
    player_pos_state = 0
    if player.top < 50:
        player_pos_state = 1  # Near Top
    elif player.bottom > HEIGHT - 50:
        player_pos_state = 2  # Near Bottom
    elif player.left < 50:
        player_pos_state = 3  # Near Left
    elif player.right > WIDTH - 50:
        player_pos_state = 4  # Near Right

    # 2. Health (already simple)
    health_state = int(health)

    # 3. Phase (already simple)
    phase_state = phase

    # 4. Nearest zombie relative direction
    zombie_dir_state = 0  # Default to "no zombie"
    if zombies:
        closest = min(
            zombies,
            key=lambda z: math.hypot(
                z.centerx - player.centerx, z.centery - player.centery
            ),
        )

        dx = closest.centerx - player.centerx
        dy = closest.centery - player.centery
        angle = math.degrees(math.atan2(-dy, dx))  # Angle in degrees

        if -22.5 <= angle < 22.5:
            zombie_dir_state = 3  # Right
        elif 22.5 <= angle < 67.5:
            zombie_dir_state = 2  # Up-Right
        elif 67.5 <= angle < 112.5:
            zombie_dir_state = 1  # Up
        elif 112.5 <= angle < 157.5:
            zombie_dir_state = 8  # Up-Left
        elif angle >= 157.5 or angle < -157.5:
            zombie_dir_state = 7  # Left
        elif -157.5 <= angle < -112.5:
            zombie_dir_state = 6  # Down-Left
        elif -112.5 <= angle < -67.5:
            zombie_dir_state = 5  # Down
        elif -67.5 <= angle < -22.5:
            zombie_dir_state = 4  # Down-Right

    return (player_pos_state, health_state, phase_state, zombie_dir_state)


def step(action):
    """
    Takes an action and updates the game state.

    The action is an integer in the range [0, 8):
        0: Stay
        1-4: Move up, down, left, right
        5-8: Shoot up, down, left, right

    Returns a tuple of (next state, reward, done) where:
        next state is a tuple of four integers representing the game state
        reward is a float representing the reward for the action
        done is a boolean indicating whether the game is over
    """
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
    """
    Moves the player based on keyboard input.

    This function checks the current state of keyboard keys to determine
    the direction of player movement. The player is moved left, right, up,
    or down by a predefined speed if the corresponding 'A', 'D', 'W', or 'S'
    key is pressed, ensuring the player remains within the screen bounds.
    """

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
    """
    Handles player input and updates game state accordingly.

    This function processes events from the Pygame event queue. If the quit event
    is detected, it terminates the game. For keydown events, it manages player
    actions such as aiming and shooting. The arrow keys set the aim direction,
    shown by a cyan arrow. Double-tapping an arrow key within a defined time
    interval fires a bullet in the current aim direction. It updates the last
    key pressed and the time of the key press to handle double-tap shooting.
    """

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
    """
    Draws the current game state to the screen.

    This function draws the player, zombies, bullets, aim arrow, and text
    elements such as health, score, and phase. If the game is over, it also
    renders a game over message and waits for 2 seconds before exiting.
    """
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
    """
    Updates the game state by managing phases, spawning and moving zombies, moving bullets, and checking for collisions.

    This function progresses the game through its phases based on elapsed time, spawns zombies at random edges with increasing frequency and speed as phases progress, and moves existing zombies towards the player. It also handles the movement of bullets and checks for collisions between bullets and zombies to update the score. Player health is reduced upon contact with zombies, leading to a game over if health reaches zero.
    """
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
    """
    Main game loop.

    If human is True, the function calls handle_input, move_player, and update_game
    each frame. If human is False, the function only calls draw_game, and relies on
    external calls to step to update the game state.

    The function runs an infinite loop, calling either the above functions or
    draw_game and clock.tick, depending on the value of human. The game loop will
    continue running until the user closes the game window, at which point the
    game will exit.
    """
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
