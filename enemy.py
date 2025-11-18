import random
from config import *

class Enemy:
    def __init__(self, grid, available_cells):
        self.grid_height, self.grid_width = grid.shape
        self.pos = random.choice(available_cells)
        self.directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Right, Left, Down, Up
        
        # Pick an initial random valid direction to start moving
        random.shuffle(self.directions)
        for d in self.directions:
            if self.is_valid_move(grid, self.pos[0] + d[0], self.pos[1] + d[1]):
                self.current_dir = d
                break
        else:
            self.current_dir = (0, 0) # Stuck

        # Speed Control
        self.move_delay = ENEMY_SPEED_DELAY
        self.timer = 0

    def move(self, grid):
        self.timer += 1
        if self.timer < self.move_delay:
            return

        self.timer = 0
        r, c = self.pos
        
        # 1. Identify valid neighbors
        valid_options = []
        for d in self.directions:
            nr, nc = r + d[0], c + d[1]
            if self.is_valid_move(grid, nr, nc):
                valid_options.append(d)
        
        if not valid_options:
            return # Trapped completely

        # 2. THE "NO U-TURN" LOGIC
        # Calculate the "backward" direction (where we just came from)
        backward_dir = (-self.current_dir[0], -self.current_dir[1])
        
        # Filter out the backward direction unless it's the ONLY option (Dead End)
        forward_options = [d for d in valid_options if d != backward_dir]
        
        if forward_options:
            # If we have forward paths, pick one randomly
            # This handles corners and T-junctions naturally
            self.current_dir = random.choice(forward_options)
        else:
            # Only reverse if we hit a Dead End
            self.current_dir = backward_dir

        # 3. Execute Move
        self.pos = (r + self.current_dir[0], c + self.current_dir[1])

    def is_valid_move(self, grid, r, c):
        return (0 <= r < self.grid_height and 
                0 <= c < self.grid_width and 
                grid[r, c] != WALL)