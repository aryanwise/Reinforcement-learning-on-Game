import random
import time
import os
import sys

# ANSI color codes for CLI visuals
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Game settings
GRID_SIZE = 5  # 5x5 grid
PLAYER_SPEED = 1
BULLET_RANGE = 5  # Bullets hit nearest zombie
PLAYER_HEALTH = 3
MAX_AMMO = 3
AMMO_RECHARGE = 0.2  # Ammo recharge probability per step
ZOMBIE_SPAWN_RATE = 0.3  # Probability per step
ZOMBIE_SPEED = 1
MAX_ZOMBIES = 2
WAVE_THRESHOLD = 10  # Kills needed for wave increase

# Initialize game state
player_x, player_y = GRID_SIZE // 2, GRID_SIZE // 2
health = PLAYER_HEALTH
ammo = MAX_AMMO
zombies = []  # List of (x, y)
bullets = []  # List of (x, y) for visual effect
score = 0
wave = 1
game_over = False
status_message = ""


def reset_game():
    global player_x, player_y, health, ammo, zombies, bullets, score, wave, game_over, status_message
    player_x, player_y = GRID_SIZE // 2, GRID_SIZE // 2
    health = PLAYER_HEALTH
    ammo = MAX_AMMO
    zombies = []
    bullets = []
    score = 0
    wave = 1
    game_over = False
    status_message = "Game started!"


def get_state():
    # State: (player_x, player_y, health, ammo, nearest_zombie_x, nearest_zombie_y)
    if zombies:
        nearest = min(
            zombies, key=lambda z: abs(z[0] - player_x) + abs(z[1] - player_y)
        )
        z_x, z_y = nearest
    else:
        z_x, z_y = -1, -1
    return (player_x, player_y, health, ammo, z_x, z_y)


def step(action):
    global player_x, player_y, health, ammo, zombies, bullets, score, wave, game_over, status_message
    reward = 0.01  # Survival reward
    done = False

    if game_over:
        reset_game()
        reward -= 20  # Death penalty
        status_message = "You died! Game reset."
        return get_state(), reward, done

    # Handle action
    status_message = ""
    if action == 0:  # Stay
        status_message = "Holding position."
    elif action == 1 and player_y > 0:  # Up
        player_y -= PLAYER_SPEED
        status_message = "Moved up."
    elif action == 2 and player_y < GRID_SIZE - 1:  # Down
        player_y += PLAYER_SPEED
        status_message = "Moved down."
    elif action == 3 and player_x > 0:  # Left
        player_x -= PLAYER_SPEED
        status_message = "Moved left."
    elif action == 4 and player_x < GRID_SIZE - 1:  # Right
        player_x += PLAYER_SPEED
        status_message = "Moved right."
    elif action == 5 and ammo > 0:  # Shoot
        ammo -= 1
        if zombies:
            nearest = min(
                zombies, key=lambda z: abs(z[0] - player_x) + abs(z[1] - player_y)
            )
            bullets.append(nearest)  # Visual effect
            zombies.remove(nearest)
            score += 10
            reward += 10  # Kill reward
            status_message = f"{YELLOW}Zombie killed! +10 points{RESET}"
            if score // WAVE_THRESHOLD >= wave:
                wave += 1
                status_message += f" {CYAN}Wave {wave} started!{RESET}"
        else:
            status_message = "Shot missed, no zombies!"
            reward -= 1  # Miss penalty
    elif action == 5:
        status_message = "Out of ammo!"

    # Recharge ammo
    if random.random() < AMMO_RECHARGE and ammo < MAX_AMMO:
        ammo += 1
        status_message += " Ammo recharged!"

    # Spawn zombies
    if len(zombies) < MAX_ZOMBIES and random.random() < ZOMBIE_SPAWN_RATE:
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x, y = random.randint(0, GRID_SIZE - 1), 0
        elif edge == "bottom":
            x, y = random.randint(0, GRID_SIZE - 1), GRID_SIZE - 1
        elif edge == "left":
            x, y = 0, random.randint(0, GRID_SIZE - 1)
        else:
            x, y = GRID_SIZE - 1, random.randint(0, GRID_SIZE - 1)
        if (x, y) not in zombies and (x, y) != (player_x, player_y):
            zombies.append((x, y))
            status_message += " Zombie spawned!"

    # Move zombies
    zombie_speed = ZOMBIE_SPEED * (1 + 0.1 * (wave - 1))
    for i, (zx, zy) in enumerate(zombies[:]):
        dx = player_x - zx
        dy = player_y - zy
        dist = max(abs(dx), abs(dy))
        if dist > 0:
            new_x = zx + int(zombie_speed * (dx // dist or 0))
            new_y = zy + int(zombie_speed * (dy // dist or 0))
            if (
                0 <= new_x < GRID_SIZE
                and 0 <= new_y < GRID_SIZE
                and (new_x, new_y) not in zombies
            ):
                zombies[i] = (new_x, new_y)

    # Check collisions
    for zx, zy in zombies[:]:
        if (zx, zy) == (player_x, player_y):
            health -= 1
            zombies.remove((zx, zy))
            reward -= 5  # Damage penalty
            status_message += f" {RED}Hit by zombie! -1 health{RESET}"
            if health <= 0:
                game_over = True
                reward -= 20
                reset_game()
                status_message = "You died! Game reset."
                return get_state(), reward, done

    # Clear bullets (visual effect)
    bullets.clear()

    return get_state(), reward, done


def draw_game():
    os.system("cls" if os.name == "nt" else "clear")
    # Draw border
    print(f"{CYAN}{'=' * 30}{RESET}")
    print(f"{CYAN}Zombie Shooter - Wave {wave}{RESET}")
    print(
        f"{GREEN}Health: {'♥' * health}{'♡' * (PLAYER_HEALTH - health)}{RESET}  "
        f"{YELLOW}Score: {score}{RESET}  {CYAN}Ammo: {'♦' * ammo}{'◇' * (MAX_AMMO - ammo)}{RESET}"
    )
    # Draw grid
    grid = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for bx, by in bullets:
        grid[by][bx] = f"{YELLOW}~{RESET}"
    for zx, zy in zombies:
        grid[zy][zx] = f"{RED}Z{RESET}"
    grid[player_y][player_x] = f"{GREEN}P{RESET}"
    print(f"{CYAN}{'―' * (GRID_SIZE * 2 + 1)}{RESET}")
    for row in grid:
        print(f"{CYAN}|{RESET} {' '.join(row)} {CYAN}|{RESET}")
    print(f"{CYAN}{'―' * (GRID_SIZE * 2 + 1)}{RESET}")
    # Draw status
    print(f"{CYAN}Status: {status_message}{RESET}")
    print(f"{CYAN}{'=' * 30}{RESET}")
    time.sleep(0.05)  # Smooth display


def main(human=False):
    reset_game()
    if human:
        while True:
            draw_game()
            action = input(
                "Move (w: up, s: down, a: left, d: right), Shoot (f), Quit (q): "
            )
            action_map = {"w": 1, "s": 2, "a": 3, "d": 4, "f": 5, "q": -1}
            if action == "q":
                print("Game over!")
                break
            state, reward, done = step(action_map.get(action, 0))
            print(f"Reward: {reward:.2f}")
    else:
        while True:
            draw_game()
            state, reward, done = step(0)  # Placeholder for RL


if __name__ == "__main__":
    main(human=True)
