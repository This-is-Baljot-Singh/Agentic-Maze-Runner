# agent.py
import numpy as np
import random
import os
from config import *

class QLearningAgent:
    def __init__(self):
        self.q_table = np.zeros((4, 2))
        self.lr = LEARNING_RATE
        self.gamma = DISCOUNT_FACTOR
        self.epsilon = EPSILON_START

    def choose_action(self, state):
        # 0 = Go for Key, 1 = Go for Goal
        if random.uniform(0, 1) < self.epsilon:
            return random.randrange(2)
        return np.argmax(self.q_table[state, :])

    def learn(self, state, action, reward, next_state):
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state, :])
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_value

    def decay_epsilon(self):
        if self.epsilon > EPSILON_MIN:
            self.epsilon *= EPSILON_DECAY
        
    def save(self): 
        np.save(Q_TABLE_FILENAME, self.q_table)
        print(f"Q-table saved to {Q_TABLE_FILENAME}")
        
    def load(self): 
        if os.path.exists(Q_TABLE_FILENAME):
            self.q_table = np.load(Q_TABLE_FILENAME)
            print(f"Q-table loaded from {Q_TABLE_FILENAME}")
            return True
        return False