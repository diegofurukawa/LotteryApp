from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os

from manager_ui import UIManager
from manager_data import DataManager
from manager_game import GameManager
from lottery_statistics import LotteryStatistics
from manager_search import SearchManager

# Verificar se o arquivo strategy_manager.py existe
# Se não existir, criar o arquivo com conteúdo básico
if not os.path.exists('strategy_manager.py'):
    with open('strategy_manager.py', 'w') as file:
        file.write("""import random
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
""")

# Agora importamos o StrategyManager
from manger_strategy import StrategyManager

class LotteryApp:
    def __init__(self):
        # Inicializar janela principal
        self.window = ctk.CTk()
        self.ui_manager = UIManager(self.window)
        
        # Inicializar gerenciadores
        self.game_manager = GameManager()
        self.data_manager = DataManager()
        self.search_manager = SearchManager()
        self.stats_manager = None
        self.strategy_manager = StrategyManager()  # Novo gerenciador
        
        # Variáveis de controle
        self.favorite_numbers_var = ctk.StringVar()
        self.favorite_numbers_var.trace_add('write', self.on_favorites_changed)
        
        # Armazenar referências da UI
        self.number_buttons = {}
        self.number_labels = []
        self.ui_components = {}
        self.filtered_numbers = set()  # Conjunto de números após filtragem
        
        # Criar interface
        self.setup_ui()
    
    def clear_history(self):
        """Limpar histórico de jogos gerados"""
        if messagebox.askyesno("Confirmar Limpeza", "Deseja realmente limpar todos os jogos gerados?"):
            # Limpar texto da área de histórico
            self.ui_components['text_areas']['histórico'].delete("0.0", "end")
            
            # Limpar display de números
            for label in self.number_labels:
                label.configure(text="00")
            
            # Limpar seleções no grid
            self.game_manager.clear_selected_numbers()
            self.update_button_appearances()

    def setup_ui(self):
        """Configurar toda a interface do usuário"""
        # Frame principal
        main_frame = self.ui_manager.create_main_frame()
        
        # Título
        self.ui_manager.create_title(main_frame)
        
        # Display de números
        self.number_labels = self.ui_manager.create_number_display(main_frame)
        
        # Grid de números
        self.number_buttons = self.ui_manager.create_number_grid(
            main_frame, 
            self.toggle_number
        )
        
        # Painel de favoritos
        self.ui_manager.create_favorites_panel(main_frame, self.favorite_numbers_var)
        
        # Painel de controle com novos botões
        buttons_config = [
            
            ("Importar Resultados", self.import_results),
            ("Selecionar Top", self.select_top_frequent),  # Novo botão
            ("Limpar Filtros", self.clear_filters),  # Novo botão
            ("Marcar como Favorito", self.mark_as_favorite),
            ("Gerar Estratégico", self.generate_strategic),  # Novo botão
            ("Gerar Números", self.generate_numbers),
            ("Gerar com Favoritos", self.generate_with_favorites),
            ("Limpar Histórico", self.clear_history),
            ("Exportar como Resultados", self.export_as_results)  # Novo botão
        ]
        
        control_panel = self.ui_manager.create_control_panel(main_frame, buttons_config)
        self.ui_components.update(control_panel)
        
        # Abas e áreas de texto
        tabs = self.ui_manager.create_tabs(main_frame)
        self.ui_components.update({
            'notebook': tabs['notebook'],
            'text_areas': tabs['text_areas']
        })
        
        # Painel de busca
        search_components = self.ui_manager.create_search_panel(
            tabs['notebook'].tab("Resultados"),
            self.search_results
        )
        self.ui_components.update(search_components)
    
    def toggle_number(self, number: int):
        """Alternar seleção de número"""
        was_added = self.game_manager.toggle_number(number)
        
        # Atualizar aparência do botão
        if was_added:
            self.number_buttons[number].configure(
                fg_color="blue",
                border_width=0
            )
        else:
            self.number_buttons[number].configure(
                fg_color=self.get_number_color(number),
                border_width=0
            )
        
        # Atualizar display de números
        self.update_number_display()
    
    def update_number_display(self):
        """Atualizar display com números selecionados"""
        selected = self.game_manager.get_selected_numbers()
        # Preencher com zeros os labels não utilizados
        while len(selected) < 6:
            selected.append(0)
        
        for label, number in zip(self.number_labels, selected):
            label.configure(text=f"{number:02d}")
    
    def get_number_color(self, number: int) -> str:
        """Obter cor baseada na frequência do número"""
        if self.stats_manager:
            return self.stats_manager.get_color_for_frequency(number)
        return ("gray75", "gray25")
    
    def on_favorites_changed(self, *args):
        """Callback para mudanças no campo de favoritos"""
        numbers_str = self.favorite_numbers_var.get()
        valid_numbers = self.game_manager.parse_favorite_numbers(numbers_str)
        
        # Atualizar favoritos no game manager
        self.game_manager.set_favorite_numbers(valid_numbers)
        
        # Atualizar aparência dos botões
        self.update_button_appearances()
    
    def update_button_appearances(self):
        """Atualizar aparência de todos os botões"""
        for number, btn in self.number_buttons.items():
            if number in self.game_manager.get_selected_numbers():
                btn.configure(
                    fg_color="blue",
                    border_width=0
                )
            elif number in self.game_manager.get_favorite_numbers():
                btn.configure(
                    fg_color=self.get_number_color(number),
                    border_color="gold",
                    border_width=2
                )
            elif hasattr(self, 'filtered_numbers') and number in self.filtered_numbers:
                # Destacar números filtrados com uma borda verde
                btn.configure(
                    fg_color=self.get_number_color(number),
                    border_color="green",
                    border_width=2
                )
            else:
                # Para botões sem borda, apenas configuramos border_width=0
                btn.configure(
                    fg_color=self.get_number_color(number),
                    border_width=0
                )
    
    def generate_numbers(self):
        """Gerar números aleatórios"""
        try:
            num_games = int(self.ui_components['num_games_var'].get())
            if num_games <= 0:
                raise ValueError("Número de jogos deve ser positivo")
            
            games = self.game_manager.generate_random_games(num_games)
            
            # Atualizar histórico
            for game in games:
                self.save_game_to_history(game)
            
            # Mostrar primeiro jogo no display
            if games:
                self.display_game(games[0])
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar números: {str(e)}")
    
    def generate_with_favorites(self):
        """Gerar números considerando favoritos e estatísticas"""
        if not self.stats_manager:
            messagebox.showwarning("Aviso", "Importe os resultados primeiro!")
            return
        
        favorite_numbers = self.game_manager.parse_favorite_numbers(
            self.favorite_numbers_var.get()
        )
        
        if not favorite_numbers:
            messagebox.showwarning(
                "Aviso", 
                "Insira alguns números favoritos primeiro!"
            )
            return
        
        try:
            num_games = int(self.ui_components['num_games_var'].get())
            if num_games <= 0:
                raise ValueError("Número de jogos deve ser positivo")
            
            # Gerar jogos usando a nova lógica inteligente
            games = self.stats_manager.generate_smart_games(
                num_games,
                favorite_numbers
            )
            
            # Salvar jogos no histórico
            for game in games:
                self.save_game_to_history(game)
            
            # Mostrar o primeiro jogo
            if games:
                self.display_game(games[0])
                
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar jogos: {str(e)}")
    
    def mark_as_favorite(self):
        """Marcar números selecionados como favoritos"""
        if not self.game_manager.mark_favorites():
            messagebox.showwarning("Aviso", "Selecione alguns números primeiro!")
            return
        
        # Atualizar campo de favoritos
        favorites = self.game_manager.format_favorite_numbers()
        self.favorite_numbers_var.set(favorites)
        
        # Limpar seleção e atualizar aparência
        self.game_manager.clear_selected_numbers()
        self.update_button_appearances()
        self.update_number_display()
        
        messagebox.showinfo("Sucesso", "Números marcados como favoritos!")
    
    def save_game_to_history(self, numbers):
        """Salvar jogo no histórico com análises"""
        # Obter a data/hora atual
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Formatar números
        numbers_str = ", ".join(f"{num:02d}" for num in sorted(numbers))
        
        # Texto base do histórico
        history_text = f"[{current_time}]    -    {numbers_str}"
        
        # Se temos dados de sorteios, adicionar análises
        if self.stats_manager:
            analysis = self.stats_manager.analyze_game(numbers)
            
            # Definir cores para o texto
            if analysis['was_drawn']:
                history_text = f"🎯 {history_text} (SORTEADO em {analysis['last_drawn_date']})"
            
            # Adicionar números que aparecem nos sorteios recentes
            if analysis['matches_recent']:
                recent_nums = ", ".join(f"{n:02d}" for n in analysis['matches_recent'])
                history_text += f"    -    ⚠️ Números recentes: {recent_nums}"

            # Adicionar ocorrências em outros sorteios
            for concurso, data in analysis['matching_numbers'].items():
                matches = ", ".join(f"{n:02d}" for n in data['numbers'])
                if len(data['numbers']) >= 4:  # Se tem 4 ou mais números coincidentes
                    history_text += f"    🔍 Concurso(s) -  {concurso}"
        
        # Adicionar ao histórico com uma linha em branco para separação
        self.ui_components['text_areas']['histórico'].insert("0.0", history_text + "\n")
    
    def display_game(self, numbers):
        """Mostrar jogo no display de números"""
        for label, number in zip(self.number_labels, numbers):
            label.configure(text=f"{number:02d}")
    
    def import_results(self):
        """Importar resultados da API"""
        def download():
            try:
                results_df, error = self.data_manager.download_results()
                
                if error:
                    messagebox.showerror("Erro", f"Erro ao importar resultados: {error}")
                    return
                
                # Criar gerenciador de estatísticas
                self.stats_manager = LotteryStatistics(results_df)
                
                # Atualizar o gerenciador de estratégias
                self.strategy_manager.set_stats_manager(self.stats_manager)
                
                # Atualizar interface
                self.update_results_display(results_df)
                self.update_number_colors()
                self.update_statistics()
                
                messagebox.showinfo("Sucesso", "Resultados importados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar resultados: {str(e)}")
        
        # Executar em uma thread separada
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
    def update_results_display(self, results_df):
        """Atualizar display de resultados"""
        if results_df.empty:
            return
            
        results_text = "Últimos Resultados da Mega Sena:\n\n"
        
        for _, row in results_df.iterrows():
            concurso = row.get('Concurso', 'N/A')
            data_sorteio = row.get('Data do Sorteio', 'N/A')
            
            numeros = self.data_manager.process_game_numbers(row)
            if numeros:
                numeros_str = self.data_manager.format_game_for_display(numeros)
                results_text += f"Concurso {concurso} ({data_sorteio})\n"
                results_text += f"Números: {numeros_str}\n"
                results_text += "=" * 50 + "\n"
        
        self.ui_components['text_areas']['resultados'].delete("0.0", "end")
        self.ui_components['text_areas']['resultados'].insert("0.0", results_text)
    
    def update_number_colors(self):
        """Atualizar cores dos botões baseado nas frequências"""
        if self.stats_manager:
            for number, btn in self.number_buttons.items():
                if number not in self.game_manager.get_selected_numbers():
                    color = self.stats_manager.get_color_for_frequency(number)
                    btn.configure(fg_color=color)
    
    def update_statistics(self):
        """Atualizar texto de estatísticas"""
        if self.stats_manager:
            stats_text = self.stats_manager.get_summary_statistics()
            self.ui_components['text_areas']['estatísticas'].delete("0.0", "end")
            self.ui_components['text_areas']['estatísticas'].insert("0.0", stats_text)
    
    def search_results(self):
        """Buscar nos resultados"""
        if not self.stats_manager:
            messagebox.showwarning("Aviso", "Importe os resultados primeiro!")
            return
        
        try:
            search_type = self.ui_components['search_type'].get()
            search_value = self.ui_components['search_var'].get()
            
            # Realizar a busca
            filtered_df = self.search_manager.search(
                self.stats_manager.results_data,
                search_type,
                search_value
            )
            
            # Formatar e exibir resultados
            results_text = self.search_manager.format_search_results(filtered_df)
            self.ui_components['text_areas']['resultados'].delete("0.0", "end")
            self.ui_components['text_areas']['resultados'].insert("0.0", results_text)
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na pesquisa: {str(e)}")
    
    def export_simulations(self):
        """Exportar simulações para arquivo"""
        history_text = self.ui_components['text_areas']['histórico'].get("0.0", "end").strip()
        if not history_text:
            messagebox.showwarning("Aviso", "Nenhum jogo para exportar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Salvar simulações"
        )
        
        if file_path:
            error = self.data_manager.export_games(history_text, file_path)
            if error:
                messagebox.showerror("Erro", f"Erro ao exportar simulações: {error}")
            else:
                messagebox.showinfo("Sucesso", "Simulações exportadas com sucesso!")
    
    # --- NOVOS MÉTODOS PARA ESTRATÉGIAS AVANÇADAS ---
    
    def select_top_frequent(self):
        """Selecionar os números mais frequentes"""
        if not self.stats_manager:
            messagebox.showwarning("Aviso", "Importe os resultados primeiro!")
            return
        
        try:
            # Definir o topo como 30 (ou um valor personalizado)
            top_count = 30
            
            # Selecionar números mais frequentes
            self.filtered_numbers = self.strategy_manager.select_most_frequent(top_count)
            
            # Destacar os números selecionados
            self.update_button_appearances()
            
            messagebox.showinfo("Sucesso", f"Selecionados os {top_count} números mais frequentes")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar números: {str(e)}")
    
    def generate_strategic(self):
        """Gerar jogos usando estratégias avançadas"""
        if not self.stats_manager:
            messagebox.showwarning("Aviso", "Importe os resultados primeiro!")
            return
        
        # Verificar se temos números favoritos
        favorite_numbers = self.game_manager.parse_favorite_numbers(
            self.favorite_numbers_var.get()
        )
        
        if not favorite_numbers:
            messagebox.showwarning(
                "Aviso", 
                "Insira alguns números favoritos primeiro!"
            )
            return
        
        try:
            num_games = int(self.ui_components['num_games_var'].get())
            if num_games <= 0:
                raise ValueError("Número de jogos deve ser positivo")
            
            # Definir o gerenciador de estatísticas para o gerenciador de estratégia
            self.strategy_manager.set_stats_manager(self.stats_manager)
            
            # Gerar jogos estratégicos
            games = self.strategy_manager.generate_strategic_games(
                num_games=num_games,
                favorite_numbers=favorite_numbers,
                filtered_numbers=self.filtered_numbers
            )
            
            # Salvar jogos no histórico
            for game in games:
                self.save_game_to_history(game)
            
            # Mostrar o primeiro jogo
            if games:
                self.display_game(games[0])
                
            messagebox.showinfo(
                "Sucesso", 
                f"Gerados {len(games)} jogos estratégicos!"
            )
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar jogos: {str(e)}")
    
    def clear_filters(self):
        """Limpar todos os filtros aplicados"""
        self.filtered_numbers = set()
        
        # Resetar as aparências dos botões
        self.update_button_appearances()
        
        messagebox.showinfo("Sucesso", "Filtros limpos")


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
    
    def run(self):
        """Iniciar a aplicação"""
        self.window.mainloop()

if __name__ == "__main__":
    app = LotteryApp()
    app.run()