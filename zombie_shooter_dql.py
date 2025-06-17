import numpy as np
import pickle
from zombie_shooter import ZombieShooter  # ensure your class is saved as zombie_game.py

# Environment setup
env = ZombieShooter()
n_actions = 9  # 0 = stay, 1 = up, 2 = down, 3 = left, 4 = right, 5–8 = shoot directions

# Hyperparameters
episodes = 10000
learning_rate = 0.1
discount_factor = 0.95
epsilon = 1.0
min_epsilon = 0.01
decay_rate = 0.0005

# State space sizes
grid_x_max = env.WIDTH // env.GRID_SIZE
grid_y_max = env.HEIGHT // env.GRID_SIZE
health_states = 4  # 0 to 3
aim_states = 4  # 0 to 3
zombie_count_states = 6  # 0 to 5
phase_states = 3  # 0 to 2

# Q-table dimensions
Q = np.zeros(
    (
        grid_x_max,
        grid_y_max,
        health_states,
        aim_states,
        zombie_count_states,
        phase_states,
        n_actions,
    )
)


def get_action(state, epsilon):
    if np.random.random() < epsilon:
        return np.random.randint(n_actions)
    return np.argmax(Q[state])


# Training loop
for episode in range(episodes):
    state = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = get_action(state, epsilon)
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        # Q-learning update
        best_next_action = np.argmax(Q[next_state])
        Q[state][action] = Q[state][action] + learning_rate * (
            reward
            + discount_factor * Q[next_state][best_next_action]
            - Q[state][action]
        )

        state = next_state
        total_reward += reward

    # Epsilon decay
    epsilon = max(min_epsilon, epsilon * np.exp(-decay_rate * episode))

    if episode % 100 == 0:
        print(
            f"Episode {episode} | Total Reward: {total_reward:.2f} | Epsilon: {epsilon:.4f}"
        )

# Save Q-table
with open("q_table.pkl", "wb") as f:
    pickle.dump(Q, f)

print("Training completed and Q-table saved!")
