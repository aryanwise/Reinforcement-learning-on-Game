"""
Original Game: Zombie Shooter game built using the Pygame library.

GAME OVERVIEW:

Gameplay:

- The player controls a green square (the player) that can move around the screen using the 'A', 'D', 'W', and 'S' keys.
- The player can aim and shoot bullets in the direction of the arrow keys.
- Zombies (red squares) spawn at random edges of the screen and move towards the player.
- The player must avoid zombies and shoot them to earn points.
- The game has multiple phases with increasing difficulty (zombie spawn rate and speed).

Game Mechanics:

- Player movement and aiming
- Bullet shooting and collision detection
- Zombie spawning and movement
- Collision detection between player and zombies
- Game over condition (player health reaches zero)
- Scorekeeping and phase progression

Code Structure:

The game is organized into several functions:
    - handle_input: handles player input (keyboard and mouse events)
    - move_player: updates player position based on input
    - update_game: updates game state (zombie spawning, movement, collision detection, etc.)
    - draw_game: draws the game state to the screen
    - main: the main game loop that calls the above functions and limits the frame rate

Overall, this code provides a basic implementation of a zombie shooter game using Pygame, with features like player movement, aiming, shooting, zombie spawning, and collision detection.
"""

import pygame
import sys
import random
import time

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
    """
    Resets the game to its initial state.

    This function reinitializes key game variables to their starting values,
    positioning the player at the center of the screen, clearing bullets and
    zombies, resetting health, score, and phase, and setting the game_over flag
    to False. It also records the current time for phase management and updates
    the time of the last zombie spawn.
    """

    global player, bullets, zombies, health, game_over, last_spawn, score, phase, phase_start
    player = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
    bullets = []
    zombies = []
    health = PLAYER_HEALTH
    score = 0
    phase = 0
    phase_start = time.time()
    last_spawn = pygame.time.get_ticks()
    game_over = False


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
                # Check for double-tap to shoot
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
                # Set aim direction
                if event.key == pygame.K_UP:
                    aim_direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    aim_direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    aim_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    aim_direction = (1, 0)


def update_game():
    """
    Updates the game state by managing phases, spawning and moving zombies,
    moving bullets, and checking for collisions.

    This function progresses the game through its phases based on elapsed time,
    spawns zombies at random edges with increasing frequency and speed as phases
    progress, and moves existing zombies towards the player. It also handles
    the movement of bullets and checks for collisions between bullets and zombies
    to update the score. Player health is reduced upon contact with zombies,
    leading to a game over if health reaches zero.
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
    # Draw aim arrow
    angle = {(0, -1): 0, (0, 1): 180, (-1, 0): 90, (1, 0): -90}[aim_direction]
    arrow_rotated = pygame.transform.rotate(arrow_img, angle)
    arrow_rect = arrow_rotated.get_rect(center=(player.centerx, player.top - 15))
    screen.blit(arrow_rotated, arrow_rect)
    # Draw text
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
        time.sleep(2)  # Show game over for 2 seconds
    pygame.display.flip()


def main():
    """
    Main game loop.

    Calls handle_input, move_player, update_game, draw_game, and limits the
    frame rate to FPS in an infinite loop. The game loop will continue running
    until the user closes the game window, at which point the game will exit.
    """
    global game_over
    while True:
        handle_input()
        move_player()
        update_game()
        draw_game()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
