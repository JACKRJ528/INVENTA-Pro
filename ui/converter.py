
import os
import csv
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime


class Converter:

    def show(self, content_frame, toplevel):

        self.content_frame = content_frame

        # self.limpar_frame()

        header = tk.Frame(self.content_frame, bg="#2d2d2d")
        header.pack(fill=tk.X, pady=10)
        titulo = tk.Label(header, text="Importar e Exportar Dados", font=("Segoe UI", 16, "bold"), fg="white", bg="#2d2d2d")
        titulo.pack()

        container = tk.Frame(self.content_frame, bg="#2d2d2d")
        container.pack(pady=20)

        # Exportar Histórico
        exportar_label = tk.Label(container, text="Exportar Histórico", font=("Segoe UI", 12), fg="white", bg="#2d2d2d")
        exportar_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        exportar_btn = tk.Button(container, text="Exportar para CSV", command=self.exportar_historico, bg="#007acc", fg="white", relief="flat")
        exportar_btn.grid(row=1, column=0, padx=10, pady=5)

        importarHis_btn = tk.Button(container, text="Importar Histórico", command=self.importar_historico, bg="#007acc", fg="white", relief="flat")
        importarHis_btn.grid(row=2, column=0, padx=10, pady=5)

        # Importar Tabela Externa
        importar_label = tk.Label(container, text="Importar Planilha Externa", font=("Segoe UI", 12), fg="white", bg="#2d2d2d")
        importar_label.grid(row=3, column=0, sticky="w", padx=10, pady=20)

        importar_btn = tk.Button(container, text="Importar Excel/CSV", command=self.importar_tabela, bg="#5aaf44", fg="white", relief="flat")
        importar_btn.grid(row=4, column=0, padx=10, pady=5)


    def exportar_historico(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_path:
                return

            conn = sqlite3.connect("db/inventa.db")
            cursor = conn.cursor()
            cursor.execute("SELECT produto, quantidade, data, tipo FROM historico")
            dados = cursor.fetchall()
            conn.close()

            with open(file_path, mode='w', newline='', encoding='utf-8') as arquivo_csv:
                writer = csv.writer(arquivo_csv)
                writer.writerow(["Produto", "Quantidade", "Data", "Tipo"])
                writer.writerows(dados)

            messagebox.showinfo("Exportação", "Histórico exportado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def importar_tabela(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return

        try:
            df = pd.read_csv(filepath)

            if 'nome' not in df.columns or 'quantidade' not in df.columns:
                messagebox.showerror("Erro", "O arquivo deve conter colunas 'nome' e 'quantidade'.")
                return

            nome_categoria = simpledialog.askstring("Categoria", "Digite o nome da categoria para os itens importados:")
            if not nome_categoria:
                messagebox.showerror("Erro", "Categoria não informada.")
                return

            nome_categoria = nome_categoria.strip().lower()
            df['nome'] = df['nome'].astype(str).str.strip().str.lower()

            conn = sqlite3.connect("db/inventa.db")
            cursor = conn.cursor()

            # Cria a categoria se não existir
            cursor.execute("SELECT id FROM categorias WHERE LOWER(nome) = ?", (nome_categoria,))
            categoria = cursor.fetchone()
            if not categoria:
                cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome_categoria,))
                conn.commit()
                categoria_id = cursor.lastrowid
            else:
                categoria_id = categoria[0]

            # Pega os atributos extras
            colunas_padrao = ['nome', 'quantidade']
            atributos = [col for col in df.columns if col not in colunas_padrao]

            # Garante que atributos existam na tabela de atributos
            for nome_atributo in atributos:
                cursor.execute("""
                    SELECT 1 FROM atributos WHERE categoria_id = ? AND LOWER(nome_atributo) = ?
                """, (categoria_id, nome_atributo.strip().lower()))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO atributos (categoria_id, nome_atributo) VALUES (?, ?)
                    """, (categoria_id, nome_atributo.strip().lower()))

            # Verifica e insere ou atualiza produtos
            for _, row in df.iterrows():
                nome = row['nome']
                quantidade = row['quantidade']
                atributos_dict = {col.strip().lower(): row[col] for col in atributos}

                # Verifica se o produto já existe na categoria (por nome)
                cursor.execute("""
                    SELECT id FROM produtos 
                    WHERE LOWER(nome) = ? AND categoria_id = ?
                """, (nome, categoria_id))
                produto = cursor.fetchone()

                if produto:
                    produto_id = produto[0]
                    # Atualiza a quantidade
                    cursor.execute("""
                        UPDATE produtos SET quantidade = ? WHERE id = ?
                    """, (quantidade, produto_id))
                    # Atualiza atributos
                    for attr, valor in atributos_dict.items():
                        cursor.execute("""
                            SELECT 1 FROM valores_atributos WHERE produto_id = ? AND LOWER(nome_atributo) = ?
                        """, (produto_id, attr))
                        if cursor.fetchone():
                            cursor.execute("""
                                UPDATE valores_atributos SET valor = ? WHERE produto_id = ? AND LOWER(nome_atributo) = ?
                            """, (valor, produto_id, attr))
                        else:
                            cursor.execute("""
                                INSERT INTO valores_atributos (produto_id, nome_atributo, valor) VALUES (?, ?, ?)
                            """, (produto_id, attr, valor))
                else:
                    # Insere como novo produto
                    self.inserir_produto_completo(nome, quantidade, categoria_id, atributos_dict, cursor)

            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Importação concluída com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar CSV: {e}")

    def inserir_produto_completo(self, nome, quantidade, categoria_id, atributos_dict, cursor):
        cursor.execute(
            "INSERT INTO produtos (nome, quantidade, categoria_id) VALUES (?, ?, ?)",
            (nome, quantidade, categoria_id)
        )
        produto_id = cursor.lastrowid

        for nome_atributo, valor in atributos_dict.items():
            cursor.execute(
                "INSERT INTO valores_atributos (produto_id, nome_atributo, valor) VALUES (?, ?, ?)",
                (produto_id, nome_atributo, str(valor))
            )

    def importar_historico(self):
        # Seleciona arquivo
        file_path = filedialog.askopenfilename(title="Selecione a planilha", filetypes=[("Planilhas", "*.csv *.xlsx")])
        if not file_path:
            return

        try:
            # Lê o arquivo (CSV ou Excel)
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            conn = sqlite3.connect("db/inventa.db")
            cursor = conn.cursor()

            for _, row in df.iterrows():
                nome_produto = row['nome_produto'].strip()
                categoria = row['categoria'].strip()
                quantidade = int(row['quantidade'])
                data_str = str(row['data_transacao']).strip()
                tipo = row['tipo_transacao'].strip().upper()

                # Converte data para o formato ISO
                try:
                    data_iso = datetime.strptime(data_str, "%d-%m-%Y").strftime("%Y-%m-%d")
                except:
                    try:
                        data_iso = datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y-%m-%d")
                    except:
                        messagebox.showerror("Erro", f"Data inválida: {data_str}")
                        continue

                if tipo not in ["ADICIONADO", "RETIRADO"]:
                    messagebox.showerror("Erro", f"Tipo de transação inválido: {tipo}")
                    continue

                # Verifica ou cria categoria
                cursor.execute("SELECT id FROM categorias WHERE nome = ?", (categoria,))
                cat = cursor.fetchone()
                if not cat:
                    cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (categoria,))
                    categoria_id = cursor.lastrowid
                else:
                    categoria_id = cat[0]

                # Verifica ou cria produto
                cursor.execute("SELECT id, quantidade FROM produtos WHERE nome = ? AND categoria_id = ?",
                               (nome_produto, categoria_id))
                produto = cursor.fetchone()
                if not produto:
                    cursor.execute("INSERT INTO produtos (nome, quantidade, categoria_id) VALUES (?, ?, ?)",
                                   (nome_produto, 0, categoria_id))
                    produto_id = cursor.lastrowid
                    quantidade_atual = 0
                else:
                    produto_id, quantidade_atual = produto

                # Aplica a transação ao estoque
                if tipo == "ADICIONADO":
                    nova_qtd = quantidade_atual + quantidade
                else:  # RETIRADO
                    if quantidade > quantidade_atual:
                        messagebox.showwarning("Aviso",
                                               f"Quantidade insuficiente para retirar {quantidade} de {nome_produto}. Pulando...")
                        continue
                    nova_qtd = quantidade_atual - quantidade

                # Atualiza produto
                cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_qtd, produto_id))

                # Registra no histórico
                cursor.execute("""
                    INSERT INTO estoque_historico (produto_id, nome_produto, quantidade, data_transacao, tipo_transacao)
                    VALUES (?, ?, ?, ?, ?)
                """, (produto_id, nome_produto, quantidade, data_iso, tipo))

            conn.commit()
            conn.close()
            messagebox.showinfo("Importação", "Histórico importado com sucesso.")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")





