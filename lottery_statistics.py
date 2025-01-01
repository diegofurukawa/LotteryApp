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
        combinations_dict = {
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
                        combinations_dict['par-par'] += 1
                    elif is_current_even and not is_next_even:
                        combinations_dict['par-impar'] += 1
                    elif not is_current_even and is_next_even:
                        combinations_dict['impar-par'] += 1
                    else:
                        combinations_dict['impar-impar'] += 1
                    total += 1
        
        return {
            'combinations': {k: v/total*100 for k, v in combinations_dict.items()},
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

    def get_hot_numbers(self, limit: int = 15) -> List[int]:
        """Retorna os números mais frequentes"""
        freq_sorted = sorted(self.number_frequencies.items(),
                           key=lambda x: (-x[1], x[0]))  # (-) para ordenar decrescente
        return [num for num, _ in freq_sorted[:limit]]

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
    
    def get_best_decade_pattern(self) -> Dict[str, int]:
        """Retorna o melhor padrão de distribuição por décadas"""
        decade_analysis = self.analyze_decade_groups()
        best_pattern = list(decade_analysis['patterns'].keys())[0]
        return {f"{i+1}0": int(n) for i, n in enumerate(best_pattern.split('-'))}

    def generate_smart_games(self, num_games: int, favorite_numbers: List[int]) -> List[List[int]]:
        """
        Gera jogos inteligentes baseados em favoritos, frequência, paridade e décadas
        Args:
            num_games: Quantidade de jogos a gerar
            favorite_numbers: Lista de números favoritos
        Returns:
            Lista de jogos gerados
        """
        games = set()  # Usar set para garantir jogos únicos
        hot_numbers = self.get_hot_numbers(20)  # Top 20 números mais frequentes
        
        # Obter melhores padrões
        parity_pattern = list(self.analyze_parity_groups()['patterns'].keys())[0]
        even_target = int(parity_pattern.split('p-')[0])
        decade_pattern = self.get_best_decade_pattern()
        
        # Tentar gerar jogos até ter a quantidade solicitada ou atingir limite máximo de tentativas
        max_attempts = num_games * 10  # Limite de tentativas para evitar loop infinito
        attempts = 0
        
        while len(games) < num_games and attempts < max_attempts:
            game = self._generate_smart_game(
                favorite_numbers=favorite_numbers,
                hot_numbers=hot_numbers,
                even_target=even_target,
                decade_pattern=decade_pattern
            )
            
            # Converter para tupla para poder adicionar ao set
            game_tuple = tuple(sorted(game))
            games.add(game_tuple)
            attempts += 1
        
        # Converter de volta para lista de listas
        return [list(game) for game in games]

    def _generate_smart_game(self, favorite_numbers: List[int], hot_numbers: List[int],
                        even_target: int, decade_pattern: Dict[str, int]) -> List[int]:
        """
        Gera um único jogo inteligente
        """
        game = []
        remaining_even = even_target
        remaining_odd = 6 - even_target
        decade_counts = {k: 0 for k in decade_pattern.keys()}
        
        # Criar lista de números favoritos embaralhada
        shuffled_favorites = favorite_numbers.copy()
        random.shuffle(shuffled_favorites)
        
        # Criar lista de números quentes embaralhada
        shuffled_hot = [n for n in hot_numbers if n not in favorite_numbers]
        random.shuffle(shuffled_hot)
        
        def can_add_number(num: int) -> bool:
            decade = f"{((num-1)//10 + 1)}0"
            current_count = decade_counts[decade]
            target_count = decade_pattern[decade]
            is_even = num % 2 == 0
            
            if is_even and remaining_even <= 0:
                return False
            if not is_even and remaining_odd <= 0:
                return False
            if current_count >= target_count:
                return False
            return True
        
        # 1. Primeiro, tentar incluir números favoritos que se encaixam nos padrões
        for num in shuffled_favorites:
            if len(game) < 6 and can_add_number(num):
                game.append(num)
                decade_counts[f"{((num-1)//10 + 1)}0"] += 1
                if num % 2 == 0:
                    remaining_even -= 1
                else:
                    remaining_odd -= 1
        
        # 2. Completar com números quentes que se encaixam nos padrões
        for num in shuffled_hot:
            if len(game) < 6 and num not in game and can_add_number(num):
                game.append(num)
                decade_counts[f"{((num-1)//10 + 1)}0"] += 1
                if num % 2 == 0:
                    remaining_even -= 1
                else:
                    remaining_odd -= 1
        
        # 3. Completar aleatoriamente seguindo os padrões
        available_numbers = list(set(range(1, 61)) - set(game))
        random.shuffle(available_numbers)
        
        for num in available_numbers:
            if len(game) < 6 and can_add_number(num):
                game.append(num)
                decade_counts[f"{((num-1)//10 + 1)}0"] += 1
                if num % 2 == 0:
                    remaining_even -= 1
                else:
                    remaining_odd -= 1
        
        return game
    
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
    
    def analyze_game(self, numbers: List[int], recent_draws: int = 5) -> Dict:
        """
        Analisa um jogo comparando com o histórico de sorteios
        Args:
            numbers: Lista de números do jogo
            recent_draws: Quantidade de sorteios recentes a considerar
        Returns:
            Dicionário com as análises
        """
        if self.results_data.empty:
            return {
                'was_drawn': False,
                'last_drawn_date': None,
                'matches_recent': [],
                'matching_numbers': {}
            }
        
        numbers_set = set(numbers)
        result = {
            'was_drawn': False,  # Jogo completo já foi sorteado?
            'last_drawn_date': None,  # Data do último sorteio deste jogo
            'matches_recent': [],  # Números que aparecem nos sorteios recentes
            'matching_numbers': {}  # Números que coincidem por sorteio
        }
        
        # Verificar cada sorteio
        for _, row in self.results_data.iterrows():
            drawn_numbers = []
            for col in self.results_data.filter(regex='Bola|Dezena').columns:
                if pd.notna(row[col]):
                    drawn_numbers.append(int(row[col]))
            
            drawn_set = set(drawn_numbers)
            matches = numbers_set.intersection(drawn_set)
            
            # Se encontrou correspondências
            if matches:
                result['matching_numbers'][row['Concurso']] = {
                    'date': row['Data do Sorteio'],
                    'numbers': sorted(list(matches))
                }
            
            # Se for o jogo completo
            if numbers_set == drawn_set:
                result['was_drawn'] = True
                result['last_drawn_date'] = row['Data do Sorteio']
                break
        
        # Verificar números nos sorteios recentes
        recent_draws_data = self.results_data.head(recent_draws)
        recent_numbers = set()
        
        for _, row in recent_draws_data.iterrows():
            for col in recent_draws_data.filter(regex='Bola|Dezena').columns:
                if pd.notna(row[col]):
                    recent_numbers.add(int(row[col]))
        
        result['matches_recent'] = sorted(list(numbers_set.intersection(recent_numbers)))
        
        return result