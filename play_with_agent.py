"""
This code acts as a game loop for the zombie shooter game using Pygame, where an agent plays the game using a pre-trained Q-table.

Code Analysis:

1. It loads a pre-trained Q-table from a file (`training_data.npz`) if it exists, otherwise it exits.

2. It resets the game and gets the initial state.

3. It enters a game loop where it:
   - Chooses the best action from the Q-table based on the current state.
   - Performs the chosen action in the game and gets the next state, reward, and whether the game is over.
   - Updates the state.
   - Draws the game screen.
   - Limits the game speed to a certain frames per second (FPS).

4. The loop continues until the game is over, at which point it prints a message and quits Pygame.

About Q-table:

The Q-table is a data structure that stores the expected reward for each state-action pair, which is used to make decisions in the game. The agent uses this Q-table to play the game without any exploration or learning.
"""

import pygame
import sys
import numpy as np
from zombie_shooter_with_rl import get_state, step, reset_game, draw_game, clock, FPS

TRAINING_FILE = (
    "training_data.npz"  # storing q-values and epsilon for the trained model
)

# Load the trained Q-table
try:
    data = np.load(TRAINING_FILE)
    q_table = data["q_table"]
    print(f"Successfully loaded Q-table from {TRAINING_FILE}")
except FileNotFoundError:
    print(f"Error: Training file '{TRAINING_FILE}' not found. Cannot run the agent.")
    sys.exit()

# Main Game Loop
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
