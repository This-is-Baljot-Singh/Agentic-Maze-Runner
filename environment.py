import pygame
import numpy as np
import random
from config import *
from utils import a_star_path, manhattan_distance
from enemy import Enemy

class MazeGame:
    def __init__(self, config=None):
        # Default config if none provided
        self.config = config if config else {
            "enemies": 3, "keys": 1, "traps": 5
        }
        
        self.grid = None
        self.agent_pos = None
        self.start_pos = None
        self.goal_pos = None
        
        # Multiple Keys Support
        self.all_key_positions = [] 
        self.collected_keys = []
        
        self.enemies = []
        self.goal_discovered = False
        
        self.generate_maze()

    @property
    def key_pos(self):
        uncollected = [k for k in self.all_key_positions if k not in self.collected_keys]
        if not uncollected:
            return (-1, -1)
        if self.agent_pos:
            return min(uncollected, key=lambda k: manhattan_distance(self.agent_pos, k))
        return uncollected[0]

    @property
    def has_key(self):
        return len(self.collected_keys) == len(self.all_key_positions)

    @has_key.setter
    def has_key(self, value):
        pass

    def generate_maze(self):
        while True:
            self.grid = np.full((GRID_HEIGHT, GRID_WIDTH), WALL, dtype=int)
            self._recursive_backtracking(1, 1, self.grid)

            path_cells = [(r, c) for r in range(1, GRID_HEIGHT - 1) for c in range(1, GRID_WIDTH - 1) if self.grid[r,c] == EMPTY]
            if len(path_cells) < 50: continue

            # Zoning
            left_zone = [p for p in path_cells if p[1] < GRID_WIDTH // 4]
            right_zone = [p for p in path_cells if p[1] > (GRID_WIDTH * 3) // 4]
            mid_zone = [p for p in path_cells if GRID_WIDTH // 4 <= p[1] <= (GRID_WIDTH * 3) // 4]

            if not left_zone or not right_zone or not mid_zone: continue

            self.start_pos = random.choice(left_zone)
            self.goal_pos = random.choice(right_zone)
            
            # 1. Keys
            self.all_key_positions = []
            self.collected_keys = []
            num_keys = self.config.get("keys", 1)
            
            if len(mid_zone) >= num_keys:
                self.all_key_positions = random.sample(mid_zone, num_keys)
            else: continue 

            # 2. Traps
            placements = {self.start_pos, self.goal_pos} | set(self.all_key_positions)
            trap_candidates = [p for p in path_cells if p not in placements]
            num_traps = self.config.get("traps", 5)
            
            if len(trap_candidates) >= num_traps:
                trap_positions = random.sample(trap_candidates, k=num_traps)
                for pos in trap_positions: self.grid[pos] = TRAP

            # 3. Enemies
            self.enemies = []
            safe_cells = [p for p in path_cells if p not in placements and self.grid[p] != TRAP]
            num_enemies = self.config.get("enemies", 3)
            
            if len(safe_cells) >= num_enemies:
                 for _ in range(num_enemies):
                    self.enemies.append(Enemy(self.grid, safe_cells))

            # Validation
            if not a_star_path(self.grid, self.start_pos, self.goal_pos): continue
            keys_reachable = True
            for k_pos in self.all_key_positions:
                if not a_star_path(self.grid, self.start_pos, k_pos):
                    keys_reachable = False
                    break
            if keys_reachable: break
        
        self.reset()

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

    def reset(self):
        self.agent_pos = self.start_pos
        self.collected_keys = []
        self.goal_discovered = False
        return self.get_state()

    def get_state(self):
        return int(self.has_key) * 2 + int(self.goal_discovered)

# --- IMPORTANT: THIS FUNCTION MUST BE OUTSIDE THE CLASS ---
# (Ensure there are NO spaces/tabs before 'def')
def draw_game_state(screen, game, assets, path=None):
    wall_texture, trap_img, key_img, goal_img = assets
    
    # Draw Grid
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            element = game.grid[r, c]
            if element == WALL:
                if wall_texture: screen.blit(wall_texture, rect)
                else: pygame.draw.rect(screen, BLACK, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
                if element == TRAP:
                    if trap_img: screen.blit(trap_img, rect)
                    else: pygame.draw.rect(screen, RED, rect)

    # Draw Start
    pygame.draw.rect(screen, GRAY, (game.start_pos[1]*CELL_SIZE, game.start_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw Keys
    for k_pos in game.all_key_positions:
        if k_pos not in game.collected_keys:
            k_rect = pygame.Rect(k_pos[1]*CELL_SIZE, k_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if key_img: screen.blit(key_img, k_rect)
            else: pygame.draw.rect(screen, YELLOW, k_rect)

    # Draw Goal
    g_rect = pygame.Rect(game.goal_pos[1]*CELL_SIZE, game.goal_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    if goal_img: screen.blit(goal_img, g_rect)
    else: pygame.draw.rect(screen, GREEN, g_rect)

    # Draw Path
    if path:
        for pos in path:
            pygame.draw.circle(screen, PATH_COLOR, (pos[1]*CELL_SIZE + CELL_SIZE//2, pos[0]*CELL_SIZE + CELL_SIZE//2), 2)

    # Draw Enemies
    for enemy in game.enemies:
        center = (enemy.pos[1]*CELL_SIZE + CELL_SIZE//2, enemy.pos[0]*CELL_SIZE + CELL_SIZE//2)
        pygame.draw.circle(screen, PURPLE, center, CELL_SIZE//2 - 2)

    # Draw Agent
    center_x = game.agent_pos[1] * CELL_SIZE + CELL_SIZE // 2
    center_y = game.agent_pos[0] * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, BLUE, (center_x, center_y), CELL_SIZE // 2 - 2)