import pygame
import numpy as np
import random
import time
import matplotlib.pyplot as plt
from collections import deque
import os
import heapq

# --- Game Configuration ---
GRID_WIDTH = 40
GRID_HEIGHT = 25
CELL_SIZE = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100
FPS = 60

# --- Training Configuration ---
VISUALIZE_TRAINING = False
LOAD_Q_TABLE_IF_EXISTS = True
SAVE_Q_TABLE_ON_EXIT = True
Q_TABLE_FILENAME = "q_table.npy"
NEW_MAZE_FREQUENCY = 50

# --- Colors & Game Elements ---
WHITE=(255,255,255); BLACK=(0,0,0); GREEN=(40,180,99); RED=(231,76,60); BLUE=(52,152,219)
YELLOW=(241,196,15); GRAY=(128,128,128); CYAN=(26,188,156); PATH_COLOR=(220, 220, 220)
EMPTY=0; WALL=1; TRAP=5; KEY=4; GOAL=3

# --- RL Hyperparameters for Strategic Q-Learning ---
TOTAL_EPISODES = 3000
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
EPSILON_START = 1.0
EPSILON_DECAY = 0.999
EPSILON_MIN = 0.05
MAX_STRATEGIC_STEPS = 5

# --- Reward Structure for Strategic Decisions ---
GOAL_REWARD = 100
KEY_REWARD = 20
DEAD_END_PENALTY = -50 
STEP_PENALTY = -1

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_star_path(grid, start, end):
    grid_height, grid_width = grid.shape
    open_set = [(0, start)]; came_from = {}; 
    g_score = { (r,c): float('inf') for r in range(grid_height) for c in range(grid_width) }
    g_score[start] = 0
    f_score = { (r,c): float('inf') for r in range(grid_height) for c in range(grid_width) }
    f_score[start] = manhattan_distance(start, end)
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            path = [];
            while current in came_from: path.append(current); current = came_from[current]
            return path[::-1]
        
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            if 0 <= neighbor[0] < grid_height and 0 <= neighbor[1] < grid_width and grid[neighbor[0], neighbor[1]] not in [WALL, TRAP]:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current; g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, end)
                    if neighbor not in [i[1] for i in open_set]: heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None

