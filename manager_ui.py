import random
import customtkinter as ctk
from typing import List, Dict, Set, Optional, Tuple, Callable


class UIManager:
    def __init__(self, master: ctk.CTk):
        self.master = master
        self.setup_window()
        
    def setup_window(self):
        """Configura a janela principal"""
        self.master.title("Gerador de Jogos - Mega Sena")
        self.master.geometry("1200x900")
        # self.master.geometry("1024x768")
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
        """Criar o painel de controle com entrada de quantidade e botões"""
        main_frame = ctk.CTkFrame(parent)
        main_frame.pack(pady=10, fill="x")
        
        # Frame superior para quantidade de jogos
        quantity_frame = ctk.CTkFrame(main_frame)
        quantity_frame.pack(pady=5, fill="x")
        
        # Label e entrada para quantidade
        num_games_label = ctk.CTkLabel(quantity_frame, text="Quantidade de Jogos:")
        num_games_label.pack(side="left", padx=5)
        
        num_games_var = ctk.StringVar(value="1")
        num_games_entry = ctk.CTkEntry(
            quantity_frame,
            textvariable=num_games_var,
            width=60
        )
        num_games_entry.pack(side="left", padx=5)
        
        # Frame inferior para botões
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(pady=5, fill="x")
        
        # Criar botões com configuração fornecida
        buttons = {}
        for text, command in buttons_config:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=16),
                width=150
            )
            btn.pack(side="left", padx=5)
            buttons[text] = btn
        
        # Adicionar botão Limpar à direita
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Limpar Histórico",
            command=buttons_config[-1][1] if len(buttons_config) > 0 else None,
            font=ctk.CTkFont(size=16),
            width=150,
            fg_color="red",
            hover_color="#b30000"  # Vermelho mais escuro para hover
        )
        clear_btn.pack(side="right", padx=5)
        buttons['Limpar Histórico'] = clear_btn
        
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
    
    # In manager_ui.py, add the following method to the UIManager class

    def create_favorites_panel(self, parent: ctk.CTkFrame, favorite_numbers_var: ctk.StringVar) -> ctk.CTkFrame:
        """Creates a panel for managing favorite numbers"""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5, fill="x")
        
        # Label
        favorites_label = ctk.CTkLabel(
            frame,
            text="Números Favoritos:",
            font=ctk.CTkFont(size=14)
        )
        favorites_label.pack(side="left", padx=5)
        
        # Entry for favorite numbers
        favorites_entry = ctk.CTkEntry(
            frame,
            textvariable=favorite_numbers_var,
            width=200,
            placeholder_text="Ex: 1, 2, 3, 4, 5, 6"
        )
        favorites_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        return frame

    # Modify the create_control_panel method to include the favorites panel
    def create_control_panel(self, parent: ctk.CTkFrame, buttons_config: list) -> Dict:
        """Criar o painel de controle com entrada de quantidade e botões organizados por categoria"""
        main_frame = ctk.CTkFrame(parent)
        main_frame.pack(pady=10, fill="x")
        
        # Frame superior para quantidade de jogos
        quantity_frame = ctk.CTkFrame(main_frame)
        quantity_frame.pack(pady=5, fill="x")
        
        # Label e entrada para quantidade
        num_games_label = ctk.CTkLabel(quantity_frame, text="Quantidade de Jogos:")
        num_games_label.pack(side="left", padx=5)
        
        num_games_var = ctk.StringVar(value="1")
        num_games_entry = ctk.CTkEntry(
            quantity_frame,
            textvariable=num_games_var,
            width=60
        )
        num_games_entry.pack(side="left", padx=5)
        
        # Organizar botões em categorias
        button_categories = {
            "importação": [],  # Grupo para importação/exportação
            "geração": [],     # Grupo para geração de jogos
            "seleção": [],     # Grupo para filtros e seleção
            "ações": []        # Grupo para outras ações
        }
        
        # Classificar botões em categorias baseado em seus nomes
        for text, command in buttons_config:
            if "Importar" in text or "Exportar" in text:
                button_categories["importação"].append((text, command))
            elif "Gerar" in text:
                button_categories["geração"].append((text, command))
            elif "Selecionar" in text or "Filtro" in text or "Marcar" in text:
                button_categories["seleção"].append((text, command))
            elif "Limpar" in text:
                button_categories["ações"].append((text, command))
            else:
                # Caso não se encaixe em nenhuma categoria específica
                button_categories["ações"].append((text, command))
        
        # Frame para os botões - primeira linha (importação e geração)
        buttons_frame1 = ctk.CTkFrame(main_frame)
        buttons_frame1.pack(pady=(5, 2), fill="x")
        
        # Frame para os botões - segunda linha (seleção e ações)
        buttons_frame2 = ctk.CTkFrame(main_frame)
        buttons_frame2.pack(pady=(2, 5), fill="x")
        
        buttons = {}
        
        # Adicionar botões da primeira linha (importação e geração)
        for text, command in button_categories["importação"] + button_categories["geração"]:
            btn = ctk.CTkButton(
                buttons_frame1,
                text=text,
                command=command,
                font=ctk.CTkFont(size=16),
                width=150
            )
            btn.pack(side="left", padx=5, pady=3)
            buttons[text] = btn
        
        # Adicionar botões da segunda linha (seleção e outras ações)
        for text, command in button_categories["seleção"] + button_categories["ações"]:
            # Se for botão de limpar, usar cor vermelha
            if "Limpar" in text:
                btn = ctk.CTkButton(
                    buttons_frame2,
                    text=text,
                    command=command,
                    font=ctk.CTkFont(size=16),
                    width=150,
                    fg_color="red",
                    hover_color="#b30000"  # Vermelho mais escuro para hover
                )
            else:
                btn = ctk.CTkButton(
                    buttons_frame2,
                    text=text,
                    command=command,
                    font=ctk.CTkFont(size=16),
                    width=150
                )
            btn.pack(side="left", padx=5, pady=3)
            buttons[text] = btn
        
        return {
            'num_games_var': num_games_var,
            'buttons': buttons
        }    
    
