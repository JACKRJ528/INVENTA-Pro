import tkinter as tk
from tkinter import messagebox
import sqlite3
from ui.main_window import MainWindow

class LoginWindow(tk.Tk):

    def Teste(self):
        pass
    def __init__(self):
        super().__init__()
        self.title("Login - Inventa")
        self.centralizar_janela(400, 250)

        tk.Label(self, text="Usuário:").pack(pady=(50, 0))
        self.usuario_entry = tk.Entry(self)
        self.usuario_entry.pack()

        tk.Label(self, text="Senha:").pack(pady=(10, 0))
        self.senha_entry = tk.Entry(self, show="*")
        self.senha_entry.pack()

        tk.Button(self, text="Entrar", command=self.verificar_login).pack(pady=15)

    def centralizar_janela(self, largura, altura):
        self.update_idletasks()
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def verificar_login(self):
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()

        conn = sqlite3.connect("db/inventa.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT, senha TEXT)")
        conn.commit()

        # Cria usuário se não existir
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()

        # Verifica login
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        if cursor.fetchone():
            self.destroy()
            MainWindow().mainloop()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas.")
