import random
from typing import List, Dict, Set, Optional, Tuple
import pandas as pd
from lottery_statistics import LotteryStatistics

class StrategyManager:
    """Gerenciador de estratégias avançadas para filtragem e geração de jogos"""
    
    def __init__(self, stats_manager: Optional[LotteryStatistics] = None):
        self.stats_manager = stats_manager
        self.filtered_numbers: Set[int] = set()
        self.base_numbers: Set[int] = set(range(1, 61))
        
    def set_stats_manager(self, stats_manager: LotteryStatistics) -> None:
        """Define o gerenciador de estatísticas"""
        self.stats_manager = stats_manager
        self.filtered_numbers = set()  # Reinicia o filtro quando atualiza as estatísticas
        
    def select_most_frequent(self, count: int = 30) -> Set[int]:
        """
        Seleciona os números mais frequentes
        
        Args:
            count: Quantidade de números a selecionar
        
        Returns:
            Conjunto de números selecionados
        """
        if not self.stats_manager:
            return set()
            
        hot_numbers = self.stats_manager.get_hot_numbers(count)
        return set(hot_numbers)
    
    def filter_recent_games(self, recent_count: int = 5) -> Set[int]:
        """
        Retira números que aparecem nos jogos recentes
        
        Args:
            recent_count: Quantidade de jogos recentes a considerar
        
        Returns:
            Conjunto de números excluídos
        """
        if not self.stats_manager or self.stats_manager.results_data.empty:
            return set()
            
        recent_draws = self.stats_manager.results_data.head(recent_count)
        excluded_numbers = set()
        
        for _, row in recent_draws.iterrows():
            for col in recent_draws.filter(regex='Bola|Dezena').columns:
                if pd.notna(row[col]):
                    excluded_numbers.add(int(row[col]))
        
        return excluded_numbers
    
    def apply_parity_filter(self, keep_patterns: List[str] = None) -> Dict[str, Set[int]]:
        """
        Filtra números para manter uma distribuição de paridade específica
        
        Args:
            keep_patterns: Lista de padrões de paridade a manter (ex: ["3p-3i", "4p-2i", "2p-4i"])
        
        Returns:
            Dicionário com conjuntos de números pares e ímpares a manter
        """
        if not keep_patterns:
            keep_patterns = ["3p-3i", "4p-2i", "2p-4i"]
            
        even_numbers = {num for num in range(1, 61) if num % 2 == 0}
        odd_numbers = {num for num in range(1, 61) if num % 2 != 0}
        
        return {
            'even': even_numbers,
            'odd': odd_numbers,
            'patterns': keep_patterns
        }
    
    def apply_decade_filter(self, min_percentage: float = 16.0) -> Dict[str, Set[int]]:
        """
        Filtra números para manter grupos de dezenas mais relevantes
        
        Args:
            min_percentage: Percentual mínimo para manter um grupo
        
        Returns:
            Dicionário com conjuntos de números por grupo de dezenas
        """
        if not self.stats_manager:
            # Se não houver estatísticas, retorna todos os grupos
            return {
                f"{i*10+1}-{(i+1)*10}": {j for j in range(i*10+1, (i+1)*10+1)}
                for i in range(6)
            }
        
        decade_analysis = self.stats_manager.analyze_decade_groups()
        decades_to_keep = {}
        
        for decade, percentage in decade_analysis['decades'].items():
            if percentage >= min_percentage:
                start, end = map(int, decade.split('-'))
                decades_to_keep[decade] = {num for num in range(start, end + 1)}
        
        return decades_to_keep
    
    def apply_all_filters(self, cercar_count: int = 12, top_count: int = 30, 
                         recent_count: int = 5, min_decade_pct: float = 16.0) -> Tuple[Set[int], Dict]:
        """
        Aplica todos os filtros e retorna os números resultantes
        
        Args:
            cercar_count: Quantidade de números favoritos a manter
            top_count: Quantidade de números mais frequentes a selecionar
            recent_count: Quantidade de jogos recentes a considerar
            min_decade_pct: Percentual mínimo para manter um grupo de dezenas
        
        Returns:
            Tuple contendo conjunto de números resultantes e informações de filtro
        """
        if not self.stats_manager:
            return set(range(1, 61)), {}
        
        # 1. Iniciar com todos os números (1-60)
        all_numbers = set(range(1, 61))
        
        # 2. Pegar os mais frequentes
        top_frequent = self.select_most_frequent(top_count)
        
        # 3. Retirar números dos jogos recentes
        recent_numbers = self.filter_recent_games(recent_count)
        filtered_set = top_frequent - recent_numbers
        
        # 4. Organizar os favoritos (cercar)
        # Obs: Na implementação, os favoritos serão definidos pelo usuário
        
        # 5. Registrar informações sobre os filtros
        filter_info = {
            'initial_count': len(all_numbers),
            'top_frequent': len(top_frequent),
            'removed_recent': len(recent_numbers),
            'remaining': len(filtered_set)
        }
        
        self.filtered_numbers = filtered_set
        return filtered_set, filter_info
    
    def generate_strategic_games(self, num_games: int, favorite_numbers: List[int], 
                                filtered_numbers: Optional[Set[int]] = None) -> List[List[int]]:
        """
        Gera jogos estratégicos baseados em favoritos e filtros
        
        Args:
            num_games: Quantidade de jogos a gerar
            favorite_numbers: Lista de números favoritos a priorizar
            filtered_numbers: Conjunto de números pré-filtrados (opcional)
        
        Returns:
            Lista de jogos gerados
        """
        if not self.stats_manager:
            # Se não houver estatísticas, gera jogos aleatórios
            return [sorted(random.sample(range(1, 61), 6)) for _ in range(num_games)]
        
        games = set()  # Usar set para garantir jogos únicos
        
        # Se não foi passado conjunto filtrado, usa o filtrado pela classe
        if filtered_numbers is None:
            filtered_numbers = self.filtered_numbers
            if not filtered_numbers:  # Se ainda estiver vazio, aplica filtros padrão
                filtered_numbers, _ = self.apply_all_filters()
        
        # Converte favoritos para conjunto para operações mais rápidas
        favorite_set = set(favorite_numbers)
        
        # Garantir que os favoritos estejam no conjunto filtrado
        valid_favorites = favorite_set.intersection(filtered_numbers)
        other_numbers = filtered_numbers - valid_favorites
        
        # Obter padrões de paridade alvo
        parity_patterns = ["3p-3i", "4p-2i", "2p-4i"]  # Padrões pré-definidos
        if self.stats_manager:
            # Tenta obter padrões das estatísticas se disponível
            parity_analysis = self.stats_manager.analyze_parity_groups()
            if parity_analysis and 'patterns' in parity_analysis:
                parity_patterns = list(parity_analysis['patterns'].keys())[:3]
        
        # Obter distribuição de dezenas alvo
        decade_target = {}
        if self.stats_manager:
            decade_analysis = self.stats_manager.analyze_decade_groups()
            if decade_analysis and 'decades' in decade_analysis:
                total = sum(decade_analysis['decades'].values())
                for decade, pct in decade_analysis['decades'].items():
                    # Convertemos para número inteiro de 0-2 para cada grupo de dezena
                    decade_target[decade] = round((pct / total) * 6)
                
                # Garantir que a soma seja 6
                adjustment_needed = 6 - sum(decade_target.values())
                if adjustment_needed != 0:
                    # Ajustar os grupos mais frequentes
                    sorted_decades = sorted(decade_target.items(), key=lambda x: (-decade_analysis['decades'][x[0]], x[0]))
                    for i in range(abs(adjustment_needed)):
                        decade = sorted_decades[i][0]
                        decade_target[decade] += 1 if adjustment_needed > 0 else -1
        
        # Tentar gerar jogos até ter a quantidade solicitada ou atingir limite de tentativas
        max_attempts = num_games * 20  # Limite para evitar loop infinito
        attempts = 0
        
        while len(games) < num_games and attempts < max_attempts:
            # Escolher padrão de paridade aleatório
            pattern = random.choice(parity_patterns)
            even_target = int(pattern.split('p-')[0])
            odd_target = 6 - even_target
            
            # Gerar jogo seguindo o padrão e priorizando favoritos
            game = self._generate_single_game(
                valid_favorites=valid_favorites,
                other_numbers=other_numbers,
                even_target=even_target,
                odd_target=odd_target,
                decade_target=decade_target
            )
            
            if game:
                # Converter para tupla para poder adicionar ao set
                game_tuple = tuple(sorted(game))
                games.add(game_tuple)
            
            attempts += 1
        
        # Converter de volta para lista de listas
        return [list(game) for game in games]
    
    def _generate_single_game(self, valid_favorites: Set[int], other_numbers: Set[int],
                             even_target: int, odd_target: int, 
                             decade_target: Dict[str, int]) -> List[int]:
        """
        Gera um único jogo seguindo os critérios de estratégia
        
        Args:
            valid_favorites: Conjunto de números favoritos válidos
            other_numbers: Conjunto de outros números filtrados
            even_target: Quantidade alvo de números pares
            odd_target: Quantidade alvo de números ímpares
            decade_target: Dicionário com quantidade alvo por grupo de dezenas
        
        Returns:
            Lista de 6 números para o jogo
        """
        game = []
        even_count = 0
        odd_count = 0
        decade_counts = {decade: 0 for decade in decade_target.keys()}
        
        # Função auxiliar para verificar se um número pode ser adicionado
        def can_add(num: int) -> bool:
            is_even = num % 2 == 0
            decade = f"{((num-1)//10)*10+1:02d}-{((num-1)//10+1)*10}"
            
            if is_even and even_count >= even_target:
                return False
            if not is_even and odd_count >= odd_target:
                return False
            if decade in decade_counts and decade_counts[decade] >= decade_target.get(decade, 1):
                return False
            return True
        
        # Primeiro, adicionar favoritos que atendem aos critérios
        favorites_list = list(valid_favorites)
        random.shuffle(favorites_list)
        
        for num in favorites_list:
            if len(game) < 6 and num not in game and can_add(num):
                game.append(num)
                if num % 2 == 0:
                    even_count += 1
                else:
                    odd_count += 1
                    
                decade = f"{((num-1)//10)*10+1:02d}-{((num-1)//10+1)*10}"
                if decade in decade_counts:
                    decade_counts[decade] += 1
        
        # Completar com outros números filtrados
        others_list = list(other_numbers)
        random.shuffle(others_list)
        
        for num in others_list:
            if len(game) < 6 and num not in game and can_add(num):
                game.append(num)
                if num % 2 == 0:
                    even_count += 1
                else:
                    odd_count += 1
                    
                decade = f"{((num-1)//10)*10+1:02d}-{((num-1)//10+1)*10}"
                if decade in decade_counts:
                    decade_counts[decade] += 1
        
        # Se não conseguiu completar 6 números, preenche aleatoriamente
        if len(game) < 6:
            remaining = set(range(1, 61)) - set(game)
            remaining_list = list(remaining)
            random.shuffle(remaining_list)
            
            for num in remaining_list:
                if len(game) < 6 and num not in game:
                    game.append(num)
        
        return sorted(game)