class MazeGame:
    def __init__(self):
        self.grid = None; self.agent_pos = None; self.start_pos = None
        self.key_pos = None; self.goal_pos = None; self.has_key = False
        self.goal_discovered = False
        self.generate_maze()

    def _recursive_backtracking(self, r, c, grid):
        grid_height, grid_width = grid.shape
        grid[r, c] = EMPTY
        neighbors = [(r-2, c), (r+2, c), (r, c-2), (r, c+2)]
        random.shuffle(neighbors)
        for nr, nc in neighbors:
            if 0 < nr < grid_height - 1 and 0 < nc < grid_width - 1 and grid[nr, nc] == WALL:
                wall_r, wall_c = (r + nr) // 2, (c + nc) // 2
                grid[wall_r, wall_c] = EMPTY
                self._recursive_backtracking(nr, nc, grid)

    def generate_maze(self):
        while True:
            self.grid = np.full((GRID_HEIGHT, GRID_WIDTH), WALL, dtype=int)
            start_r, start_c = random.randint(1, GRID_HEIGHT - 2), random.randint(1, GRID_WIDTH - 2)
            if start_r % 2 == 0: start_r = max(1, start_r - 1)
            if start_c % 2 == 0: start_c = max(1, start_c - 1)
            self._recursive_backtracking(start_r, start_c, self.grid)

            path_cells = [(r, c) for r in range(1, GRID_HEIGHT - 1) for c in range(1, GRID_WIDTH - 1) if self.grid[r,c] == EMPTY]
            if len(path_cells) < (GRID_WIDTH * GRID_HEIGHT) // 4: continue

            left_zone = [p for p in path_cells if p[1] < GRID_WIDTH // 4]
            right_zone = [p for p in path_cells if p[1] > (GRID_WIDTH * 3) // 4]
            middle_zone = [p for p in path_cells if GRID_WIDTH // 4 <= p[1] <= (GRID_WIDTH * 3) // 4]

            if not left_zone or not right_zone or not middle_zone: continue

            self.start_pos = random.choice(left_zone)
            self.goal_pos = random.choice(right_zone)
            self.key_pos = random.choice(middle_zone)
            
            placements = {self.start_pos, self.key_pos, self.goal_pos}
            
            trap_candidates = [p for p in path_cells if p not in placements]
            num_traps = 5
            if len(trap_candidates) < num_traps: continue
            
            trap_positions = random.sample(trap_candidates, k=num_traps)
            for pos in trap_positions: self.grid[pos] = TRAP

            if a_star_path(self.grid, self.start_pos, self.key_pos) and a_star_path(self.grid, self.key_pos, self.goal_pos):
                break
        self.reset()

    def reset(self):
        self.agent_pos = self.start_pos; self.has_key = False; self.goal_discovered = False
        return self.get_state()

    def get_state(self):
        return int(self.has_key) * 2 + int(self.goal_discovered)

class QLearningAgent:
    def __init__(self):
        self.q_table = np.zeros((4, 2))
        self.lr=LEARNING_RATE; self.gamma=DISCOUNT_FACTOR; self.epsilon=EPSILON_START

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon: return random.randrange(2)
        return np.argmax(self.q_table[state, :])

    def learn(self, state, action, reward, next_state):
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state, :])
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_value

    def decay_epsilon(self):
        if self.epsilon > EPSILON_MIN: self.epsilon *= EPSILON_DECAY
        
    def save(self): 
        np.save(Q_TABLE_FILENAME, self.q_table)
        print(f"Q-table saved to {Q_TABLE_FILENAME}")
        
    def load(self): 
        self.q_table = np.load(Q_TABLE_FILENAME)
        print(f"Q-table loaded from {Q_TABLE_FILENAME}")

# --- Drawing and Plotting ---
def draw_grid(screen, game, wall_texture, trap_img, key_img, goal_img):
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            rect=pygame.Rect(c*CELL_SIZE,r*CELL_SIZE,CELL_SIZE,CELL_SIZE)
            element = game.grid[r, c]
            if element == WALL:
                if wall_texture:
                    screen.blit(wall_texture, rect)
                else:
                    pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
                if element == TRAP:
                    if trap_img: screen.blit(trap_img, rect)
                    else: pygame.draw.rect(screen, RED, rect)

    start_rect = pygame.Rect(game.start_pos[1]*CELL_SIZE, game.start_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, GRAY, start_rect)
    
    if not game.has_key:
        key_rect = pygame.Rect(game.key_pos[1]*CELL_SIZE, game.key_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if key_img: screen.blit(key_img, key_rect)
        else: pygame.draw.rect(screen, YELLOW, key_rect)

    goal_rect = pygame.Rect(game.goal_pos[1]*CELL_SIZE, game.goal_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    if goal_img: screen.blit(goal_img, goal_rect)
    else: pygame.draw.rect(screen, GREEN, goal_rect)

def draw_agent_path(screen, path):
    if path:
        for pos in path:
            pygame.draw.circle(screen, PATH_COLOR, (pos[1]*CELL_SIZE + CELL_SIZE//2, pos[0]*CELL_SIZE + CELL_SIZE//2), 2)

def draw_agent(screen, agent_pos, has_key):
    center_x = agent_pos[1] * CELL_SIZE + CELL_SIZE // 2
    center_y = agent_pos[0] * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - 2
    pygame.draw.circle(screen, BLUE, (center_x, center_y), radius)
    if has_key:
        pygame.draw.circle(screen, CYAN, (center_x, center_y), radius - 3)

def draw_info(screen, episode_text, epsilon, win_rate, current_strategy):
    font=pygame.font.Font(None, 24); pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT-100, WINDOW_WIDTH, 100))
    texts = [f"Ep: {episode_text}", f"Epsilon: {epsilon:.3f}", f"Win Rate: {win_rate:.1f}%", f"Strategy: {current_strategy}"]
    for i, text in enumerate(texts):
        surf=font.render(text, True, WHITE); screen.blit(surf, (10 + i * (WINDOW_WIDTH/4), WINDOW_HEIGHT - 65))

def plot_metrics(win_rates):
    plt.figure(figsize=(12, 6)); plt.plot(win_rates, label='Win Rate (100-episode moving average)')
    plt.title('Agent Performance Over Training'); plt.xlabel('Episode'); plt.ylabel('Win Rate (%)')
    plt.ylim(0, 100); plt.grid(True); plt.legend(); plt.show()

def main():
    pygame.init(); screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A* Navigation with Q-Learning Strategy (Final Version)"); clock = pygame.time.Clock()
    
    try:
        wall_texture = pygame.image.load("Assets/Brick_Wall.png").convert()
        wall_texture = pygame.transform.scale(wall_texture, (CELL_SIZE, CELL_SIZE))
    except pygame.error:
        print("Falling back to solid color walls."); wall_texture = None

    try:
        trap_img = pygame.image.load("Assets/trap.png").convert_alpha()
        trap_img = pygame.transform.scale(trap_img, (CELL_SIZE, CELL_SIZE))
        key_img = pygame.image.load("Assets/key.png").convert_alpha()
        key_img = pygame.transform.scale(key_img, (CELL_SIZE, CELL_SIZE))
        goal_img = pygame.image.load("Assets/goal.png").convert_alpha()
        goal_img = pygame.transform.scale(goal_img, (CELL_SIZE, CELL_SIZE))
    except pygame.error:
        print("Falling back to solid colors for items/traps."); trap_img, key_img, goal_img = None, None, None

    game = MazeGame(); agent = QLearningAgent()
    win_rate_history=[]; recent_wins=deque(maxlen=100); final_win_rate = 0.0

    if LOAD_Q_TABLE_IF_EXISTS and os.path.exists(Q_TABLE_FILENAME):
        agent.load(); agent.epsilon = 0; final_win_rate = 100.0
    else:
        print("Starting training for strategic agent...")
        running = True
        for episode in range(1, TOTAL_EPISODES + 1):
            if not running: break
            
            if (episode - 1) % NEW_MAZE_FREQUENCY == 0:
                game.generate_maze()

            state = game.reset(); done = False; is_win = False; strategic_steps = 0
            
            current_path = None # To hold the path for visualization
            
            while not done and strategic_steps < MAX_STRATEGIC_STEPS:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: running = False
                if not running: break

                action = agent.choose_action(state)
                strategy = "GO FOR KEY" if action == 0 and not game.has_key else "GO FOR GOAL"
                target_pos = game.key_pos if action == 0 and not game.has_key else game.goal_pos
                path = a_star_path(game.grid, game.agent_pos, target_pos)
                
                if VISUALIZE_TRAINING:
                    current_path = path
                    screen.fill(GRAY)
                    draw_grid(screen, game, wall_texture, trap_img, key_img, goal_img)
                    draw_agent_path(screen, current_path)
                    draw_agent(screen, game.agent_pos, game.has_key)
                    win_rate = sum(recent_wins)
                    draw_info(screen, f"{episode}/{TOTAL_EPISODES}", agent.epsilon, win_rate, strategy)
                    pygame.display.flip()
                    time.sleep(0.2) # Slow down visualization

                path_reward = 0
                if path:
                    path_reward += len(path) * STEP_PENALTY
                    game.agent_pos = path[-1]
                    if game.agent_pos == game.key_pos:
                        game.has_key = True; path_reward += KEY_REWARD
                    if game.agent_pos == game.goal_pos:
                        game.goal_discovered = True
                    if game.agent_pos == game.goal_pos and game.has_key:
                        path_reward += GOAL_REWARD; is_win = True; done = True
                else:
                    path_reward += DEAD_END_PENALTY; done = True

                next_state = game.get_state()
                agent.learn(state, action, path_reward, next_state)
                state = next_state; strategic_steps += 1
            
            recent_wins.append(1 if is_win else 0); agent.decay_epsilon()
            
            if episode % 100 == 0:
                win_rate = sum(recent_wins); win_rate_history.append(win_rate)
                print(f"Episode {episode} | Win Rate (last 100): {win_rate:.1f}% | Epsilon: {agent.epsilon:.3f}")

        final_win_rate = sum(recent_wins)
        if SAVE_Q_TABLE_ON_EXIT and running: agent.save()
        if win_rate_history: plot_metrics(win_rate_history)

    # Demonstration
    print("\n--- Demonstrating Trained Agent ---")
    running = True; demo_count = 0
    while demo_count < 5 and running:
        game.generate_maze(); state = game.reset(); done = False
        
        while not done and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

            state = game.get_state(); action = agent.choose_action(state)
            strategy = "GO FOR KEY" if action == 0 and not game.has_key else "GO FOR GOAL"
            target_pos = game.key_pos if strategy == "GO FOR KEY" else game.goal_pos
            path = a_star_path(game.grid, game.agent_pos, target_pos)
            
            if path:
                for pos in path:
                    if not running: break
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: running = False
                    
                    game.agent_pos = pos
                    screen.fill(GRAY); draw_grid(screen, game, wall_texture, trap_img, key_img, goal_img); draw_agent_path(screen, path)
                    draw_agent(screen, game.agent_pos, game.has_key)
                    draw_info(screen, f"DEMO {demo_count+1}", 0, final_win_rate, strategy)
                    pygame.display.flip(); time.sleep(0.05)
                
                if game.agent_pos == game.key_pos: game.has_key = True
                if game.agent_pos == game.goal_pos: game.goal_discovered = True
            else:
                print("No safe path found for strategy:", strategy); break

            if game.agent_pos == game.goal_pos and game.has_key: done = True
        
        demo_count += 1
        if running: time.sleep(1)
        
    pygame.quit()

if __name__ == "__main__":
    main()

