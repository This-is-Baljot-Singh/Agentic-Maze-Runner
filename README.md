# Agentic Maze Runner: AI Navigation Simulation

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pygame](https://img.shields.io/badge/Library-Pygame-yellow)
![AI](https://img.shields.io/badge/AI-Q--Learning%20%2B%20A*-orange)
![License](https://shields.fly.dev/badge/license-MIT-green)

An advanced pathfinding simulation combining **Reinforcement Learning (Q-Learning)** with **Heuristic Search (A*)** to navigate dynamic, procedurally generated mazes. This project demonstrates how a hybrid AI architecture can solve complex navigation tasks involving multiple objectives, static traps, and dynamic adversaries.

![Project Screenshot](assets/Config%20UI.png) 

## 🌟 Features

### 🧠 Hybrid AI Architecture
* **Strategic Layer (Q-Learning):** High-level decision making (e.g., "Should I go for the key or the goal?").
* **Tactical Layer (A* Pathfinding):** Optimal path generation between objectives.
* **Reactive Layer (Heuristic):** Real-time collision avoidance to dodge dynamic enemies.

### 🎮 Dynamic Environment
* **Procedural Generation:** Every run features a unique maze layout using Recursive Backtracking.
* **Dynamic Enemies:** Smart patrol agents that wander the maze and hunt the player.
* **Multiple Objectives:** Configurable number of keys required to unlock the exit.
* **Hazards:** Static traps and walls to navigate around.

### 📊 Analytics & UI
* **Cyber-Themed UI:** A polished, modern configuration menu to tweak simulation parameters.
* **Heatmap Visualization:** Post-run analytics showing agent death zones and traversal density using `matplotlib` and `seaborn`.
* **Real-time Dashboard:** Tracks wins, losses, and current strategies during gameplay.

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/Agentic-Maze-Runner.git](https://github.com/yourusername/Agentic-Maze-Runner.git)
    cd Agentic-Maze-Runner
    ```

2.  **Install dependencies**
    ```bash
    pip install pygame numpy matplotlib seaborn
    ```

3.  **Run the Simulation**
    ```bash
    python main_app.py
    ```

> **Note:** If you want to retrain the agent from scratch, delete the `q_table.npy` file and run `main.py` (the training script) before running `main_app.py`.

## 📂 Project Structure

```text
Agentic-Maze-Runner/
│
├── main_app.py      # Entry point: UI, Game Loop, and Visualization
├── main.py          # Training script for the Q-Learning Agent
├── environment.py   # Maze generation, game state, and rendering logic
├── agent.py         # Q-Learning logic (Table updates, Epsilon-Greedy)
├── enemy.py         # Enemy patrol AI and movement logic
├── config.py        # Global constants (Hyperparameters, Colors, Settings)
├── ui.py            # Modern UI classes (Menu, Buttons, Selectors)
├── utils.py         # Math helpers (A*, Manhattan Distance)
├── assets/          # Images (Wall, Key, Trap, Goal textures)
└── q_table.npy      # Pre-trained Q-Table model
