import random
from typing import List, Set
from datetime import datetime

class GameManager:
    def __init__(self):
        self.selected_numbers: Set[int] = set()
        self.favorite_numbers: Set[int] = set()
        self.games_history: List[tuple] = []  # [(timestamp, numbers)]
    
    def toggle_number(self, number: int) -> bool:
        """
        Toggle selection of a number
        Returns: True if number was added, False if removed
        """
        if number in self.selected_numbers:
            self.selected_numbers.remove(number)
            return False
        elif len(self.selected_numbers) < 13:
            self.selected_numbers.add(number)
            return True
        return False
    
    def mark_favorites(self) -> bool:
        """
        Mark currently selected numbers as favorites
        Returns: True if operation was successful
        """
        if not self.selected_numbers:
            return False
        
        self.favorite_numbers.update(self.selected_numbers)
        return True
    
    def generate_random_games(self, num_games: int) -> List[List[int]]:
        """Generate specified number of random games"""
        games = []
        for _ in range(num_games):
            numbers = sorted(random.sample(range(1, 61), 6))
            self.save_game(numbers)
            games.append(numbers)
        return games
    
    def save_game(self, numbers: List[int]) -> None:
        """Save a game to history"""
        timestamp = datetime.now()
        self.games_history.append((timestamp, numbers))
    
    def get_selected_numbers(self) -> List[int]:
        """Get current selected numbers as sorted list"""
        return sorted(list(self.selected_numbers))
    
    def get_favorite_numbers(self) -> List[int]:
        """Get favorite numbers as sorted list"""
        return sorted(list(self.favorite_numbers))
    
    def clear_selected_numbers(self) -> None:
        """Clear all selected numbers"""
        self.selected_numbers.clear()
    
    def is_favorite(self, number: int) -> bool:
        """Check if a number is marked as favorite"""
        return number in self.favorite_numbers
    
    def format_game_for_history(self, numbers: List[int]) -> str:
        """Format a game for history display"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        numbers_str = " - ".join(f"{num:02d}" for num in sorted(numbers))
        return f"[{current_time}] {numbers_str}"