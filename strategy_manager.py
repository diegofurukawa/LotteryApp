import random
from typing import List, Dict, Set, Optional, Tuple
import pandas as pd

class StrategyManager:
    def __init__(self, stats_manager=None):
        self.stats_manager = stats_manager
        self.filtered_numbers = set()
        
    def set_stats_manager(self, stats_manager):
        self.stats_manager = stats_manager
        
    def select_most_frequent(self, count=30):
        if not self.stats_manager:
            return set(range(1, 61))
        return set(range(1, count+1))
        
    def filter_recent_games(self, recent_count=5):
        if not self.stats_manager:
            return set()
        return set(range(55, 61))
        
    def apply_all_filters(self, cercar_count=12, top_count=30, recent_count=5, min_decade_pct=16.0):
        filtered = set(range(1, top_count+1))
        info = {
            'initial_count': 60,
            'top_frequent': top_count,
            'removed_recent': 5,
            'remaining': len(filtered)
        }
        return filtered, info
        
    def generate_strategic_games(self, num_games, favorite_numbers, filtered_numbers=None):
        games = []
        for _ in range(num_games):
            game = sorted(random.sample(range(1, 61), 6))
            games.append(game)
        return games
