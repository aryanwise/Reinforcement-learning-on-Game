import pygame
import sys
import numpy as np
from zombie_shooter_with_rl import get_state, step, reset_game, draw_game, clock, FPS

# --- CONFIGURATION ---
TRAINING_FILE = "training_data.npz"  # The trained model you want to watch

# Load the trained Q-table
try:
    data = np.load(TRAINING_FILE)
    q_table = data["q_table"]
    print(f"Successfully loaded Q-table from {TRAINING_FILE}")
except FileNotFoundError:
    print(f"Error: Training file '{TRAINING_FILE}' not found. Cannot run the agent.")
    sys.exit()

# --- MAIN GAME LOOP ---
reset_game()
state = get_state()
game_over = False

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 1. Choose the BEST action from the Q-table (no exploration)
    action = np.argmax(q_table[state])

    # 2. Perform the action in the game
    next_state, reward, done = step(action)

    # Check if the step function indicated the game is over
    if done:
        # The step function already calls reset_game, so we can just end the loop
        game_over = True

    # 3. Update the state
    state = next_state

    # 4. Draw the game screen
    draw_game()

    # 5. Tick the clock
    clock.tick(FPS)

print("Game over. The agent has finished playing.")
pygame.quit()
