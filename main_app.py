import pygame
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import *
from environment import MazeGame, draw_game_state
from agent import QLearningAgent
from utils import a_star_path
from ui import StartMenu, Button

# --- HEATMAP CLASS ---
class HeatmapVisualizer:
    def __init__(self, grid_height, grid_width):
        self.height = grid_height; self.width = grid_width
        self.death_map = np.zeros((grid_height, grid_width))
        self.visit_map = np.zeros((grid_height, grid_width))

    def record_death(self, pos): self.death_map[pos] += 1
    def record_visit(self, pos): self.visit_map[pos] += 1
    def show_heatmap(self):
        print("Generating Heatmap...")
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        sns.heatmap(self.death_map, cmap="Reds", cbar=True, linewidths=0.1, linecolor='gray')
        plt.title("Agent Death Zones (Risk Analysis)")
        plt.subplot(1, 2, 2)
        sns.heatmap(self.visit_map, cmap="Blues", cbar=True, linewidths=0.1, linecolor='gray')
        plt.title("Agent Traversal Patterns")
        plt.tight_layout(); plt.show()

# --- ASSET LOADER ---
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

def is_safe(target_pos, enemies):
    for enemy in enemies:
        if abs(target_pos[0] - enemy.pos[0]) + abs(target_pos[1] - enemy.pos[1]) <= 2:
            return False
    return True

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze Runner Ultimate")
    clock = pygame.time.Clock()
    
    # --- MENU ---
    menu = StartMenu()
    game_config = menu.run(screen)
    if not game_config: pygame.quit(); return

    # Config extraction
    TOTAL_RUNS = game_config['runs']
    SHOW_HEATMAPS = game_config['heatmaps']
    SPEED_MODIFIER = 0.2 - (game_config['speed'] * 0.015)
    if SPEED_MODIFIER < 0: SPEED_MODIFIER = 0
    
    assets = load_assets()
    game = MazeGame(game_config)
    agent = QLearningAgent()
    if not agent.load(): print("Please train first!"); return
    agent.epsilon = 0.0
    
    # --- ANALYTICS & STATS ---
    analyzer = HeatmapVisualizer(GRID_HEIGHT, GRID_WIDTH) if SHOW_HEATMAPS else None
    wins = 0
    losses = 0
    
    pause_btn = Button(WINDOW_WIDTH - 120, WINDOW_HEIGHT - 80, 100, 40, "PAUSE")
    is_paused = False

    for episode in range(1, TOTAL_RUNS + 1):
        game.generate_maze()
        state = game.reset()
        done = False
        
        while not done:
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                     if pause_btn.rect.collidepoint(event.pos):
                         is_paused = not is_paused
                         pause_btn.text = "PLAY" if is_paused else "PAUSE"

            if is_paused:
                font = pygame.font.Font(None, 64)
                txt = font.render("PAUSED", True, YELLOW)
                screen.blit(txt, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
                pause_btn.draw(screen, pygame.font.Font(None, 24))
                pygame.display.flip(); clock.tick(10); continue 

            # Agent Logic
            action = agent.choose_action(state)
            if not game.has_key:
                target = game.key_pos
                strategy = f"Target: KEY ({len(game.collected_keys)}/{len(game.all_key_positions)})"
            else:
                target = game.goal_pos
                strategy = "Target: GOAL"

            path = a_star_path(game.grid, game.agent_pos, target)
            
            if path:
                path_blocked = False
                step_idx = 0
                
                while step_idx < len(path):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: return
                        if event.type == pygame.MOUSEBUTTONDOWN:
                             if pause_btn.rect.collidepoint(event.pos):
                                 is_paused = not is_paused
                                 pause_btn.text = "PLAY" if is_paused else "PAUSE"
                    
                    if is_paused:
                        font = pygame.font.Font(None, 64); txt = font.render("PAUSED", True, YELLOW)
                        screen.blit(txt, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
                        pause_btn.draw(screen, pygame.font.Font(None, 24)); pygame.display.flip(); time.sleep(0.1); continue

                    # Movement
                    next_step = path[step_idx]
                    should_wait = False
                    if not is_safe(next_step, game.enemies): should_wait = True
                    old_agent_pos = game.agent_pos
                    
                    if not should_wait:
                        game.agent_pos = next_step
                        if analyzer: analyzer.record_visit(game.agent_pos) # Analytics
                        
                        if game.agent_pos in game.all_key_positions and game.agent_pos not in game.collected_keys:
                            game.collected_keys.append(game.agent_pos)
                        step_idx += 1
                    
                    # Enemy Update
                    for enemy in game.enemies:
                        old_enemy = enemy.pos
                        enemy.move(game.grid)
                        
                        # Check Collision
                        collision = False
                        if enemy.pos == game.agent_pos: collision = True
                        if not should_wait and game.agent_pos == old_enemy and enemy.pos == old_agent_pos: collision = True
                        
                        if collision:
                            path_blocked = True
                            if analyzer: analyzer.record_death(game.agent_pos) # Analytics
                    
                    if path_blocked: done = True; break
                    
                    # Drawing
                    screen.fill(GRAY)
                    draw_game_state(screen, game, assets, path)
                    
                    # UI / Dashboard
                    pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT-100, WINDOW_WIDTH, 100))
                    font = pygame.font.Font(None, 28)
                    
                    # Column 1: Run Info
                    screen.blit(font.render(f"Run: {episode}/{TOTAL_RUNS}", True, WHITE), (20, WINDOW_HEIGHT - 85))
                    screen.blit(font.render(strategy, True, WHITE), (20, WINDOW_HEIGHT - 60))
                    
                    # Column 2: Stats (Wins/Losses)
                    screen.blit(font.render(f"WINS: {wins}", True, GREEN), (300, WINDOW_HEIGHT - 85))
                    screen.blit(font.render(f"LOSSES: {losses}", True, RED), (300, WINDOW_HEIGHT - 60))
                    
                    # Column 3: Keys
                    screen.blit(font.render(f"Keys Found: {len(game.collected_keys)}", True, YELLOW), (500, WINDOW_HEIGHT - 85))

                    pause_btn.draw(screen, pygame.font.Font(None, 24))
                    
                    if should_wait:
                        pygame.draw.circle(screen, (255, 165, 0), 
                            (game.agent_pos[1]*CELL_SIZE+10, game.agent_pos[0]*CELL_SIZE+10), 20, 2)

                    pygame.display.flip()
                    time.sleep(SPEED_MODIFIER if not should_wait else 0.2)
                
                if not path_blocked:
                    if game.has_key and game.agent_pos == game.goal_pos:
                        print("WIN!")
                        wins += 1
                        done = True
                    elif path_blocked: # Should have been caught above, but double check
                        losses += 1
                        done = True
                else:
                    print("Loss: Died to enemy.")
                    losses += 1
                    done = True
            else:
                print("Loss: No path.")
                losses += 1
                done = True
                
            state = game.get_state()

    pygame.quit()
    
    # Show Heatmaps if enabled
    if analyzer and SHOW_HEATMAPS:
        analyzer.show_heatmap()

if __name__ == "__main__":
    main()