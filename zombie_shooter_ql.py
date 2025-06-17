import numpy as np
import random

# Import functions from game:
# Get state: Check what is happening inside the game
# Step: Perform action and get results eg: new state or reward
# Reset game: New game after end
# Draw game, clock, FPS: Visualise agent play
from zombie_shooter_with_rl import get_state, step, reset_game, draw_game, clock, FPS

# Q-learning parameters
alpha = 0.1  # Learning rate
gamma = 0.99  # Discount factor
epsilon = 1.0  # Exploration rate
epsilon_min = 0.01
epsilon_decay = 0.995
episodes = 5000  # We can increase the episode as per training
action_space_size = 9
state_space_size = (10, 10, 4, 4, 5, 5, 3)  # Shape of all possible states

# Initialize Q-table
q_table = np.zeros(state_space_size + (action_space_size,))


def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, action_space_size - 1)  # Explore
    else:
        return np.argmax(q_table[state])  # Exploit


# Training loop
for episode in range(episodes):
    state = reset_game()
    state = get_state()
    total_reward = 0
    done = False
    while not done:
        action = choose_action(state)
        next_state, reward, done = step(action)
        # Q-table update
        old_value = q_table[state + (action,)]
        next_max = np.max(q_table[next_state])
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state + (action,)] = new_value
        state = next_state
        total_reward += reward
        # Update game screen
        draw_game()
        clock.tick(FPS)
    # Decay epsilon
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay
    print(f"Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {epsilon}")

print("Training finished.")
np.save("q_table_enhanced.npy", q_table)
