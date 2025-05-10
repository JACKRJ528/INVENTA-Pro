import os
import sqlite3
import tkinter as tk
from ui.database_log import Log_Manager
from tkinter import ttk, messagebox, font


class PurchaseOrders:
    def conectar(self):
        return sqlite3.connect("db/inventa.db")

    def show(self, content_frame, toplevel):
        self.content_frame = content_frame
        self.ordens = []  # Exemplo: lista de tuplas (produto, quantidade)

        self.setup_header()
        self.setup_botoes()

        self.setup_treeview()
        self.carregar_ordens()

    def setup_header(self):
        header_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        header_frame.pack(fill=tk.X, pady=10)

        title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        tk.Label(header_frame, text="Ordens de Compra", bg="#2d2d2d", fg="white", font=title_font).pack()

    def setup_botoes(self):
        botoes_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        botoes_frame.pack(fill=tk.X, pady=5)

        btn_remover = tk.Button(botoes_frame, text="Definir como Atendida", command=self.definir_como_atendida,
                                bg="#444", fg="white", font=("Segoe UI", 10), relief="flat", padx=10, pady=5)
        btn_remover.pack(pady=5)

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

        self.tree = ttk.Treeview(self.content_frame,
                                 columns=("Codigo", "Nome", "Quantidade", "Unidade", "Valor Unitario", "Categoria"),
                                 show="headings")
        self.tree.heading("Codigo", text="Codigo")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.heading("Unidade", text="Unidade")
        self.tree.heading("Valor Unitario", text="Valor Unitario")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.selecionar_item)

    def setup_botoes(self):
        botoes_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        botoes_frame.pack(fill=tk.X, pady=5)

        self.btn_remover = tk.Button(botoes_frame, text="Definir como Atendida", command=self.definir_como_atendida,
                                bg="#444", fg="white", font=("Segoe UI", 10), relief="flat", padx=10, pady=5)

        self.btn_remover.pack(pady=5)

    def carregar_ordens(self):
        if self.tree.get_children() != 0:
            for item in self.tree.get_children():
                self.tree.delete(item)

        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT 
                        id,
                        codigo, 
                        nome, 
                        quantidade,
                        unidade, 
                        valor_unitario, 
                        categoria_id
                        FROM ordens_compra
                    """)

        for row in cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row[1:])

    def selecionar_item(self, event):
        item_id = self.tree.identify_row(event.y)  # identifica o item clicado baseado na posição Y

        if item_id:
            # Selecionou um item válido
            valores = self.tree.item(item_id, "values")
            if valores:
                self.item_selecionado = valores
                # Mostrar campo e botão
                self.btn_remover.pack(pady=5)

        else:
            # Clicou fora (área vazia)
            self.item_selecionado = None
            self.tree.selection_remove(self.tree.focus())  # força deselecionar o item
            # Esconder campo e botão
            self.btn_remover.pack_forget()

    def adicionar_ordem_compra(self, produto_id , nome_produto, quantidade):
        conn = sqlite3.connect("db/inventa.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ordens_compra (id_produto, nome_produto , quantidade) VALUES (?, ?, ?)", (produto_id, nome_produto, quantidade))
        conn.commit()

        self.save_log(produto_id,"OC: "+ nome_produto,quantidade,"ABERTURA" )

    def definir_como_atendida(self):
        resposta = messagebox.askyesno("Confirmar", "Deseja realmente marcar esta ordem como atendida?")
        if resposta:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ordens_compra WHERE id_produto = ? AND nome_produto = ? AND quantidade = ?", (self.item_selecionado[0],self.item_selecionado[1], self.item_selecionado[2],))

            conn.commit()

            self.add_oc_itens(self.item_selecionado[0], self.item_selecionado[2])

            self.save_log(self.item_selecionado[0], "OC: "+ self.item_selecionado[1], self.item_selecionado[2], "FECHAMENTO")

            messagebox.showinfo("Sucesso", "Ordem marcada como atendida.")

            self.carregar_ordens()


    def add_oc_itens(self,id, quant):
        from ui.database_manager import DB_Manager

        db = DB_Manager()
        db.add_by_name_id(id, quant)



    def save_log(self, produto_id, nome_produto, quantidade, tipo_transacao):
        log = Log_Manager()
        log.registrar_transacao(produto_id, nome_produto, quantidade, tipo_transacao)
