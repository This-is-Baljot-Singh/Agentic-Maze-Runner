import pygame
import time
import numpy as np
from config import *
from environment import MazeGame, draw_game_state
from agent import QLearningAgent
from utils import a_star_path

def load_assets():
    # Reusing asset loading from main.py
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
    pygame.display.set_caption("Maze Runner - FINAL DEMO")
    clock = pygame.time.Clock()
    
    assets = load_assets()
    game = MazeGame()
    agent = QLearningAgent()
    
    # --- CRITICAL: LOAD BRAIN & DISABLE RANDOMNESS ---
    if not agent.load():
        print(f"Error: Could not find {Q_TABLE_FILENAME}. Run main.py to train first!")
        return
    
    agent.epsilon = 0.0  # 0% Randomness (Pure Intelligence)
    
    num_demos = 5
    print(f"Starting {num_demos} Demo Episodes...")

    for episode in range(1, num_demos + 1):
        game.generate_maze() # New maze every time
        state = game.reset()
        done = False
        
        print(f"--- Demo {episode} ---")
        
        while not done:
            # Check for quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return

            # 1. Agent decides STRATEGY (Go to Key vs Go to Goal)
            action = agent.choose_action(state)
            
            if action == 0 and not game.has_key:
                target = game.key_pos
                strategy = "Target: KEY"
            else:
                target = game.goal_pos
                strategy = "Target: GOAL"

            # 2. Calculate Path (A*)
            path = a_star_path(game.grid, game.agent_pos, target)
            
            if path:
                path_blocked = False
                
                for next_step in path:
                    # Handle Quit mid-walk
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: return
                    
                    # Store positions BEFORE moving to check for "swaps"
                    old_agent_pos = game.agent_pos
                    
                    # 1. Move Agent
                    game.agent_pos = next_step
                    
                    # 2. Check: Did Agent walk DIRECTLY into an Enemy?
                    # (This handles if the agent walks into an enemy that hasn't moved yet)
                    for enemy in game.enemies:
                        if game.agent_pos == enemy.pos:
                            print("   -> Ran into an enemy!")
                            path_blocked = True
                            break
                    if path_blocked: 
                        done = True
                        break

                    # 3. Move Enemies & Check for Tunneling
                    for enemy in game.enemies:
                        old_enemy_pos = enemy.pos
                        enemy.move(game.grid)
                        
                        # Check A: Did Enemy walk onto Agent?
                        if enemy.pos == game.agent_pos:
                            print("   -> Enemy caught Agent!")
                            path_blocked = True
                        
                        # Check B: The "Tunneling" Fix (Swap Detection)
                        # If Agent moved to Enemy's old spot... AND Enemy moved to Agent's old spot
                        if game.agent_pos == old_enemy_pos and enemy.pos == old_agent_pos:
                            print("   -> Head-on collision (Tunneling fixed)!")
                            path_blocked = True

                    if path_blocked:
                        done = True # Game Over (Loss)
                        break # Stop walking the path
                        
                    # Draw Screen
                    screen.fill(GRAY)
                    draw_game_state(screen, game, assets, path)
                    
                    # Draw Text overlay
                    font = pygame.font.Font(None, 36)
                    text = font.render(f"Demo {episode} | {strategy}", True, WHITE)
                    pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT-40, WINDOW_WIDTH, 40))
                    screen.blit(text, (20, WINDOW_HEIGHT-35))
                    
                    pygame.display.flip()
                    time.sleep(0.1) 
                
                # Check Objectives at end of path (only if didn't die)
                if not path_blocked:
                    if game.agent_pos == game.key_pos:
                        game.has_key = True
                        print("   -> Key Collected.")
                        
                    if game.agent_pos == game.goal_pos and game.has_key:
                        print("   -> ESCAPED! (Win)")
                        done = True
                        time.sleep(1) 
            else:
                # No path found (Trapped)
                print("   -> No path found!")
                done = True
            
            # Update State
            state = game.get_state()

    pygame.quit()

if __name__ == "__main__":
    main()