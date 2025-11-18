# config.py

# --- Game Configuration ---
GRID_WIDTH = 40
GRID_HEIGHT = 25
CELL_SIZE = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100
FPS = 60

# --- Training Configuration ---
VISUALIZE_TRAINING = False  # Set to True to watch it learn
LOAD_Q_TABLE_IF_EXISTS = True
SAVE_Q_TABLE_ON_EXIT = True
Q_TABLE_FILENAME = "q_table.npy"
NEW_MAZE_FREQUENCY = 50

# --- RL Hyperparameters ---
TOTAL_EPISODES = 3000
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
EPSILON_START = 1.0
EPSILON_DECAY = 0.999
EPSILON_MIN = 0.05
MAX_STRATEGIC_STEPS = 50 # Increased slightly for safety

# --- Reward Structure ---
GOAL_REWARD = 100
KEY_REWARD = 20
DEAD_END_PENALTY = -50 
STEP_PENALTY = -1

# --- Enemy Configuration ---
NUM_ENEMIES = 4       # Enough to be annoying, not impossible
ENEMY_SPEED_DELAY = 0 # 0 = Fast (Moves every frame), 2 = Slow
ENEMY_PENALTY = -100

# --- Colors ---
WHITE=(255,255,255); BLACK=(0,0,0); GREEN=(40,180,99); RED=(231,76,60)
BLUE=(52,152,219); YELLOW=(241,196,15); GRAY=(128,128,128)
CYAN=(26,188,156); PATH_COLOR=(220, 220, 220)
PURPLE = (155, 89, 182)

# --- Cell Types ---
EMPTY=0; WALL=1; TRAP=5; KEY=4; GOAL=3