import tkinter as tk
from tkinter import messagebox
import sqlite3

class RegistroEntrada(tk.Frame):
    def __init__(self, master, db_path):
        super().__init__(master)
        self.db_path = db_path
        self.pack(padx=20, pady=20)

        tk.Label(self, text="Escaneie o código de barras ou digite manualmente:").pack()
        self.entry = tk.Entry(self, font=("Arial", 18))
        self.entry.pack(pady=10)
        self.entry.focus()
        self.entry.bind("<Return>", self.verificar_codigo)

    def verificar_codigo(self, event=None):
        codigo = self.entry.get().strip()
        if not codigo:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM solicitacoes_compra WHERE codigo_rastreio = ? AND atendida = 0", (codigo,))
        resultado = cursor.fetchone()

        if resultado:
            solicitacao_id = resultado[0]
            cursor.execute("UPDATE solicitacoes_compra SET atendida = 1 WHERE id = ?", (solicitacao_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Solicitação {codigo} marcada como atendida.")
        else:
            messagebox.showwarning("Não encontrada", "Código não corresponde a uma solicitação pendente.")

        conn.close()
        self.entry.delete(0, tk.END)
        self.entry.focus()
