import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from main import processar_documentos
from check import gerar_relatorio

# Configuração do banco PostgreSQL
DB_CONFIG = {
    'dbname': 'auditoria_documentos',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def listar_documentos():
    """Função para listar todos os documentos cadastrados com filtros opcionais."""
    empresa_filtro = entry_empresa.get().strip()
    funcionario_filtro = entry_funcionario.get().strip()
    ordenar_por = combo_ordenacao.get()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        query = """
            SELECT e.nome AS empresa, 
                   CASE WHEN d.tipo IN ('FOLHA', 'FOLHA13') THEN 'TODOS' ELSE f.nome END AS funcionario, 
                   d.ano, d.mes, d.tipo 
            FROM documentos d
            JOIN empresas e ON d.empresa_id = e.id
            LEFT JOIN funcionarios f ON d.funcionario_id = f.id
        """
        params = []
        
        if empresa_filtro:
            query += " WHERE e.nome ILIKE %s"
            params.append(f"%{empresa_filtro}%")
        
        if funcionario_filtro:
            if empresa_filtro:
                query += " AND f.nome ILIKE %s"
            else:
                query += " WHERE f.nome ILIKE %s"
            params.append(f"%{funcionario_filtro}%")
        
        if ordenar_por == "Ano Crescente":
            query += " ORDER BY d.ano ASC, d.mes ASC"
        elif ordenar_por == "Ano Decrescente":
            query += " ORDER BY d.ano DESC, d.mes DESC"
        elif ordenar_por == "A-Z":
            query += " ORDER BY d.tipo ASC"
        elif ordenar_por == "Z-A":
            query += " ORDER BY d.tipo DESC"
        
        cur.execute(query, params)
        documentos = cur.fetchall()

        # Limpar a treeview antes de adicionar novos resultados
        for row in tree.get_children():
            tree.delete(row)

        for doc in documentos:
            tree.insert("", "end", values=doc)

        cur.close()
        conn.close()

        if not documentos:
            messagebox.showinfo("Consulta", "Nenhum documento encontrado com os filtros aplicados.")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar documentos: {e}")

def iniciar_processamento():
    """Chama a função do main.py para processar os documentos."""
    processar_documentos()
    messagebox.showinfo("Sucesso", "Processamento concluído!")

def gerar_relatorio_auditoria():
    """Chama a função do check.py para gerar o relatório de auditoria."""
    gerar_relatorio()
    messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")

# Criando a interface principal
root = tk.Tk()
root.title("Auditoria de Documentos")
root.geometry("900x500")

# Seção de filtros
frame_filtros = ttk.LabelFrame(root, text="Filtros de Pesquisa")
frame_filtros.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_filtros, text="Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_empresa = ttk.Entry(frame_filtros, width=30)
entry_empresa.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_filtros, text="Funcionário:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_funcionario = ttk.Entry(frame_filtros, width=30)
entry_funcionario.grid(row=0, column=3, padx=5, pady=5)

# Opções de ordenação
combo_ordenacao = ttk.Combobox(frame_filtros, values=["Ano Crescente", "Ano Decrescente", "A-Z", "Z-A"])
combo_ordenacao.grid(row=0, column=4, padx=5, pady=5)
combo_ordenacao.set("Ano Crescente")

btn_filtrar = ttk.Button(frame_filtros, text="Buscar Documentos", command=listar_documentos)
btn_filtrar.grid(row=0, column=5, padx=10, pady=5)

# Tabela para exibir os documentos
frame_tabela = ttk.Frame(root)
frame_tabela.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("Empresa", "Funcionário", "Ano", "Mês", "Tipo de Documento")
tree = ttk.Treeview(frame_tabela, columns=columns, show="headings")
tree.pack(side="left", fill="both", expand=True)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Botões de ação
frame_botoes = ttk.Frame(root)
frame_botoes.pack(fill="x", padx=10, pady=10)

btn_processar = ttk.Button(frame_botoes, text="Processar PDFs", command=iniciar_processamento)
btn_processar.pack(side="left", padx=5, pady=5)

btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", command=gerar_relatorio_auditoria)
btn_relatorio.pack(side="left", padx=5, pady=5)

btn_sair = ttk.Button(frame_botoes, text="Sair", command=root.quit)
btn_sair.pack(side="right", padx=5, pady=5)

# Rodar a interface
root.mainloop()
