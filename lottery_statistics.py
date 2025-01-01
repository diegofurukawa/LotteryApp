import pandas as pd
from collections import Counter
from typing import List, Dict, Tuple
from itertools import combinations
import random

class LotteryStatistics:
    def __init__(self, results_data: pd.DataFrame):
        self.results_data = results_data
        self.number_frequencies = {}
        self.calculate_frequencies()
    
    def calculate_frequencies(self) -> None:
        """Calcula a frequência de todos os números"""
        all_numbers = []
        for col in self.results_data.filter(regex='Bola|Dezena').columns:
            all_numbers.extend(self.results_data[col].dropna().astype(int).tolist())
        self.number_frequencies = Counter(all_numbers)
    
    def analyze_decade_groups(self) -> Dict:
        """Analisa a frequência dos grupos de dezenas"""
        decades = {
            '01-10': 0, '11-20': 0, '21-30': 0,
            '31-40': 0, '41-50': 0, '51-60': 0
        }
        
        decade_patterns = []
        total_games = 0
        
        for _, row in self.results_data.iterrows():
            game_decades = {k: 0 for k in decades.keys()}
            numbers = []
            
            for col in self.results_data.filter(regex='Bola|Dezena').columns:
                if pd.notna(row[col]):
                    num = int(row[col])
                    numbers.append(num)
                    decade_key = f"{((num-1)//10)*10+1:02d}-{((num-1)//10+1)*10}"
                    game_decades[decade_key] += 1
                    decades[decade_key] += 1
            
            if numbers:
                pattern = '-'.join(str(v) for v in game_decades.values())
                decade_patterns.append(pattern)
                total_games += 1
        
        pattern_freq = Counter(decade_patterns)
        return {
            'decades': {k: v/total_games/6*100 for k, v in decades.items()},
            'patterns': {k: {'count': v, 'percentage': v/total_games*100}
                        for k, v in pattern_freq.most_common(10)}
        }
    
    def analyze_parity_combinations(self) -> Dict:
        """Analisa combinações de paridade entre números consecutivos"""
        combinations = {
            'par-par': 0,
            'par-impar': 0,
            'impar-par': 0,
            'impar-impar': 0
        }
        total = 0
        
        for _, row in self.results_data.iterrows():
            numbers = []
            for col in self.results_data.filter(regex='Bola|Dezena').columns:
                if pd.notna(row[col]):
                    numbers.append(int(row[col]))
            
            if numbers:
                numbers.sort()
                for i in range(len(numbers)-1):
                    is_current_even = numbers[i] % 2 == 0
                    is_next_even = numbers[i+1] % 2 == 0
                    
                    if is_current_even and is_next_even:
                        combinations['par-par'] += 1
                    elif is_current_even and not is_next_even:
                        combinations['par-impar'] += 1
                    elif not is_current_even and is_next_even:
                        combinations['impar-par'] += 1
                    else:
                        combinations['impar-impar'] += 1
                    total += 1
        
        return {
            'combinations': {k: v/total*100 for k, v in combinations.items()},
            'total_analyzed': total
        }
    
    def analyze_parity_groups(self) -> Dict:
        """Analisa grupos de paridade nas dezenas sorteadas"""
        parity_patterns = []
        
        for _, row in self.results_data.iterrows():
            numbers = []
            for col in self.results_data.filter(regex='Bola|Dezena').columns:
                if pd.notna(row[col]):
                    numbers.append(int(row[col]))
            
            if numbers:
                even_count = sum(1 for num in numbers if num % 2 == 0)
                odd_count = len(numbers) - even_count
                pattern = f"{even_count}p-{odd_count}i"  # p = par, i = ímpar
                parity_patterns.append(pattern)
        
        pattern_freq = Counter(parity_patterns)
        total = len(parity_patterns)
        
        return {
            'patterns': {k: {'count': v, 'percentage': (v/total)*100} 
                        for k, v in pattern_freq.most_common()}
        }

    def get_color_for_frequency(self, number: int) -> str:
        """Retorna a cor em formato hexadecimal baseada na frequência do número"""
        if not self.number_frequencies:
            return "#808080"
        
        freq = self.number_frequencies.get(number, 0)
        min_freq = min(self.number_frequencies.values())
        max_freq = max(self.number_frequencies.values())
        
        if max_freq > min_freq:
            normalized = (freq - min_freq) / (max_freq - min_freq)
        else:
            normalized = 0
        
        red = int(255 * (1 - normalized))
        green = int(255 * normalized)
        return f"#{red:02x}{green:02x}00"
    
    def get_frequency_legend(self) -> List[Tuple[str, int, int]]:
        """Retorna dados para a legenda de frequência"""
        if not self.number_frequencies:
            return []
        
        min_freq = min(self.number_frequencies.values())
        max_freq = max(self.number_frequencies.values())
        steps = 5
        
        legend = []
        for i in range(steps):
            freq = min_freq + (max_freq - min_freq) * i / (steps - 1)
            normalized = i / (steps - 1)
            red = int(255 * (1 - normalized))
            green = int(255 * normalized)
            color = f"#{red:02x}{green:02x}00"
            legend.append((color, int(freq), int(freq)))
        
        return legend

    def generate_smart_games(self, num_games: int, favorite_numbers: List[int] = None) -> List[List[int]]:
        """Gera jogos considerando padrões de paridade e números favoritos"""
        # Obter distribuição de paridade mais comum
        parity_analysis = self.analyze_parity_groups()
        most_common_pattern = list(parity_analysis['patterns'].keys())[0]
        even_count = int(most_common_pattern.split('p-')[0])
        
        games = []
        all_numbers = list(range(1, 61))
        even_numbers = [n for n in all_numbers if n % 2 == 0]
        odd_numbers = [n for n in all_numbers if n % 2 != 0]
        
        if favorite_numbers:
            # Garantir que números favoritos apareçam com mais frequência
            favorite_weight = 3
            for _ in range(num_games):
                game = []
                remaining_even = even_count
                remaining_odd = 6 - even_count
                
                # Adicionar números favoritos primeiro
                for num in favorite_numbers:
                    if len(game) < 6:
                        if num % 2 == 0 and remaining_even > 0:
                            game.append(num)
                            remaining_even -= 1
                        elif num % 2 != 0 and remaining_odd > 0:
                            game.append(num)
                            remaining_odd -= 1
                
                # Completar com outros números
                while remaining_even > 0:
                    available = [n for n in even_numbers if n not in game]
                    weights = [favorite_weight if n in favorite_numbers else 1 for n in available]
                    num = random.choices(available, weights=weights)[0]
                    game.append(num)
                    remaining_even -= 1
                
                while remaining_odd > 0:
                    available = [n for n in odd_numbers if n not in game]
                    weights = [favorite_weight if n in favorite_numbers else 1 for n in available]
                    num = random.choices(available, weights=weights)[0]
                    game.append(num)
                    remaining_odd -= 1
                
                games.append(sorted(game))
        else:
            # Gerar jogos normalmente seguindo o padrão de paridade
            for _ in range(num_games):
                game = sorted(random.sample(even_numbers, even_count) + 
                            random.sample(odd_numbers, 6 - even_count))
                games.append(game)
        
        return games
    
    def get_summary_statistics(self) -> str:
        """Retorna um resumo das estatísticas em formato de texto"""
        if self.results_data.empty:
            return "Sem dados disponíveis"
        
        stats_text = "Estatísticas da Mega Sena\n\n"
        
        # Números mais e menos sorteados
        most_common = sorted(self.number_frequencies.items(), key=lambda x: (-x[1], x[0]))
        least_common = sorted(self.number_frequencies.items(), key=lambda x: (x[1], x[0]))
        
        stats_text += "TOP 10 - Mais sorteados:\n"
        for number, freq in most_common[:10]:
            stats_text += f"Número {number:02d}: {freq} vezes\n"
        
        stats_text += "\nTOP 10 - Menos sorteados:\n"
        for number, freq in least_common[:10]:
            stats_text += f"Número {number:02d}: {freq} vezes\n"
        
        # Análise de grupos de dezenas
        decade_analysis = self.analyze_decade_groups()
        stats_text += "\nDistribuição por Grupos de Dezenas:\n"
        for decade, percentage in decade_analysis['decades'].items():
            stats_text += f"Grupo {decade}: {percentage:.1f}%\n"
        
        stats_text += "\nPadrões mais comuns de grupos:\n"
        for pattern, data in list(decade_analysis['patterns'].items())[:5]:
            stats_text += f"Padrão {pattern}: {data['count']} jogos ({data['percentage']:.1f}%)\n"
        
        # Análise de paridade
        parity_analysis = self.analyze_parity_groups()
        stats_text += "\nDistribuição de Paridade:\n"
        for pattern, data in parity_analysis['patterns'].items():
            stats_text += f"{pattern}: {data['count']} jogos ({data['percentage']:.1f}%)\n"
        
        # Análise de combinações de paridade
        parity_combinations = self.analyze_parity_combinations()
        stats_text += "\nCombinações de Paridade:\n"
        for combo, percentage in parity_combinations['combinations'].items():
            stats_text += f"{combo}: {percentage:.1f}%\n"
        
        return stats_text