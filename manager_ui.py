import customtkinter as ctk
from typing import Dict, Callable

class UIManager:
    def __init__(self, master: ctk.CTk):
        self.master = master
        self.setup_window()
        
    def setup_window(self):
        """Configura a janela principal"""
        self.master.title("Gerador de Jogos - Mega Sena")
        self.master.geometry("1200x900")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")
    
    def create_main_frame(self) -> ctk.CTkFrame:
        """Cria e retorna o frame principal"""
        main_frame = ctk.CTkFrame(self.master)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        return main_frame
    
    def create_title(self, parent: ctk.CTkFrame) -> ctk.CTkLabel:
        """Cria e retorna o título"""
        title = ctk.CTkLabel(
            parent,
            text="Mega Sena - Gerador de Jogos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=10)
        return title
    
    def create_number_display(self, parent: ctk.CTkFrame, num_labels: int = 6) -> list:
        """Cria e retorna os labels para exibição dos números"""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10)
        
        labels = []
        for _ in range(num_labels):
            label = ctk.CTkLabel(
                frame,
                text="00",
                font=ctk.CTkFont(size=20, weight="bold"),
                width=60,
                height=60,
                fg_color=("gray75", "gray25"),
                corner_radius=30
            )
            label.pack(side="left", padx=5)
            labels.append(label)
        
        return labels
    
    def create_number_grid(self, parent: ctk.CTkFrame, command: Callable) -> Dict[int, ctk.CTkButton]:
        """Cria e retorna o grid de botões numéricos"""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="x")
        
        buttons = {}
        for i in range(60):
            number = i + 1
            row = i // 10
            col = i % 10
            
            btn = ctk.CTkButton(
                frame,
                text=f"{number:02d}",
                width=50,
                height=50,
                font=ctk.CTkFont(size=14),
                command=lambda n=number: command(n)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            buttons[number] = btn
        
        return buttons
    
    def create_control_panel(self, parent: ctk.CTkFrame, buttons_config: list) -> Dict:
        """Cria o painel de controle com entrada de quantidade e botões"""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, fill="x")
        
        # Quantidade de jogos
        num_games_label = ctk.CTkLabel(frame, text="Quantidade de Jogos:")
        num_games_label.pack(side="left", padx=5)
        
        num_games_var = ctk.StringVar(value="1")
        num_games_entry = ctk.CTkEntry(
            frame,
            textvariable=num_games_var,
            width=60
        )
        num_games_entry.pack(side="left", padx=5)
        
        # Botões
        buttons = {}
        for text, command in buttons_config:
            btn = ctk.CTkButton(
                frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=16),
                width=150
            )
            btn.pack(side="left", padx=5)
            buttons[text] = btn
        
        return {
            'num_games_var': num_games_var,
            'buttons': buttons
        }
    
    def create_tabs(self, parent: ctk.CTkFrame) -> Dict:
        """Cria e retorna as abas de histórico, resultados e estatísticas"""
        notebook = ctk.CTkTabview(parent)
        notebook.pack(pady=10, fill="both", expand=True)
        
        tabs = ["Histórico", "Resultados", "Estatísticas"]
        for tab in tabs:
            notebook.add(tab)
        
        text_areas = {}
        for tab in tabs:
            text_area = ctk.CTkTextbox(
                notebook.tab(tab),
                font=ctk.CTkFont(size=14)
            )
            text_area.pack(padx=10, pady=5, fill="both", expand=True)
            text_areas[tab.lower()] = text_area
        
        return {
            'notebook': notebook,
            'text_areas': text_areas
        }
    
    def create_search_panel(self, parent: ctk.CTkFrame, search_command: Callable) -> Dict:
        """Cria o painel de busca"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)
        
        search_var = ctk.StringVar()
        search_type = ctk.StringVar(value="Concurso")
        
        # Label
        search_label = ctk.CTkLabel(frame, text="Pesquisar por:")
        search_label.pack(side="left", padx=5)
        
        # Function to clear search field when type changes
        def on_type_change(choice):
            search_var.set("")  # Clear search field
            search_type.set(choice)  # Update search type
        
        # Combo
        search_options = ["Concurso", "Ano", "Mês"]
        search_combo = ctk.CTkOptionMenu(
            frame,
            values=search_options,
            variable=search_type,
            width=100,
            command=on_type_change  # Add type change handler
        )
        search_combo.pack(side="left", padx=5)
        
        # Entry with Enter key binding
        search_entry = ctk.CTkEntry(
            frame,
            textvariable=search_var,
            width=150
        )
        search_entry.pack(side="left", padx=5)
        # Bind Enter key to search command
        search_entry.bind('<Return>', lambda event: search_command())
        
        # Button
        search_button = ctk.CTkButton(
            frame,
            text="Buscar",
            command=search_command,
            width=100
        )
        search_button.pack(side="left", padx=5)
        
        return {
            'search_var': search_var,
            'search_type': search_type
        }