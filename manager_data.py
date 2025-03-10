from tkinter import filedialog, messagebox
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
    
    @staticmethod
    def export_as_results(self):
        """Exportar simulações no formato dos resultados oficiais"""
        # Verificar se há jogos no histórico
        if not self.game_manager.games_history:
            messagebox.showwarning("Aviso", "Nenhum jogo para exportar!")
            return
        
        # Solicitar local para salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Exportar como Resultados"
        )
        
        if not file_path:
            return  # Usuário cancelou
        
        # Exportar no formato de resultados
        error = self.data_manager.export_results_format(
            self.game_manager.games_history, 
            file_path
        )
        
        if error:
            messagebox.showerror("Erro", f"Erro ao exportar: {error}")
        else:
            messagebox.showinfo("Sucesso", "Jogos exportados com sucesso no formato de resultados oficiais!")

    @staticmethod
    def export_results_format(self, games_history, file_path: str) -> Optional[str]:
        """
        Exporta os jogos gerados no mesmo formato dos resultados da Mega Sena
        
        Args:
            games_history: Lista de tuplas [(timestamp, numbers)]
            file_path: Caminho do arquivo para salvar (formato Excel .xlsx)
            
        Returns:
            Mensagem de erro se houver, None caso contrário
        """
        try:
            import pandas as pd
            from datetime import datetime
            
            # Criar DataFrame vazio com as mesmas colunas dos resultados
            df = pd.DataFrame(columns=[
                'Concurso', 'Data do Sorteio', 'Bola1', 'Bola2', 'Bola3', 
                'Bola4', 'Bola5', 'Bola6', 'Arrecadacao_Total'
            ])
            
            # Preencher com os jogos gerados
            for i, (timestamp, numbers) in enumerate(games_history, 1):
                if isinstance(timestamp, datetime):
                    date_str = timestamp.strftime('%d/%m/%Y')
                else:
                    # Se for string, tenta extrair a data
                    try:
                        date_parts = timestamp.split('[')[1].split(']')[0].strip()
                        date_str = date_parts.split()[0]
                    except:
                        date_str = datetime.now().strftime('%d/%m/%Y')
                
                # Ordenar os números
                sorted_numbers = sorted(numbers)
                
                # Criar linha para o DataFrame
                row = {
                    'Concurso': f'SIM-{i:04d}',  # Prefixo SIM para indicar que é simulado
                    'Data do Sorteio': date_str,
                }
                
                # Adicionar as bolas
                for j, num in enumerate(sorted_numbers, 1):
                    row[f'Bola{j}'] = num
                    
                # Adicionar arrecadação fictícia
                row['Arrecadacao_Total'] = 0
                
                # Adicionar ao DataFrame
                df.loc[len(df)] = row
            
            # Salvar como Excel
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
                
            df.to_excel(file_path, index=False)
            return None
        except Exception as e:
            return str(e)