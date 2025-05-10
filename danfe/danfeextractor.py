import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import sqlite3

class DANFEImporter:
    def conectar(self):
        return sqlite3.connect("db/inventa.db")

    def show(self, content_frame, toplevel):
        self.content_frame = content_frame
        self.toplevel = toplevel
        self.produtos = []
        self.danfe_numero = ""

        self.content_frame.configure(bg="#2e2e2e")

        self.label_danfe = tk.Label(self.content_frame, text="Número da DANFE: --", bg="#2e2e2e", fg="white", font=("Arial", 12))
        self.label_danfe.pack(pady=5)

        self.btn_abrir = tk.Button(self.content_frame, text="Selecionar XML", command=self.abrir_xml, bg="#444", fg="white")
        self.btn_abrir.pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e")
        style.configure("Treeview.Heading", background="#444", foreground="white")

        self.tree = ttk.Treeview(self.content_frame, columns=("codigo", "nome", "quantidade", "unidade", "valor_unitario"), show="headings")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("unidade", text="Unidade")
        self.tree.heading("valor_unitario", text="Valor Unitário")
        self.tree.pack(pady=10, expand=True, fill=tk.BOTH)

        self.btn_salvar = tk.Button(self.content_frame, text="Salvar no banco", command=self.salvar_produtos, bg="#444", fg="white")
        self.btn_salvar.pack(pady=10)

    def abrir_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos XML", "*.xml")])
        if not file_path:
            return

        try:
            self.produtos, self.danfe_numero = self.extrair_itens_danfe(file_path)
            self.label_danfe.config(text=f"Número da DANFE: {self.danfe_numero}")

            for item in self.tree.get_children():
                self.tree.delete(item)

            for p in self.produtos:
                self.tree.insert("", tk.END, values=(p['codigo'], p['nome'], p['quantidade'], p['unidade'], p['valor_unitario']))

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar XML:\n{e}")

    def extrair_itens_danfe(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}

        danfe_numero = root.find(".//ns:nNF", ns).text

        produtos = []
        for det in root.findall(".//ns:det", ns):
            prod = det.find("ns:prod", ns)
            yet = False
            skip = False

            if skip == False:
                for produto in produtos:
                    if produto['codigo'] == prod.find("ns:cProd", ns).text:
                        produto['quantidade']+= float(prod.find("ns:qCom", ns).text)
                        yet = True

            if yet == False:
                produtos.append({
                    'codigo': prod.find("ns:cProd", ns).text,
                    'nome': prod.find("ns:xProd", ns).text,
                    'quantidade': float(prod.find("ns:qCom", ns).text),
                    'unidade': prod.find("ns:uCom", ns).text,
                    'valor_unitario': float(prod.find("ns:vUnCom", ns).text),
                    'categoria_id': danfe_numero
                })

        return produtos, danfe_numero

    def salvar_produtos(self):
        if not self.produtos:
            messagebox.showwarning("Aviso", "Nenhum produto para salvar.")
            return

        try:
            conn = self.conectar()
            cursor = conn.cursor()

            for item in self.produtos:
                cursor.execute("""
                    INSERT INTO ordens_compra (codigo, nome, quantidade, unidade, valor_unitario, categoria_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item['codigo'],
                    item['nome'],
                    item['quantidade'],
                    item['unidade'],
                    item['valor_unitario'],
                    item['categoria_id']
                ))

                try:
                    cursor.execute("""
                        INSERT INTO categorias (id, nome)
                        VALUES (?,?)
                    """, (
                        item['categoria_id'],
                        item['categoria_id']
                    ))
                except:
                    pass
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", f"{len(self.produtos)} produtos salvos com categoria_id = {self.danfe_numero}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar no banco:\n{e}")