def create_strategy_panel(self, parent: ctk.CTkFrame, strategies_config: List[Tuple[str, Callable]]) -> Dict:
        """
        Cria um painel para estratégias avançadas
        
        Args:
            parent: Frame pai
            strategies_config: Lista de tuplas (texto, função) para os botões de estratégia
            
        Returns:
            Dicionário com componentes criados
        """
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, fill="x")
        
        # Frame para os controles de parâmetros
        params_frame = ctk.CTkFrame(frame)
        params_frame.pack(pady=5, fill="x")
        
        # Título do painel
        title_label = ctk.CTkLabel(
            params_frame,
            text="Estratégias Avançadas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=5, pady=5)
        
        # Parâmetros de estratégia
        cercar_var = ctk.StringVar(value="12")
        top_count_var = ctk.StringVar(value="30")
        recent_count_var = ctk.StringVar(value="5")
        
        # Frame para parâmetros na linha 1
        params_line1 = ctk.CTkFrame(params_frame)
        params_line1.pack(fill="x", pady=2)
        
        # Parâmetro: Números a cercar
        cercar_label = ctk.CTkLabel(params_line1, text="Números a cercar:")
        cercar_label.pack(side="left", padx=5)
        
        cercar_entry = ctk.CTkEntry(
            params_line1,
            textvariable=cercar_var,
            width=60
        )
        cercar_entry.pack(side="left", padx=5)
        
        # Parâmetro: Top mais frequentes
        top_label = ctk.CTkLabel(params_line1, text="Top mais frequentes:")
        top_label.pack(side="left", padx=5)
        
        top_entry = ctk.CTkEntry(
            params_line1,
            textvariable=top_count_var,
            width=60
        )
        top_entry.pack(side="left", padx=5)
        
        # Parâmetro: Jogos recentes a evitar
        recent_label = ctk.CTkLabel(params_line1, text="Evitar jogos recentes:")
        recent_label.pack(side="left", padx=5)
        
        recent_entry = ctk.CTkEntry(
            params_line1,
            textvariable=recent_count_var,
            width=60
        )
        recent_entry.pack(side="left", padx=5)
        
        # Checkboxes para opções de estratégia
        options_frame = ctk.CTkFrame(params_frame)
        options_frame.pack(fill="x", pady=2)
        
        use_parity_var = ctk.BooleanVar(value=True)
        parity_check = ctk.CTkCheckBox(
            options_frame,
            text="Filtrar por paridade",
            variable=use_parity_var
        )
        parity_check.pack(side="left", padx=5)
        
        use_decade_var = ctk.BooleanVar(value=True)
        decade_check = ctk.CTkCheckBox(
            options_frame,
            text="Filtrar por grupos de dezenas",
            variable=use_decade_var
        )
        decade_check.pack(side="left", padx=5)
        
        # Frame para os botões de estratégia
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(pady=5, fill="x")
        
        # Criar botões com configuração fornecida
        buttons = {}
        for text, command in strategies_config:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=14),
                width=180,
                height=35
            )
            btn.pack(side="left", padx=5, pady=5)
            buttons[text] = btn
        
        return {
            'cercar_var': cercar_var,
            'top_count_var': top_count_var,
            'recent_count_var': recent_count_var,
            'use_parity_var': use_parity_var,
            'use_decade_var': use_decade_var,
            'buttons': buttons
        }
    
def create_filter_info_panel(self, parent: ctk.CTkFrame) -> Dict:
    """
    Cria um painel para exibir informações de filtragem
    
    Args:
        parent: Frame pai
        
    Returns:
        Dicionário com componentes criados
    """
    frame = ctk.CTkFrame(parent)
    frame.pack(pady=5, fill="x")
    
    # Título do painel
    title_label = ctk.CTkLabel(
        frame,
        text="Informações de Filtragem",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    title_label.pack(anchor="w", padx=5, pady=5)
    
    # Área de texto para informações
    info_text = ctk.CTkTextbox(
        frame,
        height=60,
        font=ctk.CTkFont(size=12)
    )
    info_text.pack(padx=5, pady=5, fill="x")
    
    return {
        'info_text': info_text
    }

def update_filter_info(self, info_text: ctk.CTkTextbox, filter_info: Dict) -> None:
    """
    Atualiza o texto de informações de filtragem
    
    Args:
        info_text: Componente de texto a atualizar
        filter_info: Dicionário com informações de filtragem
    """
    info_text.delete("0.0", "end")
    
    if not filter_info:
        info_text.insert("0.0", "Nenhuma filtragem aplicada")
        return
        
    info_str = "Resumo da filtragem:\n"
    
    if 'initial_count' in filter_info and 'remaining' in filter_info:
        info_str += f"- Total de números: {filter_info['initial_count']}\n"
        
    if 'top_frequent' in filter_info:
        info_str += f"- Selecionados mais frequentes: {filter_info['top_frequent']}\n"
        
    if 'removed_recent' in filter_info:
        info_str += f"- Removidos de jogos recentes: {filter_info['removed_recent']}\n"
        
    if 'remaining' in filter_info:
        info_str += f"- Números após filtragem: {filter_info['remaining']}\n"
    
    info_text.insert("0.0", info_str)