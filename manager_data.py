import pandas as pd
import requests
from io import BytesIO
from typing import Tuple, Optional
from datetime import datetime

class DataManager:
    API_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Mega-Sena"
    
    @staticmethod
    def download_results() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Downloads and processes lottery results from the API
        Returns: Tuple[DataFrame or None, error message or None]
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(DataManager.API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            df = pd.read_excel(BytesIO(response.content))
            df = df.sort_values('Concurso', ascending=False)
            
            return df, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def export_games(games_history: str, file_path: str) -> Optional[str]:
        """
        Exports generated games to a file
        Returns: error message if any, None otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Simulações Mega Sena\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write(games_history)
            return None
        except Exception as e:
            return str(e)
    
    @staticmethod
    def process_game_numbers(row: pd.Series) -> list:
        """
        Processes a row of lottery results to extract the numbers
        Returns: List of numbers from the game
        """
        numeros = []
        for i in range(1, 7):
            col_name = f'Bola{i}' if f'Bola{i}' in row.index else f'Dezena {i}'
            if col_name in row.index and pd.notna(row[col_name]):
                numeros.append(int(row[col_name]))
        return sorted(numeros)

    @staticmethod
    def format_game_for_display(numeros: list) -> str:
        """
        Formats a list of numbers into a display string
        Returns: Formatted string of numbers
        """
        return ', '.join(f"{num:02d}" for num in sorted(numeros))