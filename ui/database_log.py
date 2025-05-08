import os
import sqlite3
from tkinter import font
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, Toplevel



class Log_Manager:

    def conectar(self):
        return sqlite3.connect("db/inventa.db")

    def show(self,frame,toplevel):

        self.content_frame = frame

        self.setup_header()
        # Criar a árvore para exibir o histórico
        self.setup_treeview()

        self.carregar_historico()

    def setup_header(self):
        header_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)

        title_font = font.Font(family="Segoe UI", size=18, weight="bold")

        self.title_label = tk.Label(
            header_frame,
            text="Histórico do Estoque",
            font=title_font,
            bg="#2d2d2d",
            fg="#ffffff",
            anchor="w"
        )
        self.title_label.pack(side=tk.LEFT)

        # Espaço para busca
        search_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        search_frame.pack(fill=tk.X, pady=(0, 10), padx=20)

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",  # cursor branco
            relief=tk.FLAT
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))

        self.search_button = tk.Button(
            search_frame,
            text="Buscar",
            font=("Segoe UI", 10, "bold"),
            bg="#007acc",
            fg="#ffffff",
            activebackground="#005f99",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            command=self.buscar_historico  # Você vai precisar criar essa função!
        )
        self.search_button.pack(side=tk.LEFT)

    def setup_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2d2d2d",
                        foreground="#ffffff",
                        fieldbackground="#2d2d2d",
                        bordercolor="#1e1e1e",
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.map("Treeview", background=[('selected', '#007acc')])

        self.tree = ttk.Treeview(
            self.content_frame,
            columns=("ID","Produto", "Quantidade", "Data", "Tipo"),
            show="headings"
        )

        self.tree.heading("ID", text="ID")
        self.tree.heading("Produto", text="Produto")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Tipo", text="Tipo")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def buscar_historico(self):
        termo = self.search_entry.get().strip().lower()

        # Se nada foi digitado, recarrega todos os dados
        if not termo:
            self.carregar_historico()
            return

        # Limpa a árvore atual

        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']  # Pega os valores das colunas
            produto = str(valores[0]).lower()  # Considerando que Produto está na coluna 0

            if termo not in produto:
                self.tree.delete(item)

        return

    def carregar_historico(self):
        if self.tree.get_children() != 0:
            for item in self.tree.get_children():
                self.tree.delete(item)


        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT produto_id, nome_produto, quantidade, data_transacao, tipo_transacao FROM estoque_historico ORDER BY data_transacao DESC")

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def registrar_transacao(self,produto_id, nome_produto, quantidade, tipo_transacao):
        conn = self.conectar()
        cursor = conn.cursor()

        # Adicionar a transação no histórico
        cursor.execute('''
            INSERT INTO estoque_historico (produto_id, nome_produto, quantidade, data_transacao, tipo_transacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (produto_id, nome_produto, quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo_transacao))

        conn.commit()
        conn.close()
