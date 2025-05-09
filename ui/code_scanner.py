import tkinter as tk
from tkinter import messagebox
import sqlite3

class RegistroEntrada:
    def conectar(self):
        return sqlite3.connect("db/inventa.db")
    def show(self, content_frame, toplevel):

        self.content_frame = content_frame
        self.toplevel = toplevel

        tk.Label(self.content_frame, text="Escaneie o código de barras ou digite manualmente:").pack()
        self.entry = tk.Entry(self.content_frame, font=("Arial", 18))
        self.entry.pack(pady=10)
        self.entry.focus()
        self.entry.bind("<Return>", self.verificar_codigo)

    def verificar_codigo(self, event=None):
        codigo = self.entry.get().strip()
        if not codigo:
            return

        conn = self.conectar()
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
