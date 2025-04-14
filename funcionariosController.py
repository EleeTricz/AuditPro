import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import psycopg2

# Configuração do banco
DB_CONFIG = {
    'dbname': 'auditoria_documentos',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def conectar_banco():
    return psycopg2.connect(**DB_CONFIG)

def carregar_funcionarios():
    conn = conectar_banco()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, data_admissao FROM funcionarios")
    funcionarios = cur.fetchall()
    conn.close()
    return funcionarios

def atualizar_funcionario():
    try:
        id_func = entry_id.get()
        nova_data = entry_data.get()
        if not id_func or not nova_data:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("UPDATE funcionarios SET data_admissao = %s WHERE id = %s", (nova_data, id_func))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Data de admissão atualizada!")
        atualizar_lista()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar: {e}")

def adicionar_funcionario():
    try:
        nome = entry_nome.get()
        data_admissao = entry_data.get()
        if not nome or not data_admissao:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("INSERT INTO funcionarios (nome, data_admissao) VALUES (%s, %s)", (nome, data_admissao))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Funcionário cadastrado!")
        atualizar_lista()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar: {e}")

def excluir_funcionario():
    try:
        id_func = entry_id.get()
        if not id_func:
            messagebox.showwarning("Aviso", "Informe o ID do funcionário!")
            return
        conn = conectar_banco()
        cur = conn.cursor()
        cur.execute("DELETE FROM funcionarios WHERE id = %s", (id_func,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Funcionário excluído!")
        atualizar_lista()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir: {e}")

def atualizar_lista():
    for item in tree.get_children():
        tree.delete(item)
    for funcionario in carregar_funcionarios():
        tree.insert("", "end", values=funcionario)

# Criando janela principal
root = tb.Window(themename="superhero")
root.title("Gestão de Funcionários")
root.geometry("600x400")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Tabela
columns = ("ID", "Nome", "Data de Admissão")
tree = ttk.Treeview(frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(pady=10, fill="both", expand=True)

# Campos de entrada
entry_id = ttk.Entry(frame, width=10)
entry_id.pack(side="left", padx=5)
entry_id.insert(0, "ID")

entry_nome = ttk.Entry(frame, width=20)
entry_nome.pack(side="left", padx=5)
entry_nome.insert(0, "Nome")

entry_data = ttk.Entry(frame, width=15)
entry_data.pack(side="left", padx=5)
entry_data.insert(0, "Data (AAAA-MM-DD)")

# Botões
ttk.Button(frame, text="Atualizar", command=atualizar_funcionario).pack(side="left", padx=5)
ttk.Button(frame, text="Adicionar", command=adicionar_funcionario).pack(side="left", padx=5)
ttk.Button(frame, text="Excluir", command=excluir_funcionario).pack(side="left", padx=5)

# Carregar funcionários
atualizar_lista()

root.mainloop()
