import numpy as np
from zombie_env import ZombieEnv
from collections import defaultdict
import random
import time
import pygame


class QLearningAgent:
    def __init__(self):
        self.alpha = 0.05  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.01
        self.q_table = defaultdict(lambda: np.zeros(9))  # 9 actions

    def discretize_state(self, state):
        """Discretize the already discrete state from ZombieEnv"""
        px = min(int(state[0]), 14)  # grid_x (0 to 14, capped)
        py = min(int(state[1]), 14)  # grid_y (0 to 14, capped)
        health = min(int(state[2]), 3)  # health (0 to 3)
        aim_idx = int(state[3])  # aim_idx (0 to 3)
        zombie_count = min(int(state[4]), 5)  # zombie_count (0 to 5)
        phase = int(state[5])  # phase (0 to 2)
        return (px, py, health, aim_idx, zombie_count, phase)

    def choose_action(self, state):
        discrete_state = self.discretize_state(state)
        if random.random() < self.epsilon:
            return random.randint(0, 8)
        return np.argmax(self.q_table[discrete_state])

    def learn(self, state, action, reward, next_state, terminated):
        discrete_state = self.discretize_state(state)
        next_discrete = self.discretize_state(next_state)
        current_q = self.q_table[discrete_state][action]
        max_next_q = np.max(self.q_table[next_discrete])
        new_q = current_q + self.alpha * (
            reward + self.gamma * max_next_q * (1 - terminated) - current_q
        )
        self.q_table[discrete_state][action] = new_q
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)


def handle_pygame_events():
    """Process Pygame events to prevent freezing"""
    pygame.event.pump()  # Keep event queue clear
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            print("Quit event detected")
            return False
    return True


def train_agent(episodes=500):
    env = ZombieEnv(render_mode="none")  # No rendering during training
    agent = QLearningAgent()
    total_states = 0

    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        start_time = time.time()
        step_count = 0
        while True:
            if not handle_pygame_events():
                env.close()
                return None, None

            action = agent.choose_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            agent.learn(state, action, reward, next_state, terminated)
            state = next_state
            total_reward += reward
            step_count += 1

            if truncated:  # Quit on ESC
                break
            if terminated:  # Reset on death
                state, _ = env.reset()

        total_states = len(agent.q_table)
        if episode % 10 == 0:
            eps_time = time.time() - start_time
            print(
                f"Ep {episode:3d} | Reward: {total_reward:6.1f} | "
                f"Epsilon: {agent.epsilon:.2f} | States: {total_states} | "
                f"Steps: {step_count} | Time: {eps_time:.1f}s"
            )

    np.save("q_table.npy", dict(agent.q_table))
    env.close()
    return env, agent


def test_agent(env, agent, episodes=3, render_delay=50):
    env = ZombieEnv(render_mode="human")  # Render during testing
    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        while True:
            if not handle_pygame_events():
                env.close()
                return

            env.render()
            pygame.time.delay(render_delay)
            action = agent.choose_action(state)
            state, reward, terminated, truncated, _ = env.step(action)
            total_reward += reward

            if truncated:
                break
            if terminated:
                state, _ = env.reset()

        print(f"Test Episode {episode+1}: Reward = {total_reward:.1f}")
        pygame.time.delay(1000)

    env.close()


if __name__ == "__main__":
    print("=== TRAINING PHASE ===")
    env, agent = train_agent(episodes=300)
    if env and agent:
        print("\n=== TESTING PHASE ===")
        test_agent(env, agent, episodes=3)
