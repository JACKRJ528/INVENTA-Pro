import tkinter as tk
from posixpath import curdir
from tkinter import ttk, messagebox, Toplevel
from tkinter import font
import sqlite3

from db.database import obter_categorias, obter_produtos_por_categoria, adicionar_categoria
from ui.database_log import Log_Manager
from ui.purchase_orders import PurchaseOrders
from ui.dashboard import Dashboard


class DB_Manager:

    def conectar(self):
        return sqlite3.connect("db/inventa.db")

    def show(self, frame, toplevel):
        self.content_frame = frame
        self.toplevel = toplevel
        self.conn = self.conectar()
        self.cursor = self.conn.cursor()

        self.setup_header()
        self.setup_inputs()
        self.setup_treeview()
        self.carregar_categorias()
        self.carregar_produtos()
        self.mostrar_categoria(self.categoria_combobox.get())

    def setup_header(self):
        title_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        title_frame.pack(fill=tk.X, pady=(20, 10), padx=20)

        title_font = font.Font(family="Segoe UI", size=18, weight="bold")

        self.title_label = tk.Label(
            title_frame,
            text="Controle do Estoque",
            font=title_font,
            bg="#2d2d2d",
            fg="#ffffff",
            anchor="w"
        )
        self.title_label.pack(side=tk.LEFT)

        header_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        header_frame.pack(fill=tk.X, pady=10)

        self.label_categoria = tk.Label(header_frame, text="Categoria:", bg="#2d2d2d", fg="#ffffff")
        self.label_categoria.pack(side=tk.LEFT, padx=(0, 10))

        self.categoria_var = tk.StringVar()
        self.categoria_combobox = ttk.Combobox(header_frame, textvariable=self.categoria_var, state="readonly")
        self.categoria_combobox.pack(side=tk.LEFT)
        self.categoria_combobox.bind("<<ComboboxSelected>>", self.carregar_campos_dinamicos)

        self.btn_nova_categoria = tk.Button(
            header_frame,
            text="Nova Categoria",
            bg="#4CAF50",
            fg="#ffffff",
            command=self.nova_categoria
        )
        self.btn_nova_categoria.pack(side=tk.LEFT, padx=10)

        self.refresh_button = tk.Button(
            header_frame,
            text="Atualizar Lista",
            bg="#007acc",
            fg="#ffffff",
            command=lambda: self.mostrar_categoria(self.categoria_combobox.get())
        )
        self.refresh_button.pack(side=tk.LEFT, padx=10)

        self.quantidade_label = tk.Label(header_frame, text="Quantidade para remover:")
        self.quantidade_label.pack_forget()

        self.quantidade_entry = tk.Entry(header_frame, width=10)
        self.quantidade_entry.pack_forget()

        self.confirmar_button = tk.Button(
            header_frame,
            text="Confirmar Remoção",
            command=self.remover_quantidade,
            bg="#460000",
            fg="#ffffff",
            activebackground="#3a3a3a",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 10)
        )
        self.confirmar_button.pack_forget()

        self.oc_button = tk.Button(header_frame, text="Gerar Ordem Compra")
        self.oc_button.pack_forget()

        self.item_selecionado = None

    def setup_inputs(self):
        self.entry_frame = tk.Frame(self.content_frame, bg="#1e1e1e")
        self.entry_frame.pack(fill=tk.X, pady=(10, 0))

        self.canvas = tk.Canvas(
            self.entry_frame,
            bg="#2d2d2d",
            height=40,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side="top", fill="x", expand=False)

        self.scrollbar = tk.Scrollbar(
            self.entry_frame,
            orient="horizontal",
            command=self.canvas.xview,
            bg="#1e1e1e",
            troughcolor="#1e1e1e",
            activebackground="#3c3c3c",
            relief="flat"
        )
        self.scrollbar.pack(side="top", fill="x")

        self.frame_inputs = tk.Frame(self.canvas, bg="#2d2d2d")
        self.canvas.create_window((0, 0), window=self.frame_inputs, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.frame_inputs.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

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

        self.tree = ttk.Treeview(self.content_frame, columns=("Nome", "Quantidade", "Categoria"), show="headings")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.selecionar_item)

    def carregar_produtos(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("""
            SELECT produtos.id, produtos.nome, produtos.quantidade, categorias.nome 
            FROM produtos
            LEFT JOIN categorias ON produtos.categoria_id = categorias.id
        """)
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row[1:])


    def selecionar_item(self, event):
        item_id = self.tree.identify_row(event.y)  # identifica o item clicado baseado na posição Y

        def confirmar_ordem():
            qtd = self.entry_qtd.get().strip()
            if not qtd.isdigit():
                messagebox.showerror("Erro", "Informe uma quantidade válida.")
                return
            self.cursor.execute("SELECT id FROM categorias WHERE nome = ?",(self.categoria_combobox.get(),))
            categID = self.cursor.fetchall()

            self.cursor.execute("SELECT id FROM produtos WHERE nome = ? AND categoria_id = ?",(self.nome_item,categID[0][0],))
            p_id = self.cursor.fetchall()


            self.adicionar_ordem_compra(p_id[0][0],self.nome_item, int(qtd))

            messagebox.showinfo("Sucesso", "Ordem gerada com sucesso!")

            self.popup.destroy()

        def mostrar_ordem():

            self.nome_item = valores[1]

            self.popup = tk.Toplevel(self.toplevel)
            self.popup.title("Gerar Ordem de Compra")
            self.popup.geometry("300x200")
            self.popup.configure(bg="#2d2d2d")
            self.popup.transient(self.toplevel)
            self.popup.grab_set()

            tk.Label(self.popup, text=f"Produto: {self.nome_item}", bg="#2d2d2d", fg="white", font=("Segoe UI", 12)).pack(pady=10)

            tk.Label(self.popup, text="Quantidade:", bg="#2d2d2d", fg="white").pack()
            self.entry_qtd = tk.Entry(self.popup)
            self.entry_qtd.pack(pady=5)

            tk.Button(self.popup, text="Confirmar", command=confirmar_ordem).pack(pady=10)


        if item_id:
            # Selecionou um item válido
            valores = self.tree.item(item_id, "values")
            if valores:
                self.item_selecionado = valores
                # Mostrar campo e botão
                self.quantidade_label.pack(side=tk.LEFT, padx=5)
                self.quantidade_entry.pack(side=tk.LEFT, padx=5)
                self.confirmar_button.pack(side=tk.LEFT, padx=5)
                self.oc_button.pack(side=tk.LEFT, padx=25)
                self.oc_button.config(command=mostrar_ordem)

        else:
            # Clicou fora (área vazia)
            self.item_selecionado = None
            self.tree.selection_remove(self.tree.focus())  # força deselecionar o item
            # Esconder campo e botão
            self.quantidade_label.pack_forget()
            self.quantidade_entry.pack_forget()
            self.confirmar_button.pack_forget()

    def remover_quantidade(self):
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Nenhum item selecionado.")
            return

        try:
            quantidade_remover = int(self.quantidade_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido!")
            return

        id_produto = self.item_selecionado[0]

        # Buscar a quantidade diretamente no banco
        self.cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (id_produto,))
        resultado = self.cursor.fetchone()

        if not resultado:
            messagebox.showerror("Erro", "Produto não encontrado no banco de dados.")
            return

        quantidade_atual = int(resultado[0])

        if quantidade_remover >= quantidade_atual:
            # Remover produto do banco
            self.cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
            self.conn.commit()
            messagebox.showinfo("Item removido", "A quantidade removida é igual ou maior ao estoque.\nO item foi excluído!")
            self.save_log(id_produto,self.item_selecionado[1],quantidade_remover,"RETIRADO")
            self.save_log(id_produto,self.item_selecionado[1],0,"ESGOTADO")
        else:
            # Atualizar a quantidade
            nova_quantidade = quantidade_atual - quantidade_remover
            self.cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, id_produto))
            self.conn.commit()
            messagebox.showinfo("Quantidade atualizada", f"Quantidade atualizada para {nova_quantidade}.")
            self.save_log(id_produto,self.item_selecionado[1],quantidade_remover,"RETIRADO")


        # Atualizar a tabela
        self.quantidade_label.pack_forget()
        self.quantidade_entry.pack_forget()
        self.confirmar_button.pack_forget()
        self.quantidade_entry.delete(0, tk.END)
        self.item_selecionado = None
        self.carregar_produtos()
        self.mostrar_categoria(self.categoria_combobox.get())

    def add_by_name_id(self, p_id, qnt):

        conn = self.conectar()
        cursor = conn.cursor()
        print(qnt)
        # Atualiza somando a quantidade
        cursor.execute("""
            UPDATE produtos 
            SET quantidade = quantidade + ? 
            WHERE id = ?
        """, (int(qnt), int(p_id)))

        conn.commit()
        conn.close()

    def adicionar_produto(self, categoria_id, atributos):
        nome = self.nome_entry.get().strip()
        qtd = self.qtd_entry.get().strip()

        if not nome or not qtd:
            messagebox.showwarning("Campos vazios", "Preencha todos os campos obrigatorios: NOME E QUANTIDADE.")
            return

        try:
            qtd = int(qtd)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser número inteiro.")
            return

        # Verificar se o produto já existe
        self.cursor.execute("""
            SELECT id, quantidade FROM produtos
            WHERE LOWER(nome) = LOWER(?) AND categoria_id = ?
        """, (nome, categoria_id))
        resultado = self.cursor.fetchone()

        if resultado:
            # Produto já existe: atualizar a quantidade
            produto_id, qtd_atual = resultado
            nova_qtd = qtd_atual + qtd
            self.cursor.execute("""
                UPDATE produtos SET quantidade = ? WHERE id = ?
            """, (nova_qtd, produto_id))
            self.conn.commit()
            self.save_log(produto_id, nome, qtd, "ADICIONADO")
        else:
            # Produto não existe: inserir novo
            self.cursor.execute(
                "INSERT INTO produtos (nome, quantidade, categoria_id) VALUES (?, ?, ?)",
                (nome, qtd, categoria_id)
            )
            produto_id = self.cursor.lastrowid
            self.conn.commit()
            self.save_log(produto_id, nome, qtd, "ADICIONADO")

            # Inserir os atributos personalizados
            for atributo in atributos:
                entrada = self.inputs_atributos.get(atributo)
                if entrada:
                    valor = entrada.get().strip()
                    if valor:
                        self.salvar_valores_personalizados(produto_id, atributo, valor)

        self.conn.commit()
        self.mostrar_categoria(self.categoria_combobox.get())

    def adicionar_ordem_compra(self, categ, nome_produto, quantidade):
        po = PurchaseOrders()
        po.adicionar_ordem_compra(categ,nome_produto, quantidade)

    def carregar_categorias(self):
        categorias = obter_categorias()
        self.categoria_combobox["values"] = [c[1] for c in categorias]

        if categorias:
            self.categoria_combobox.current(0)
            self.mostrar_categoria(self.categoria_combobox.get())

    def mostrar_categoria(self, categoria_nome):
        self.tree.delete(*self.tree.get_children())

        conn = sqlite3.connect("db/inventa.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorias WHERE nome = ?", (categoria_nome,))
        resultado = cursor.fetchone()
        if not resultado:
            return
        categoria_id = resultado[0]

        cursor.execute("SELECT id, nome, quantidade FROM produtos WHERE categoria_id = ?", (categoria_id,))
        produtos_infos = cursor.fetchall()

        cursor.execute("SELECT nome_atributo FROM atributos WHERE categoria_id = ?", (categoria_id,))
        atributos = [row[0] for row in cursor.fetchall()]

        self.tree["columns"] = ["ID"] + ["Nome"] + atributos + ["Quantidade"]
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, anchor="w", width=120)

        for pid, nome_produto, quantidade in produtos_infos:
            cursor.execute("SELECT nome_atributo, valor FROM valores_atributos WHERE produto_id = ?", (pid,))
            dados = {nome: valor for nome, valor in cursor.fetchall()}
            linha = [pid] + [nome_produto] + [dados.get(attr, "") for attr in atributos] + [quantidade]
            self.tree.insert("", tk.END, values=linha)

        conn.close()

        for widget in self.frame_inputs.winfo_children():
            widget.destroy()

        self.inputs_atributos = {}

        self.add_input("Nome:", "nome")
        for attr in atributos:
            self.add_input(f"{attr}:", attr)
        self.add_input("Quantidade:", "quantidade")

        adicionar_button = tk.Button(self.frame_inputs, text="Adicionar Produto", bg="#4CAF50", fg="#ffffff",
                                     command=lambda: self.adicionar_produto(categoria_id, atributos))
        adicionar_button.pack(side=tk.LEFT, padx=10)

    def add_input(self, label_text, key):
        label = tk.Label(self.frame_inputs, text=label_text, bg="#2d2d2d", fg="#ffffff")
        label.pack(side=tk.LEFT, padx=5)
        entry = tk.Entry(self.frame_inputs, width=15, bg="#3c3c3c", fg="#ffffff", insertbackground="#ffffff")
        entry.pack(side=tk.LEFT, padx=5)
        if key == "nome":
            self.nome_entry = entry
        elif key == "quantidade":
            self.qtd_entry = entry
        self.inputs_atributos[key] = entry

    def nova_categoria(self):
        def adicionar_atributo():
            nome = atributo_entry.get().strip()
            if nome:
                nome = nome.lower()
                nome = nome.replace(" ", "_")

                atributos.append(nome)
                atributos_listbox.insert(tk.END, nome)
                atributo_entry.delete(0, tk.END)

        def salvar_categoria():
            nome_categoria = nome_entry.get().strip()
            if not nome_categoria:
                messagebox.showerror("Erro", "Nome da categoria não pode estar vazio.")
                return
            if not atributos:
                messagebox.showerror("Erro", "Adicione pelo menos um atributo.")
                return

            adicionar_categoria(nome_categoria)
            categoria_id = self.obter_categoria_id(nome_categoria)

            conn = sqlite3.connect("db/inventa.db")
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO atributos (categoria_id, nome_atributo) VALUES (?, ?)",
                [(categoria_id, nome_atributo) for nome_atributo in atributos]
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Categoria criada com sucesso!")
            janela.destroy()

            self.save_log(0,"CATEG: "+ nome_categoria,1,"CRIADA")

            self.carregar_categorias()

        atributos = []

        janela = Toplevel(self.toplevel)
        janela.title("Criar Nova Categoria")
        janela.geometry("400x400")
        janela.configure(bg="#2d2d2d")
        janela.transient(self.toplevel)
        janela.grab_set()

        frame_nome = tk.Frame(janela, bg="#2d2d2d")
        frame_nome.pack(pady=10)
        tk.Label(frame_nome, text="Nome da Categoria:", bg="#2d2d2d", fg="#ffffff").pack(anchor="w")
        nome_entry = tk.Entry(frame_nome, width=40, bg="#3c3c3c", fg="#ffffff", insertbackground="#ffffff")
        nome_entry.pack()

        frame_atributo = tk.Frame(janela, bg="#2d2d2d")
        frame_atributo.pack(pady=10)
        tk.Label(frame_atributo, text="Novo Atributo:", bg="#2d2d2d", fg="#ffffff").pack(anchor="w")
        atributo_entry = tk.Entry(frame_atributo, width=30, bg="#3c3c3c", fg="#ffffff", insertbackground="#ffffff")
        atributo_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(frame_atributo, text="Adicionar", command=adicionar_atributo, bg="#007acc", fg="#ffffff").pack(side=tk.LEFT)

        tk.Label(janela, text="Atributos adicionados:", bg="#2d2d2d", fg="#ffffff").pack()
        atributos_listbox = tk.Listbox(janela, height=8, bg="#3c3c3c", fg="#ffffff")
        atributos_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        tk.Button(janela, text="Salvar Categoria", command=salvar_categoria, bg="#4CAF50", fg="#ffffff").pack(pady=10)
    @staticmethod
    def obter_categoria_id(nome_categoria):
        conexao = sqlite3.connect("db/inventa.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM categorias WHERE nome = ?", (nome_categoria,))
        resultado = cursor.fetchone()
        conexao.close()
        return resultado[0] if resultado else None

    def obter_atributos_por_categoria(self, nome_categoria):
        categoria_id = self.obter_categoria_id(nome_categoria)
        if not categoria_id:
            print(f"ERRO AO OBTER ID DA CATEGORIA {nome_categoria}")
            return []

    def carregar_campos_dinamicos(self, event=None):
        categoria_selecionada = self.categoria_combobox.get()
        self.mostrar_categoria(categoria_selecionada)

    def salvar_valores_personalizados(self, produto_id, nome_atributo, valor):

        self.cursor.execute("""
            INSERT INTO valores_atributos (produto_id, nome_atributo, valor)
            VALUES (?, ?, ?)
        """, (produto_id, nome_atributo, valor))

    def save_log(self, produto_id, nome_produto, quantidade, tipo_transacao):
        log = Log_Manager()
        log.registrar_transacao(produto_id, nome_produto, quantidade, tipo_transacao)
