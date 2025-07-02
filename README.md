# Zombie Shooter with Reinforcement Learning Agent

> Developed By: Aryan Mishra

This project demonstrates my implementation of a **Q-learning Reinforcement Learning (RL) agent** trained to play a custom-built 2D arcade game, **"Zombie Shooter,"** developed using Pygame.

The agent learns to **navigate, evade zombies, and shoot them** to maximize its score and survival time. This repository includes the full game environment, RL training script, playback script, and a Jupyter Notebook for project analysis.

---

## 🔧 Setup and Installation

To run this project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone "https://github.com/aryanwise/Reinforcement-learning-on-Game"
```

### 2. Navigate into the Project Directory

```bash
cd Reinforcement-learning-on-Game
```

### 3. Set Up a Virtual Environment

It's highly recommended to isolate dependencies using a virtual environment.

#### On macOS/Linux:

```bash
python3 -m venv project_env
source project_env/bin/activate
```

#### On Windows:

```bash
python -m venv project_env
.\project_env\Scripts\Activate.ps1
```

### 4. Install Dependencies

Install all required packages using:

```bash
pip install -r requirements.txt
```

If you do not need the project or dependency you can uninstall the required packages using:

```bash
pip uninstall -r requirements.txt
```

---

## 📂 File Descriptions and Usage

### `zombie_shooter.py`

- **Purpose:** Main game loop built with Pygame. Lets a human play the game using the keyboard.
- **Run With:**

```bash
python zombie_shooter.py
```

---

### `zombie_shooter_ql.py`

- **Purpose:** Trains the Q-learning RL agent over a series of episodes (e.g., 5000).
- **Output:** Saves the learned Q-table to `training_data.npz`.

- **Training Mode Toggle:**  
  You can toggle visual training by editing `VISUAL_TRAINING` inside this script:

  - `True`: Watch the agent train (slower)
  - `False`: Headless mode (faster)

- **Run With:**

```bash
python zombie_shooter_ql.py
```

---

### `play_with_agent.py`

- **Purpose:** Loads the trained Q-table and runs the game using the agent's learned policy.
- **Run After Training:**

```bash
python play_with_agent.py
```

---

### `RL_Project_Analysis.ipynb`

- **Purpose:** A Jupyter Notebook for analyzing the agent’s learned strategy using heatmaps, charts, and statistics.
- **Run With:**

```bash
jupyter notebook RL_Project_Analysis.ipynb
```

### `read_npz.py`

- **Purpose:** A python script to view the q_values and epsilon stored in training_data.npz (numpy arrays format)
- **Run With:**

```bash
python read_npz.py
```

---

## 🚀 How to Use the Project

1. **Train the Agent**

   Run the training script to let the agent learn from scratch:

   ```bash
   python q_learning_agent_enhanced.py
   ```

2. **Watch the Agent Play**

   After training, run this to observe the learned behavior:

   ```bash
   python play_with_agent.py
   ```

3. **(Optional) Analyze the Project**

   Use the Jupyter Notebook to visualize and interpret how the agent makes decisions:

   ```bash
   jupyter notebook RL_Project_Analysis.ipynb
   ```

```

---

## ✅ Summary

Through this project, I successfully built and trained a Q-learning agent capable of surviving and scoring in a dynamic zombie environment. From raw pixel movement to action selection and long-term strategy, the agent learned a survivable policy and demonstrated its competence via visualizations and live play.
```
