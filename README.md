# **Agentic Maze Runner: A Strategic AI with A\* Navigation**

## **1\. Project Overview**

This project presents a sophisticated AI agent that learns to solve complex, procedurally generated mazes. The agent's objective is to find a key and then navigate to a goal, all while avoiding traps and finding the most efficient path possible.

This implementation utilizes a powerful **hybrid AI model** that separates high-level strategic planning from low-level tactical navigation. A **Q-learning algorithm** is trained to make strategic decisions, while the *A search algorithm*\* is used to execute those decisions by finding the optimal, trap-free path. This architecture creates a highly intelligent and reliable agent capable of solving intricate challenges.

## **2\. Key Features**

* **Advanced Maze Generation:** Mazes are generated using a **Recursive Backtracking algorithm**, creating complex, aesthetically pleasing corridors and dead ends similar to classic maze designs. The generation is zoned, ensuring the start is always on the left, the goal on the right, and the key in the middle.  
* **Strategic Q-Learner:** Instead of learning to move step-by-step, the Q-learning agent is trained to make high-level strategic choices:  
  1. **Go for the Key**  
  2. Go for the Goal  
     Its decisions are based on a simple but powerful state: (has\_key, goal\_discovered).  
* \**Optimal A* Navigation:\*\* Once the agent chooses a strategy, the A\* pathfinding algorithm takes over. It calculates the **shortest possible path** to the target (key or goal) that **completely avoids traps**. This guarantees efficient and safe movement, eliminating any possibility of the agent getting stuck or wandering.  
* **Intelligent Memory & Backtracking:** The agent has a memory of whether it has seen the goal. If it discovers the goal before finding the key, the Q-learner is trained to understand that the correct strategy is to go back for the key and then return to the remembered goal location.  
* **Custom Visuals:** The game uses custom sprites for the key, goal, and traps, along with a brick texture for the walls, creating an engaging and polished visual experience.

## **3\. How to Run the Project**

### **Prerequisites**

You must have Python and the following libraries installed:

* pygame: For the game engine and graphics.  
* numpy: For efficient data structures.  
* matplotlib: For plotting the training performance.

You can install them using pip:

pip install pygame numpy matplotlib

### **File Setup**

1. Place the maze\_runner.py script in a directory.  
2. Place the following image files in the **Assets directory**:  
   * Brick\_Wall.png (for the walls)  
   * trap.png (the traps)  
   * key.png (the key)  
   * goal.png (the goal)

*The code will gracefully fall back to solid colors if the images are not found.*

### **Execution**

Run the script from your terminal:

python maze\_runner.py

* **Training:** The agent will begin training automatically if a saved q\_table.npy file is not found. The training process is fast and runs in the background. Progress will be printed to the console.  
* **Demonstration:** After training (or if a saved file is loaded), a Pygame window will open, and the agent will demonstrate its learned strategy by solving 5 new, randomly generated mazes.

## **4\. Methodology Analysis**

The success of this agent lies in its **hierarchical learning structure**. By separating the problem into two distinct layers, we allow each component to do what it does best:

* **The Q-Learner (The "Brain"):** Focuses only on the grand strategy. With just four possible states, it can quickly and reliably learn the optimal policy (e.g., "if I don't have the key, going for it has the highest long-term reward").  
* \**The A* Algorithm (The "Legs"):\*\* Acts as a perfect navigator. It is given a simple command ("go to the key") and executes it with flawless efficiency, handling all the complex calculations of pathfinding and trap avoidance.

This model avoids the pitfalls of earlier versions where a single, monolithic Q-learner was overwhelmed by the massive number of possible navigational states. This separation of concerns is a key concept in advanced robotics and AI design.

## **5\. Real-World Connections**

This project serves as an excellent educational tool and a practical demonstration of several key AI concepts:

* **Hierarchical Reinforcement Learning:** The agent's two-layer structure is a simplified model of how complex AI systems are built. For example, a self-driving car might have a strategic layer that decides to "change lanes" and a tactical layer that handles the precise steering and acceleration.  
* **Optimal Pathfinding:** The A\* algorithm is a cornerstone of logistics, robotics, and video game AI, used for everything from NPC navigation to planning routes for delivery drones.  
* **Machine Learning in Game AI:** This project shows how AI can be used to create dynamic and intelligent opponents that can adapt to ever-changing environments, providing a much more compelling experience than statically scripted enemies.
