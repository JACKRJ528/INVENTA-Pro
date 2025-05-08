import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter import font
import sqlite3

from matplotlib.backend_bases import cursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
from tkcalendar import DateEntry

from ui.purchase_orders import PurchaseOrders

class Dashboard:

    def show(self, content_frame, toplevel):

        self.content_frame = content_frame
        self.root = toplevel
        # Frame para conteudo do cabeçario
        self.header_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        self.header_frame.pack(fill=tk.X, pady=10)

        # Frame para conteúdo da análise
        self.dashboard_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)



        # Apenas o cabeçario é fixo nessa janela
        title = tk.Label(self.header_frame, text="Dashboard do Estoque", bg="#2d2d2d", fg="#ffffff", font=("Segoe UI", 18, "bold"))
        title.pack(side=tk.LEFT, padx=20)

        self.btn_estquant = tk.Button(self.header_frame, text="Análise de Quantidade", command=self.analise_estoque_minima,
                                   bg="#3a3a3a", fg="white", font=("Segoe UI", 10), relief=tk.FLAT)
        self.btn_estquant.pack(side=tk.LEFT, padx=10)

        self.btn_fluxo = tk.Button(self.header_frame, text="Análise de Fluxo", command=self.mostrar_fluxo_estoque,
                                   bg="#3a3a3a", fg="white", font=("Segoe UI", 10), relief=tk.FLAT)
        self.btn_fluxo.pack(side=tk.LEFT, padx=10)

        self.botao_ordem_compra = tk.Button(
            self.header_frame, text="Gerar Ordem de Compra", bg="#007acc", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.abrir_ordem_compra_popup
        )
        self.botao_ordem_compra.pack_forget()  # Esconder inicialmente
        self.analise_estoque_minima()

    def ao_selecionar_item(self, event):
        selecionado = self.tree.identify_row(event.y)

        if selecionado:
            self.item_selecionado = self.tree.item(selecionado)['values']
            self.botao_ordem_compra.pack(pady=10)
        else:
            self.tree.selection_remove(self.tree.focus())
            self.botao_ordem_compra.pack_forget()
            if hasattr(self, 'item_selecionado'):
                del self.item_selecionado

    def limpar_frame(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

    def analise_estoque_minima(self):
        self.limpar_frame()

        self.tree = ttk.Treeview(self.dashboard_frame, columns=("Produto", "Categoria" , "Qtd", "Qtd Mín", "Status"), show="headings", selectmode="browse")
        self.tree.heading("Produto", text="Produto")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Qtd", text="Quantidade")
        self.tree.heading("Qtd Mín", text="Qtd. Mínima")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True)



        self.tree.bind("<ButtonRelease-1>", self.ao_selecionar_item)

        self.conn = sqlite3.connect("db/inventa.db")
        self.cursor = self.conn.cursor()

        # 1. Buscar categorias com o atributo "quantidade_minima"
        self.cursor.execute("SELECT DISTINCT categoria_id FROM atributos WHERE nome_atributo = ?", ('quantidade_minima',))
        categorias = self.cursor.fetchall()
        IDs = list(set(cat[0] for cat in categorias))
        produtos_info = []
        produtos = []
        if IDs:
            for id in IDs:
                self.cursor.execute("SELECT nome FROM categorias WHERE id = ?",(id,))
                nome = self.cursor.fetchall()

                self.cursor.execute(" SELECT id, nome, quantidade FROM produtos WHERE categoria_id = ?",(id,))
                for pd in self.cursor.fetchall():
                    temp = []

                    temp.append(pd[0])
                    temp.append(pd[1])
                    temp.append(nome[0][0])
                    temp.append(pd[2])
                    produtos.append(temp)

            for produto_id, nome, categoria , quantidade in produtos:
                    # 2. Buscar o valor da quantidade mínima
                    self.cursor.execute("""
                        SELECT valor
                        FROM valores_atributos
                        WHERE produto_id = ? AND nome_atributo = ?
                    """, (produto_id, 'quantidade_minima'))

                    resultado = self.cursor.fetchone()
                    if resultado:
                        try:
                            quantidade_minima = float(resultado[0])
                            produtos_info.append({
                                'nome': nome,
                                'categoria': categoria,
                                'quantidade': quantidade,
                                'quantidade_minima': quantidade_minima
                            })
                        except ValueError:
                            pass  # Ignorar se a quantidade mínima não for numérica


        for produto in produtos_info:
            quantidade = produto.get("quantidade")
            quantidade_minima = produto.get("quantidade_minima")

            if quantidade_minima == 0:
                status = "Sem mínimo"
            else:
                proporcao = quantidade / quantidade_minima
                if proporcao > 2:
                    status = "Superlotado"
                elif proporcao > 1.1:
                    status = "Pleno"
                elif proporcao >= 0.9:
                    status = "Suficiente"
                elif proporcao >= 0.5:
                    status = "Baixa"
                else:
                    status = "Esgotando"

            self.tree.insert("", "end", values=(
                produto.get("nome"),produto.get("categoria"), quantidade, quantidade_minima, status
            ))

    def abrir_ordem_compra_popup(self):
        if not hasattr(self, 'item_selecionado'):
            return
        valores = self.item_selecionado

        self.nome_item = valores[0]
        catg = valores[1]


        self.cursor.execute(" SELECT id FROM categorias WHERE nome = ?", (catg,))

        catgID = self.cursor.fetchall()

        self.cursor.execute("""
                                SELECT id
                                FROM produtos
                                WHERE nome = ? AND categoria_id = ?
                            """, (self.nome_item, catgID[0][0]))

        produto_id = self.cursor.fetchall()

        self.popup = tk.Toplevel(self.root)
        self.popup.title("Gerar Ordem de Compra")
        self.popup.geometry("300x200")
        self.popup.configure(bg="#2d2d2d")
        self.popup.transient(self.root)
        self.popup.grab_set()

        tk.Label(self.popup, text=f"Produto: {self.nome_item}", bg="#2d2d2d", fg="white", font=("Segoe UI", 12)).pack(
            pady=10)

        tk.Label(self.popup, text="Quantidade:", bg="#2d2d2d", fg="white").pack()
        self.entry_qtd = tk.Entry(self.popup)
        self.entry_qtd.pack(pady=5)


        def confirmar_ordem():
            try:
                quantidade = int(self.entry_qtd.get())
                if quantidade > 0:
                    self.adicionar_ordem_compra(produto_id[0][0], self.nome_item, quantidade)
                    messagebox.showinfo("Ordem Compra", "Ordem de Compra confirmada!")

                    self.popup.destroy()

            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida")
                self.popup.destroy()

        tk.Button(self.popup, text="Confirmar", command=confirmar_ordem).pack(pady=10)

    def mostrar_fluxo_estoque(self):
        from collections import defaultdict
        from datetime import datetime
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self.limpar_frame()

        # Pega categorias
        self.cursor.execute("SELECT id, nome FROM categorias")
        categorias = self.cursor.fetchall()
        nomes_categorias = [cat[1] for cat in categorias]
        categoria_map = {cat[1]: cat[0] for cat in categorias}

        filtro_frame = tk.Frame(self.dashboard_frame, bg="#2d2d2d")
        filtro_frame.pack(fill=tk.X, pady=10)

        # Categoria dropdown
        tk.Label(filtro_frame, text="Categoria:", bg="#2d2d2d", fg="white").pack(side=tk.LEFT, padx=5)
        categoria_var = tk.StringVar()
        categoria_combo = ttk.Combobox(filtro_frame, textvariable=categoria_var, values=nomes_categorias, width=20)
        categoria_combo.pack(side=tk.LEFT, padx=5)

        # Produto dropdown
        tk.Label(filtro_frame, text="Produto:", bg="#2d2d2d", fg="white").pack(side=tk.LEFT, padx=5)
        produto_var = tk.StringVar()
        produto_combo = ttk.Combobox(filtro_frame, textvariable=produto_var, values=[], width=20)
        produto_combo.pack(side=tk.LEFT, padx=5)

        def atualizar_produtos(*args):
            categoria_nome = categoria_var.get()
            categoria_id = categoria_map.get(categoria_nome)
            if categoria_id:
                self.cursor.execute("SELECT nome FROM produtos WHERE categoria_id = ?", (categoria_id,))
                produtos = self.cursor.fetchall()
                nomes = [p[0] for p in produtos]
                produto_combo['values'] = nomes
                produto_combo.set('')

        categoria_combo.bind("<<ComboboxSelected>>", atualizar_produtos)

        # Tipo de transação
        tk.Label(filtro_frame, text="Tipo:", bg="#2d2d2d", fg="white").pack(side=tk.LEFT, padx=5)
        tipo_var = tk.StringVar(value="Tudo")
        tipo_menu = ttk.Combobox(filtro_frame, textvariable=tipo_var, values=["Tudo", "Entrada", "Saída"], width=10)
        tipo_menu.pack(side=tk.LEFT, padx=5)

        # Data inicial/final
        tk.Label(filtro_frame, text="Data Inicial:", bg="#2d2d2d", fg="white").pack(side=tk.LEFT, padx=5)
        data_ini_entry = DateEntry(filtro_frame, date_pattern='dd-mm-yyyy', width=12)
        data_ini_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(filtro_frame, text="Data Final:", bg="#2d2d2d", fg="white").pack(side=tk.LEFT, padx=5)
        data_fim_entry = DateEntry(filtro_frame, date_pattern='dd-mm-yyyy', width=12)
        data_fim_entry.pack(side=tk.LEFT, padx=5)

        # Tabela
        tree = ttk.Treeview(self.dashboard_frame, columns=("Produto", "Quantidade", "Tipo", "Data"), show="headings")
        for col in ("Produto", "Quantidade", "Tipo", "Data"):
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        grafico_frame = tk.Frame(self.dashboard_frame, bg="#213f3f")
        grafico_frame.pack(fill=tk.BOTH, expand=True)

        def filtrar():
            nome = produto_var.get().strip()
            categoria = categoria_var.get().strip()
            tipo = tipo_var.get()
            data_ini = data_ini_entry.get_date().strftime("%Y-%m-%d")
            data_fim = data_fim_entry.get_date().strftime("%Y-%m-%d")

            query = "SELECT produto_id, nome_produto, quantidade, data_transacao, tipo_transacao FROM estoque_historico WHERE 1=1"
            params = []

            if nome:
                query += " AND nome_produto LIKE ?"
                params.append(f"%{nome}%")

            if categoria:
                categoria_id = categoria_map.get(categoria)
                query += " AND produto_id IN (SELECT id FROM produtos WHERE categoria_id = ?)"
                params.append(categoria_id)

            if tipo == "Entrada":
                query += " AND tipo_transacao = ?"
                params.append("ADICIONADO")
            elif tipo == "Saída":
                query += " AND tipo_transacao = ?"
                params.append("RETIRADO")
            else:
                query += " AND tipo_transacao IN (?, ?)"
                params.extend(["ADICIONADO", "RETIRADO"])

            if data_ini:
                query += " AND date(data_transacao) >= date(?)"
                params.append(data_ini)

            if data_fim:
                query += " AND date(data_transacao) <= date(?)"
                params.append(data_fim)

            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()

            for row in tree.get_children():
                tree.delete(row)

            for item in resultados:
                tree.insert("", tk.END, values=(item[1], item[2], item[4], item[3]))

            # Gráfico
            for widget in grafico_frame.winfo_children():
                widget.destroy()

            dados_brutos = defaultdict(list)

            for _, nome_produto, qtd, data, tipo_transacao in resultados:
                data_formatada = datetime.strptime(data.split(" ")[0], "%Y-%m-%d").date()
                if tipo_transacao.upper() == "ADICIONADO":
                    dados_brutos[data_formatada].append(qtd)
                elif tipo_transacao.upper() == "RETIRADO":
                    dados_brutos[data_formatada].append(-qtd)

            # Calcular saldo acumulado
            datas_ordenadas = sorted(dados_brutos.keys())
            quantidade_acumulada = 0
            datas = []
            quantidades = []

            for data in datas_ordenadas:
                for q in dados_brutos[data]:
                    quantidade_acumulada += q
                datas.append(data)
                quantidades.append(quantidade_acumulada)

            if datas and quantidades:
                fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
                ax.plot(datas, quantidades, marker='o', color='skyblue')
                ax.set_title("Fluxo de Estoque (Saldo Acumulado)")
                ax.set_xlabel("Data")
                ax.set_ylabel("Quantidade em Estoque")
                ax.grid(True)
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=grafico_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tk.Button(filtro_frame, text="Buscar", command=filtrar, bg="#007acc", fg="white").pack(side=tk.LEFT, padx=10)

    def adicionar_ordem_compra(self, categ, nome_produto, quantidade):
        po = PurchaseOrders()
        po.adicionar_ordem_compra(categ,nome_produto, quantidade)
