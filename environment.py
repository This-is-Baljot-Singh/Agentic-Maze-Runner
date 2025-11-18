# environment.py
import pygame
import numpy as np
import random
from config import *
from utils import a_star_path
from enemy import Enemy

class MazeGame:
    def __init__(self):
        self.grid = None; self.agent_pos = None; self.start_pos = None
        self.key_pos = None; self.goal_pos = None; self.has_key = False
        self.goal_discovered = False
        self.enemies = []
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

            # Get empty cells
            path_cells = [(r, c) for r in range(1, GRID_HEIGHT - 1) for c in range(1, GRID_WIDTH - 1) if self.grid[r,c] == EMPTY]
            if len(path_cells) < (GRID_WIDTH * GRID_HEIGHT) // 4: continue

            # Zoning for difficulty
            left_zone = [p for p in path_cells if p[1] < GRID_WIDTH // 4]
            right_zone = [p for p in path_cells if p[1] > (GRID_WIDTH * 3) // 4]
            middle_zone = [p for p in path_cells if GRID_WIDTH // 4 <= p[1] <= (GRID_WIDTH * 3) // 4]

            if not left_zone or not right_zone or not middle_zone: continue

            self.start_pos = random.choice(left_zone)
            self.goal_pos = random.choice(right_zone)
            self.key_pos = random.choice(middle_zone)
            
            # Place Traps
            placements = {self.start_pos, self.key_pos, self.goal_pos}
            trap_candidates = [p for p in path_cells if p not in placements]
            
            if len(trap_candidates) >= 5:
                trap_positions = random.sample(trap_candidates, k=5)
                for pos in trap_positions: self.grid[pos] = TRAP
            
            self.enemies = []
            # Get all safe spots (excluding start/goal/key/traps)
            safe_cells = [p for p in path_cells if p not in placements and self.grid[p] != TRAP]
            
            if len(safe_cells) > NUM_ENEMIES:
                for _ in range(NUM_ENEMIES):
                    enemy = Enemy(self.grid, safe_cells)
                    self.enemies.append(enemy)

            # Solvability Check
            if a_star_path(self.grid, self.start_pos, self.key_pos) and a_star_path(self.grid, self.key_pos, self.goal_pos):
                break
        self.reset()

    def reset(self):
        self.agent_pos = self.start_pos; self.has_key = False; self.goal_discovered = False
        return self.get_state()

    def get_state(self):
        return int(self.has_key) * 2 + int(self.goal_discovered)

# --- Drawing Functions ---
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
    start_rect = pygame.Rect(game.start_pos[1]*CELL_SIZE, game.start_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, GRAY, start_rect)
    
    # Draw Key
    if not game.has_key:
        key_rect = pygame.Rect(game.key_pos[1]*CELL_SIZE, game.key_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if key_img: screen.blit(key_img, key_rect)
        else: pygame.draw.rect(screen, YELLOW, key_rect)

    # Draw Goal
    goal_rect = pygame.Rect(game.goal_pos[1]*CELL_SIZE, game.goal_pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    if goal_img: screen.blit(goal_img, goal_rect)
    else: pygame.draw.rect(screen, GREEN, goal_rect)

    # Draw Path
    if path:
        for pos in path:
            pygame.draw.circle(screen, PATH_COLOR, (pos[1]*CELL_SIZE + CELL_SIZE//2, pos[0]*CELL_SIZE + CELL_SIZE//2), 2)

    for enemy in game.enemies:
        center_x = enemy.pos[1] * CELL_SIZE + CELL_SIZE // 2
        center_y = enemy.pos[0] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, PURPLE, (center_x, center_y), CELL_SIZE // 2 - 2)
        
    # Draw Agent
    center_x = game.agent_pos[1] * CELL_SIZE + CELL_SIZE // 2
    center_y = game.agent_pos[0] * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - 2
    pygame.draw.circle(screen, BLUE, (center_x, center_y), radius)
    if game.has_key:
        pygame.draw.circle(screen, CYAN, (center_x, center_y), radius - 3)