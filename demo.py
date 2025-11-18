import pygame
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import *
from environment import MazeGame, draw_game_state
from agent import QLearningAgent
from utils import a_star_path

# --- NEW: Heatmap Class ---
class HeatmapVisualizer:
    def __init__(self, grid_height, grid_width):
        self.height = grid_height
        self.width = grid_width
        self.death_map = np.zeros((grid_height, grid_width))
        self.visit_map = np.zeros((grid_height, grid_width))

    def record_death(self, pos):
        self.death_map[pos] += 1

    def record_visit(self, pos):
        self.visit_map[pos] += 1

    def show_heatmap(self):
        print("Generating Heatmap...")
        plt.figure(figsize=(10, 5))
        
        # Plot 1: Death Heatmap
        plt.subplot(1, 2, 1)
        sns.heatmap(self.death_map, cmap="Reds", cbar=True, linewidths=0.1, linecolor='gray')
        plt.title("Agent Death Zones (Risk Analysis)")
        plt.xlabel("Grid X"); plt.ylabel("Grid Y")

        # Plot 2: Traversal Heatmap (Where did it walk?)
        plt.subplot(1, 2, 2)
        sns.heatmap(self.visit_map, cmap="Blues", cbar=True, linewidths=0.1, linecolor='gray')
        plt.title("Agent Traversal Patterns")
        plt.xlabel("Grid X"); plt.ylabel("Grid Y")

        plt.tight_layout()
        plt.show()

def load_assets():
    try:
        wall = pygame.image.load("assets/Brick_Wall.png").convert()
        wall = pygame.transform.scale(wall, (CELL_SIZE, CELL_SIZE))
    except: wall = None
    
    def load_icon(name):
        try:
            img = pygame.image.load(f"assets/{name}.png").convert_alpha()
            return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except: return None

    return wall, load_icon("trap"), load_icon("key"), load_icon("goal")

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze Runner - FINAL DEMO + ANALYTICS")
    
    assets = load_assets()
    game = MazeGame()
    agent = QLearningAgent()
    
    # Initialize Heatmap Tracker
    analyzer = HeatmapVisualizer(GRID_HEIGHT, GRID_WIDTH)

    if not agent.load():
        print(f"Error: Could not find {Q_TABLE_FILENAME}. Run main.py to train first!")
        return
    
    agent.epsilon = 0.0 
    
    # INCREASE DEMO COUNT FOR BETTER DATA
    num_demos = 10 
    print(f"Starting {num_demos} Demo Episodes for Data Collection...")

    for episode in range(1, num_demos + 1):
        game.generate_maze()
        state = game.reset()
        done = False
        
        print(f"--- Demo {episode} ---")
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return

            action = agent.choose_action(state)
            target = game.key_pos if (action == 0 and not game.has_key) else game.goal_pos
            strategy = "Target: KEY" if target == game.key_pos else "Target: GOAL"

            path = a_star_path(game.grid, game.agent_pos, target)
            
            if path:
                path_blocked = False
                for next_step in path:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: return
                    
                    # --- ANALYTICS: Record Step ---
                    analyzer.record_visit(next_step)
                    
                    old_agent_pos = game.agent_pos
                    game.agent_pos = next_step
                    
                    # Check pre-move collision
                    for enemy in game.enemies:
                        if game.agent_pos == enemy.pos:
                            print("   -> Ran into an enemy!")
                            analyzer.record_death(game.agent_pos) # RECORD DEATH
                            path_blocked = True
                            break
                    if path_blocked: 
                        done = True; break

                    # Move Enemies
                    for enemy in game.enemies:
                        old_enemy_pos = enemy.pos
                        enemy.move(game.grid)
                        
                        if enemy.pos == game.agent_pos:
                            print("   -> Enemy caught Agent!")
                            analyzer.record_death(game.agent_pos) # RECORD DEATH
                            path_blocked = True
                        
                        if game.agent_pos == old_enemy_pos and enemy.pos == old_agent_pos:
                            print("   -> Head-on collision!")
                            analyzer.record_death(game.agent_pos) # RECORD DEATH
                            path_blocked = True

                    if path_blocked:
                        done = True; break
                        
                    # Visualization (Faster speed for data collection)
                    screen.fill(GRAY)
                    draw_game_state(screen, game, assets, path)
                    pygame.display.flip()
                    # time.sleep(0.05) # Reduced sleep for faster data collection
                
                if not path_blocked:
                    if game.agent_pos == game.key_pos: game.has_key = True
                    if game.agent_pos == game.goal_pos and game.has_key:
                        print("   -> ESCAPED! (Win)")
                        done = True
            else:
                print("   -> No path found!")
                done = True
            
            state = game.get_state()
    
    pygame.quit()
    
    # --- SHOW THE ANALYTICS ---
    analyzer.show_heatmap()

if __name__ == "__main__":
    main()