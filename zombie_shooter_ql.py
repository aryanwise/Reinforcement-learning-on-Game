import pygame
import sys
import numpy as np
import random

# Make sure your game file is named this or update the import
from zombie_shooter_with_rl import (
    get_state,
    step,
    reset_game,
    draw_game,
    clock,
    FPS,
    main,
)

# --- TRAINING CONTROLS ---
VISUAL_TRAINING = False  # Set to False to train without graphics for max speed
LOAD_TRAINING_DATA = True  # Set to True to continue training from a saved file
SAVE_INTERVAL = 100  # Save the training data every 100 episodes
TRAINING_FILE = "training_data.npz"  # File to save/load data

# Q-learning parameters
alpha = 0.1
gamma = 0.99
# Epsilon will now be loaded from the file if it exists
epsilon_min = 0.01
epsilon_decay = 0.995

episodes = 5000
action_space_size = 9

# Simplified state space
state_space_size = (5, 4, 3, 9)  # (player_pos, health, phase, zombie_direction)

# Initialize or load Q-table and epsilon
if LOAD_TRAINING_DATA:
    try:
        data = np.load(TRAINING_FILE)
        q_table = data["q_table"]
        epsilon = data["epsilon"]
        print(
            f"Loaded training data. Q-table shape: {q_table.shape}, Epsilon: {epsilon:.4f}"
        )
    except FileNotFoundError:
        print("No training data found. Starting from scratch.")
        q_table = np.zeros(state_space_size + (action_space_size,))
        epsilon = 1.0  # Start with max exploration
else:
    q_table = np.zeros(state_space_size + (action_space_size,))
    epsilon = 1.0  # Start with max exploration


def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, action_space_size - 1)  # Explore
    else:
        return np.argmax(q_table[state])  # Exploit


# --- Main Training Loop ---
for episode in range(1, episodes + 1):
    state = reset_game()
    state = get_state()
    total_reward = 0
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save on exit and quit
                np.savez(TRAINING_FILE, q_table=q_table, epsilon=epsilon)
                pygame.quit()
                sys.exit()

        action = choose_action(state)
        next_state, reward, done = step(action)

        old_value = q_table[state + (action,)]
        next_max = np.max(q_table[next_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state + (action,)] = new_value

        state = next_state
        total_reward += reward

        if VISUAL_TRAINING:
            draw_game()

        clock.tick(FPS)

    # Decay epsilon
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    print(
        f"Episode: {episode}, Total Reward: {total_reward:.2f}, Epsilon: {epsilon:.4f}"
    )

    # Periodically save the Q-table AND epsilon
    if episode % SAVE_INTERVAL == 0:
        np.savez(TRAINING_FILE, q_table=q_table, epsilon=epsilon)
        print(f"--- Training data saved at episode {episode} ---")

print("Training finished.")
# Final save
np.savez(TRAINING_FILE, q_table=q_table, epsilon=epsilon)
