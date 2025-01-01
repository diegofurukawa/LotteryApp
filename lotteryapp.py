import customtkinter as ctk
from tkinter import messagebox, filedialog

from manager_ui import UIManager
from manager_data import DataManager
from manager_game import GameManager
from lottery_statistics import LotteryStatistics
from manager_search import SearchManager

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
        
        # Armazenar referências da UI
        self.number_buttons = {}
        self.number_labels = []
        self.ui_components = {}
        
        # Criar interface
        self.setup_ui()
    
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
        
        # Painel de controle
        buttons_config = [
            ("Gerar Números", self.generate_numbers),
            ("Gerar com Favoritos", self.generate_with_favorites),
            ("Marcar como Favorito", self.mark_as_favorite),
            ("Importar Resultados", self.import_results),
            ("Exportar Simulações", self.export_simulations)
        ]
        
        self.ui_components.update(
            self.ui_manager.create_control_panel(main_frame, buttons_config)
        )
        
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
            self.number_buttons[number].configure(fg_color="blue")
        else:
            self.number_buttons[number].configure(
                fg_color=self.get_number_color(number)
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
        """Gerar números considerando favoritos"""
        if not self.stats_manager:
            messagebox.showwarning("Aviso", "Importe os resultados primeiro!")
            return
        
        if not self.game_manager.get_favorite_numbers():
            messagebox.showwarning("Aviso", "Marque alguns números como favoritos primeiro!")
            return
        
        try:
            num_games = int(self.ui_components['num_games_var'].get())
            if num_games <= 0:
                raise ValueError("Número de jogos deve ser positivo")
            
            games = self.stats_manager.generate_smart_games(
                num_games,
                self.game_manager.get_favorite_numbers()
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
        
        # Atualizar aparência dos botões favoritos
        for num in self.game_manager.get_favorite_numbers():
            self.number_buttons[num].configure(border_color="gold", border_width=2)
        
        messagebox.showinfo("Sucesso", "Números marcados como favoritos!")
    
    def save_game_to_history(self, numbers):
        """Salvar jogo no histórico"""
        history_text = self.game_manager.format_game_for_history(numbers)
        self.ui_components['text_areas']['histórico'].insert("0.0", history_text + "\n")
    
    def display_game(self, numbers):
        """Mostrar jogo no display de números"""
        for label, number in zip(self.number_labels, numbers):
            label.configure(text=f"{number:02d}")
    
    def import_results(self):
        """Importar resultados da API"""
        def download():
            results_df, error = self.data_manager.download_results()
            
            if error:
                messagebox.showerror("Erro", f"Erro ao importar resultados: {error}")
                return
            
            # Criar gerenciador de estatísticas
            self.stats_manager = LotteryStatistics(results_df)
            
            # Atualizar interface
            self.update_results_display(results_df)
            self.update_number_colors()
            self.update_statistics()
            
            messagebox.showinfo("Sucesso", "Resultados importados com sucesso!")
        
        # Executar em uma thread separada
        import threading
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
                results_text += "-" * 50 + "\n"
        
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
    
    def run(self):
        """Iniciar a aplicação"""
        self.window.mainloop()

if __name__ == "__main__":
    app = LotteryApp()
    app.run()