import tkinter as tk
from tkinter import font

from ui.dashboard import Dashboard
from ui.database_manager import DB_Manager
from ui.database_log import Log_Manager
from ui.user_manager import UserManager
from ui.purchase_orders import PurchaseOrders
from ui.converter import Converter
from ui.code_scanner import RegistroEntrada
from danfe.danfeextractor import DANFEImporter

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventa - Controle de Estoque")
        self.geometry("1280x720")

        self.tema_claro = False  # <- Modo escuro por padrão. Pode alternar com método futuro.

        # Definições de cores por tema
        self.definir_cores_tema()

        # Frame principal
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar_frame = tk.Frame(self.main_frame, bg=self.cor_sidebar, width=200)
        self.sidebar_frame.pack(side="left", fill=tk.BOTH)
        self.sidebar_frame.pack_propagate(False)

        title_font = font.Font(family="Segoe UI", size=18, weight="bold")

        title_label = tk.Label(self.sidebar_frame, text="Inventa", font=title_font,
                               bg=self.cor_titulo, fg=self.cor_texto)
        title_label.pack(pady=20, padx=10, fill=tk.X)

        # Conteúdo
        self.content_frame = tk.Frame(self.main_frame, bg=self.cor_fundo)
        self.content_frame.pack(side="left", fill=tk.BOTH, expand=True)

        self.create_options()

    def definir_cores_tema(self):
        if self.tema_claro:
            self.cor_fundo = "#f0f0f0"
            self.cor_sidebar = "#dcdcdc"
            self.cor_titulo = "#ffffff"
            self.cor_texto = "#000000"
            self.cor_botao = "#e0e0e0"
            self.cor_hover = "#cccccc"
            self.cor_alerta = "#ffcccc"
        else:
            self.cor_fundo = "#2d2d2d"
            self.cor_sidebar = "#1e1e1e"
            self.cor_titulo = "#2d2d2d"
            self.cor_texto = "#ffffff"
            self.cor_botao = "#2d2d2d"
            self.cor_hover = "#3a3a3a"
            self.cor_alerta = "#460000"

    def create_options(self):
        estilo_botao = {
            "bg": self.cor_botao,
            "fg": self.cor_texto,
            "activebackground": self.cor_hover,
            "activeforeground": self.cor_texto,
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 0,
            "font": ("Segoe UI", 10)
        }

        estilo_alerta = estilo_botao.copy()
        estilo_alerta["bg"] = self.cor_alerta

        botoes = [
            ("Estoque", "database"),
            ("Ordens Compras", "purchase"),
            ("Histórico", "datalog"),
            ("Análise", "dashboard"),
            ("Usuários", "usertab"),
            ("Exportar-Importar", "converter"),
            ("Importar DANFE", "danfeimporter"),
            ("Registrar Entrada", "codescanner")
        ]

        for texto, destino in botoes:
            b = tk.Button(self.sidebar_frame, text=texto,
                          command=lambda d=destino: self.change_menu(d),
                          **estilo_botao)
            b.pack(fill=tk.X, pady=5, padx=10)

        self.exit_button = tk.Button(self.sidebar_frame, text="Sair",
                                     command=self.quit,
                                     **estilo_alerta)
        self.exit_button.pack(fill=tk.X, pady=(0, 20), padx=10, side=tk.BOTTOM)

        self.change_menu("database")

    def change_menu(self, menuName):
        # 🔍 Melhor prática: destruir apenas se houver widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 🔄 Ideal: você pode guardar instâncias para evitar reconstrução se necessário
        match menuName:
            case "database":
                DB_Manager().show(self.content_frame, self)
            case "datalog":
                Log_Manager().show(self.content_frame, self)
            case "usertab":
                UserManager().show(self.content_frame, self)
            case "purchase":
                PurchaseOrders().show(self.content_frame, self)
            case "converter":
                Converter().show(self.content_frame, self)
            case "dashboard":
                Dashboard().show(self.content_frame, self)
            case "codescanner":
                RegistroEntrada().show(self.content_frame, self)
            case "danfeimporter":
                DANFEImporter().show(self.content_frame, self)

    # ✅ Função futura para alternar tema
    def alternar_tema(self):
        self.tema_claro = not self.tema_claro
        self.definir_cores_tema()
        self.destroy()
        self.__init__()  # Reinicia janela com novo tema (melhor: modularizar futura troca em tempo real)

