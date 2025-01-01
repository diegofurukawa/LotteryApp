import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime

class SearchManager:
    def __init__(self):
        self.search_types = {
            "Concurso": self._search_by_contest,
            "Ano": self._search_by_year,
            "Mês": self._search_by_month,
        }
    
    def search(self, df: pd.DataFrame, search_type: str, search_value: str) -> pd.DataFrame:
        """
        Realiza a busca no DataFrame com base no tipo e valor da busca
        
        Args:
            df: DataFrame com os resultados
            search_type: Tipo de busca ('Concurso', 'Ano', 'Mês')
            search_value: Valor a ser buscado
            
        Returns:
            DataFrame filtrado com os resultados da busca
        """
        if df.empty or not search_value.strip():
            return df
            
        search_func = self.search_types.get(search_type)
        if not search_func:
            raise ValueError(f"Tipo de busca inválido: {search_type}")
            
        return search_func(df, search_value.strip())
    
    def _search_by_contest(self, df: pd.DataFrame, value: str) -> pd.DataFrame:
        """Busca por número do concurso"""
        try:
            # Permite busca parcial e exata
            return df[df['Concurso'].astype(str).str.contains(value, na=False)]
        except Exception as e:
            raise ValueError(f"Erro na busca por concurso: {str(e)}")
    
    def _search_by_year(self, df: pd.DataFrame, value: str) -> pd.DataFrame:
        """Busca por ano"""
        try:
            # Converte a coluna de data para datetime se necessário
            if not pd.api.types.is_datetime64_any_dtype(df['Data do Sorteio']):
                df['Data do Sorteio'] = pd.to_datetime(df['Data do Sorteio'])
            
            return df[df['Data do Sorteio'].dt.year.astype(str).str.contains(value, na=False)]
        except Exception as e:
            raise ValueError(f"Erro na busca por ano: {str(e)}")
    
    def _search_by_month(self, df: pd.DataFrame, value: str) -> pd.DataFrame:
        """Busca por mês"""
        try:
            # Converte a coluna de data para datetime se necessário
            if not pd.api.types.is_datetime64_any_dtype(df['Data do Sorteio']):
                df['Data do Sorteio'] = pd.to_datetime(df['Data do Sorteio'])
            
            # Aceita tanto número do mês quanto nome
            if value.isdigit():
                month_filter = df['Data do Sorteio'].dt.month.astype(str).str.contains(value, na=False)
            else:
                # Converte o mês para nome em português e permite busca case-insensitive
                month_names = {
                    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                }
                df['month_name'] = df['Data do Sorteio'].dt.month.map(month_names)
                month_filter = df['month_name'].str.contains(value.lower(), na=False)
                df = df.drop('month_name', axis=1)
            
            return df[month_filter]
        except Exception as e:
            raise ValueError(f"Erro na busca por mês: {str(e)}")
    
    def format_search_results(self, filtered_df: pd.DataFrame) -> str:
        """
        Formata os resultados da busca para exibição
        
        Args:
            filtered_df: DataFrame com os resultados filtrados
            
        Returns:
            String formatada com os resultados
        """
        if filtered_df.empty:
            return "Nenhum resultado encontrado para a busca."
        
        results_text = "Resultados da pesquisa:\n\n"
        
        for _, row in filtered_df.iterrows():
            concurso = row.get('Concurso', 'N/A')
            data_sorteio = row.get('Data do Sorteio', 'N/A')
            
            # Extrai os números do sorteio
            numeros = []
            for i in range(1, 7):
                col_name = f'Bola{i}' if f'Bola{i}' in filtered_df.columns else f'Dezena {i}'
                if col_name in filtered_df.columns and pd.notna(row[col_name]):
                    numeros.append(int(row[col_name]))
            
            if numeros:
                numeros_str = ' - '.join(f"{num:02d}" for num in sorted(numeros))
                results_text += f"Concurso {concurso} ({data_sorteio})\n"
                results_text += f"Números: {numeros_str}\n"
                results_text += "-" * 50 + "\n"
        
        return results_text