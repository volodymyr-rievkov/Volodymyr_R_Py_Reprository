import gymnasium as gym
import numpy as np
from tqdm import trange, tqdm
import matplotlib.pyplot as plt
import time
import os
import json

class QAgent:
    def __init__(self,
                 bins=(12, 12, 24, 24),
                 alpha=0.2,
                 gamma=0.99,
                 epsilon=1.0,
                 epsilon_decay=0.9995,
                 min_alpha=0.05,
                 min_epsilon=0.01,
                 relative_path="PythonApplications/ML/Lab_4/data"):
        self.env = gym.make('CartPole-v1')
        self.alpha_init = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_alpha = min_alpha
        self.min_epsilon = min_epsilon
        self.bins = bins
        self.q_table = np.zeros(bins + (self.env.action_space.n,))
        self.episodes_trained = 0
        self.relative_path = relative_path
        self.table_path = None

        self.obs_low = np.array([-2.4, -3.0, -0.209, -3.0])
        self.obs_high = np.array([2.4, 3.0, 0.209, 3.0])

    def discretize(self, obs):
        ratios = (obs - self.obs_low) / (self.obs_high - self.obs_low)
        indices = np.clip((ratios * np.array(self.bins)).astype(int),
                          0, np.array(self.bins) - 1)
        return tuple(indices)

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        return np.argmax(self.q_table[state])

    def train(self, episodes=15000, early_window=150, early_mean=495, early_min=480):
        rewards = []
        start_time = time.time()
        
        with trange(episodes, desc="Training", ncols=100) as pbar:
            for ep in pbar:
                obs, _ = self.env.reset()
                state = self.discretize(obs)
                total_reward = 0
                done = False
                truncated = False

                while not (done or truncated):
                    action = self.choose_action(state)
                    next_obs, reward, done, truncated, _ = self.env.step(action)
                    next_state = self.discretize(next_obs)

                    alpha = max(self.min_alpha, self.alpha_init * (1 - ep / episodes))
                    best_next = np.max(self.q_table[next_state])
                    self.q_table[state + (action,)] += alpha * (
                        reward + self.gamma * best_next - self.q_table[state + (action,)]
                    )

                    state = next_state
                    total_reward += reward

                self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
                rewards.append(total_reward)

                if len(rewards) >= early_window:
                    last_window = rewards[-early_window:]
                    if np.mean(last_window) >= early_mean and np.min(last_window) >= early_min:
                        self.episodes_trained = ep + 1
                        tqdm.write(f"Early stopping at episode {ep}, reward stabilized.")
                        break
                GREEN = "\033[92m"
                RED = "\033[91m"
                RESET = "\033[0m"
                color = GREEN if total_reward >= early_mean else RED
                pbar.set_postfix({"last_reward": f"{color}{total_reward}{RESET}"})
            else:
                self.episodes_trained = episodes

        elapsed = time.time() - start_time
        print(f"\nTraining finished in {(elapsed / 60):.2f} minutes.")
        print(f"Average reward (last {early_window} eps): {np.mean(rewards[-early_window:]):.2f}")
        return rewards

    def play(self, episodes=5, delay=0.02, render=True):
        env = gym.make('CartPole-v1', render_mode='human' if render else None)
        total_rewards = []

        for ep in range(1, episodes + 1):
            obs, _ = env.reset()
            state = self.discretize(obs)
            done = False
            truncated = False
            total_reward = 0

            while not (done or truncated):
                if render:
                    env.render()
                action = np.argmax(self.q_table[state])
                next_obs, reward, done, truncated, _ = env.step(action)
                state = self.discretize(next_obs)
                total_reward += reward
                time.sleep(delay)

            print(f"Episode {ep}: Reward = {total_reward:.2f}")
            total_rewards.append(total_reward)

        env.close()
        print(f"Average reward over {episodes} episodes: {np.mean(total_rewards):.2f}")
        return total_rewards

    def plot_rewards(self, rewards, window=100):
        plt.figure(figsize=(10, 5))
        plt.plot(rewards, label="Episode reward", alpha=0.4)
        if len(rewards) >= window:
            moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
            plt.plot(range(window-1, len(rewards)), moving_avg,
                     label=f"Moving average ({window})", linewidth=2)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title(f"Training Performance ({self.episodes_trained} episodes)")
        plt.legend()
        plt.grid(True)
        
        os.makedirs(self.relative_path, exist_ok=True)
        plot_path = os.path.join(self.relative_path, f"training_plot_{self.episodes_trained}.png")
        plt.savefig(plot_path)
        print(f"Plot saved to {plot_path}")
        plt.show()

    def save_qtable(self):
        os.makedirs(self.relative_path, exist_ok=True)
        path = os.path.join(self.relative_path, f"q_table_{self.episodes_trained}.npy")
        np.save(path, self.q_table)
        print(f"Q-table saved to {path}")
        self.table_path = path

    def load_qtable(self, path=None):
        if path is None:
            path = self.table_path
        if os.path.exists(path):
            self.q_table = np.load(path, allow_pickle=True)
            print(f"Q-table loaded from {path}")
        else:
            print("No Q-table found at the given path.")

    def save_params(self):
        os.makedirs(self.relative_path, exist_ok=True)
        path = os.path.join(self.relative_path, f"params_{self.episodes_trained}.json")
        params = {
            "bins": self.bins,
            "alpha_init": self.alpha_init,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_decay": self.epsilon_decay,
            "min_alpha": self.min_alpha,
            "min_epsilon": self.min_epsilon,
            "episodes_trained": self.episodes_trained
        }
        with open(path, "w") as f:
            json.dump(params, f, indent=4)
        print(f"Parameters saved to {path}")


if __name__ == "__main__":
    agent = QAgent()
    # rewards = agent.train(episodes=15000)
    # agent.save_qtable()
    # agent.save_params()
    # agent.plot_rewards(rewards)
    agent.load_qtable("PythonApplications/ML/Lab_4/data/q_table_9341.npy")
    agent.play(episodes=5)
