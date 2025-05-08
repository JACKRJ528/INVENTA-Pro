import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "inventa.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = conectar()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    # Tabela de ordem de compra
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordens_compra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_produto INTEGER NOT NULL,
                nome_produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL
            )
        ''')



    """
    cursor.execute("ALTER TABLE ordens_compra RENAME COLUMN id_produto TO categoria;")
    
    cursor.execute(""
            ALTER TABLE ordens_compra ADD COLUMN id_produto INTEGER NOT NULL;
    "")
    
    
    """

    # Tabela de categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')

    # Tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    # Tabela de atributos por categoria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atributos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER,
            nome_atributo TEXT NOT NULL,
            UNIQUE(categoria_id, nome_atributo),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    # Tabela de valores preenchidos dos produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valores_atributos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            nome_atributo TEXT NOT NULL,
            valor TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            nome_produto TEXT,
            quantidade INTEGER,
            data_transacao TEXT,
            tipo_transacao TEXT,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    """)

    # Criar usuário admin padrão
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "1234"))

    conn.commit()
    conn.close()

def obter_categorias():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
    categorias = cursor.fetchall()
    conn.close()
    return categorias

def adicionar_categoria(nome):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # categoria já existe
    conn.close()

def obter_produtos_por_categoria(nome_categoria):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorias WHERE nome = ?", (nome_categoria,))
    categoria = cursor.fetchone()
    if not categoria:
        conn.close()
        return []

    categoria_id = categoria[0]
    cursor.execute("SELECT id, nome FROM produtos WHERE categoria_id = ?", (categoria_id,))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def obter_atributos_da_categoria(categoria_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM atributos WHERE categoria_id = ?", (categoria_id,))
    atributos = cursor.fetchall()
    conn.close()
    return atributos

def salvar_valores_produto(produto_id, valores_dict):
    conn = conectar()
    cursor = conn.cursor()
    for atributo_id, valor in valores_dict.items():
        cursor.execute('''
            INSERT OR REPLACE INTO valores_produto (produto_id, atributo_id, valor)
            VALUES (?, ?, ?)
        ''', (produto_id, atributo_id, valor))
    conn.commit()
    conn.close()

def adicionar_atributo_a_categoria(nome_categoria, nome_atributo):
    categoria_id = obter_categoria_id(nome_categoria)
    if not categoria_id:
        raise ValueError(f"A categoria '{nome_categoria}' não foi encontrada.")

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            INSERT INTO atributos (categoria_id, nome_atributo)
            VALUES (?, ?)
        """, (categoria_id, nome_atributo))
        conexao.commit()
    except sqlite3.IntegrityError:
        pass  # Atributo já existe para esta categoria
    finally:
        conexao.close()