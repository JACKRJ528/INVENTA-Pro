import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter import font
import sqlite3


class UserManager:
    def conectar(self):
        return sqlite3.connect("db/inventa.db")

    def show(self, frame,toplevel):
        self.content_frame = frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.setup_header()
        self.setup_user_form()
        self.setup_user_list()

    def setup_header(self):
        header = tk.Frame(self.content_frame, bg="#2d2d2d")
        header.pack(fill=tk.X, pady=10)

        title = tk.Label(header, text="Gerenciar Usuários", bg="#2d2d2d", fg="#ffffff",
                         font=("Segoe UI", 18, "bold"))
        title.pack()

    def setup_user_form(self):
        form_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Nome:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.nome_entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=25)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Senha:", bg="#2d2d2d", fg="white", font=("Segoe UI", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.senha_entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=25, show="*")
        self.senha_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self.content_frame, bg="#2d2d2d")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Adicionar Usuário", font=("Segoe UI", 10), command=self.adicionar_usuario, bg="#007acc", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Remover Selecionado", font=("Segoe UI", 10), command=self.remover_usuario, bg="#cc0000", fg="white").pack(side=tk.LEFT, padx=10)

    def setup_user_list(self):
        self.tree = ttk.Treeview(self.content_frame, columns=("Nome",), show="headings")
        self.tree.heading("Nome", text="Nome")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("Treeview", background="#2d2d2d", foreground="#ffffff", fieldbackground="#2d2d2d", font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", "#007acc")])

        self.carregar_usuarios()

    def carregar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, senha TEXT)")
        cursor.execute("SELECT usuario FROM usuarios")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def adicionar_usuario(self):
        nome = self.nome_entry.get().strip()
        senha = self.senha_entry.get().strip()

        if not nome or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Usuário adicionado.")
        self.carregar_usuarios()
        self.nome_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)

    def remover_usuario(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um usuário para remover.")
            return

        nome = self.tree.item(selecionado[0])["values"][0]

        if messagebox.askyesno("Confirmar", f"Remover usuário '{nome}'?"):
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE nome = ?", (nome,))
            conn.commit()
            conn.close()
            self.carregar_usuarios()
            messagebox.showinfo("Sucesso", "Usuário removido.")
