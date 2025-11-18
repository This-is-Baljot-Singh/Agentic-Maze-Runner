# utils.py
import heapq
from config import *

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_star_path(grid, start, end):
    grid_height, grid_width = grid.shape
    open_set = [(0, start)]
    came_from = {}
    
    g_score = { (r,c): float('inf') for r in range(grid_height) for c in range(grid_width) }
    g_score[start] = 0
    
    f_score = { (r,c): float('inf') for r in range(grid_height) for c in range(grid_width) }
    f_score[start] = manhattan_distance(start, end)
    
    open_set_hash = {start} # Faster lookups

    while open_set:
        _, current = heapq.heappop(open_set)
        open_set_hash.discard(current)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            
            # Bounds and collision check
            if (0 <= neighbor[0] < grid_height and 
                0 <= neighbor[1] < grid_width and 
                grid[neighbor[0], neighbor[1]] not in [WALL, TRAP]):
                
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, end)
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
    return None