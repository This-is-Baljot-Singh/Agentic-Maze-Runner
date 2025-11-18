# main.py
import pygame
import time
import matplotlib.pyplot as plt
from collections import deque

from config import *
from environment import MazeGame, draw_game_state
from agent import QLearningAgent
from utils import a_star_path

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

def draw_dashboard(screen, episode_text, epsilon, win_rate, strategy):
    font = pygame.font.Font(None, 24)
    pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT-100, WINDOW_WIDTH, 100))
    texts = [f"Ep: {episode_text}", f"Epsilon: {epsilon:.3f}", f"Win Rate: {win_rate:.1f}%", f"Strategy: {strategy}"]
    for i, text in enumerate(texts):
        surf = font.render(text, True, WHITE)
        screen.blit(surf, (10 + i * (WINDOW_WIDTH/4), WINDOW_HEIGHT - 65))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AI Maze Runner - Project Refactored")
    clock = pygame.time.Clock()
    
    assets = load_assets()
    game = MazeGame()
    agent = QLearningAgent()
    
    win_rates = []
    recent_wins = deque(maxlen=100)

    # --- TRAINING LOOP ---
    if LOAD_Q_TABLE_IF_EXISTS:
        if agent.load(): agent.epsilon = 0

    print("Starting Training...")
    running = True
    for episode in range(1, TOTAL_EPISODES + 1):
        if not running: break
        
        if (episode - 1) % NEW_MAZE_FREQUENCY == 0:
            game.generate_maze()

        state = game.reset()
        done = False
        steps = 0
        is_win = False
        
        while not done and steps < MAX_STRATEGIC_STEPS:
            for enemy in game.enemies:
                enemy.move(game.grid)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
            
            action = agent.choose_action(state)
            
            # Decode Strategy for Visualization
            if action == 0 and not game.has_key:
                target = game.key_pos
                strategy_name = "SEEK KEY"
            else:
                target = game.goal_pos
                strategy_name = "SEEK GOAL"

            # Execute Movement (A* layer)
            path = a_star_path(game.grid, game.agent_pos, target)
            step_count_in_path = 0
            path_interrupted = False
            
            # Visualization
            if VISUALIZE_TRAINING:
                screen.fill(GRAY)
                draw_game_state(screen, game, assets, path)
                draw_dashboard(screen, f"{episode}", agent.epsilon, sum(recent_wins), strategy_name)
                pygame.display.flip()
                # time.sleep(0.05) # Uncomment to slow down

            # Calculate Reward
            reward = 0
            if path:
                # SIMULATE WALKING THE PATH STEP-BY-STEP
                for next_step in path:
                    
                    # 1. Move Agent
                    game.agent_pos = next_step
                    step_count_in_path += 1
                    
                    # 2. Move Enemies
                    for enemy in game.enemies:
                        enemy.move(game.grid)

                    # 3. Check Collision
                    enemy_positions = [e.pos for e in game.enemies]
                    if game.agent_pos in enemy_positions:
                        reward += ENEMY_PENALTY
                        path_interrupted = True
                        done = True # Game Over
                        break # Stop moving

                    # 4. Visualization (Optional: Update screen every step to see the chase)
                    if VISUALIZE_TRAINING:
                        screen.fill(GRAY)
                        draw_game_state(screen, game, assets, path)
                        # ... draw dashboard ...
                        pygame.display.flip()
                        # time.sleep(0.02) # Tiny delay to see movement

                # END OF PATH LOOP
                
                if not path_interrupted:
                    reward += step_count_in_path * STEP_PENALTY
                    
                    # Check Key/Goal logic (Existing logic)
                    if game.agent_pos == game.key_pos:
                        game.has_key = True
                        reward += KEY_REWARD
                    
                    if game.agent_pos == game.goal_pos and game.has_key:
                        game.goal_discovered = True
                        reward += GOAL_REWARD
                        is_win = True
                        done = True
            else:
                reward += DEAD_END_PENALTY
                done = True

            next_state = game.get_state()
            agent.learn(state, action, reward, next_state)
            state = next_state
            steps += 1

        recent_wins.append(1 if is_win else 0)
        agent.decay_epsilon()

        if episode % 100 == 0:
            current_win_rate = sum(recent_wins)
            win_rates.append(current_win_rate)
            print(f"Episode {episode} | Win Rate: {current_win_rate}% | Epsilon: {agent.epsilon:.2f}")

    if SAVE_Q_TABLE_ON_EXIT:
        agent.save()
    
    plt.plot(win_rates)
    plt.title("Training Performance")
    plt.show()
    pygame.quit()

if __name__ == "__main__":
    main()