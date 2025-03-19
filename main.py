import os
import psycopg2

# Configuração do banco PostgreSQL
DB_CONFIG = {
    'dbname': 'auditoria_documentos',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def conectar_banco():
    """Cria e retorna uma conexão com o banco de dados."""
    return psycopg2.connect(**DB_CONFIG)

def documento_existe(cur, empresa_id, funcionario_id, ano, mes, tipo):
    """Verifica se um documento já está no banco de dados."""
    cur.execute(
        """
        SELECT 1 FROM documentos 
        WHERE funcionario_id IS NOT DISTINCT FROM %s 
        AND empresa_id = %s 
        AND tipo = %s 
        AND mes = %s 
        AND ano = %s
        """,
        (funcionario_id, empresa_id, tipo, mes, ano)
    )
    return cur.fetchone() is not None

def inserir_documento(conn, empresa, funcionario, ano, mes, tipo, pdf_path):
    try:
        cur = conn.cursor()

        # Buscar ou inserir empresa
        cur.execute("SELECT id FROM empresas WHERE nome = %s", (empresa,))
        empresa_id = cur.fetchone()
        if not empresa_id:
            cur.execute("INSERT INTO empresas (nome) VALUES (%s) RETURNING id", (empresa,))
            empresa_id = cur.fetchone()[0]
        else:
            empresa_id = empresa_id[0]

        # Definir funcionario_id como NULL para FOLHA e FOLHA13
        funcionario_id = None
        if tipo not in ("FOLHA", "FOLHA13"):
            cur.execute("SELECT id FROM funcionarios WHERE nome = %s AND empresa_id = %s", (funcionario, empresa_id))
            funcionario_id = cur.fetchone()
            if not funcionario_id:
                cur.execute("INSERT INTO funcionarios (nome, empresa_id) VALUES (%s, %s) RETURNING id", (funcionario, empresa_id))
                funcionario_id = cur.fetchone()[0]
            else:
                funcionario_id = funcionario_id[0]

        # Verificar se o documento já existe antes de inserir
        if documento_existe(cur, empresa_id, funcionario_id, ano, mes, tipo):
            print(f"Documento {tipo} ({mes}/{ano}) já está no banco. Pulando...")
        else:
            # Ler o PDF como binário
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            # Inserir documento com o arquivo PDF
            cur.execute(
                """
                INSERT INTO documentos (funcionario_id, empresa_id, tipo, mes, ano, data_upload, arquivo_pdf)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                """,
                (funcionario_id, empresa_id, tipo, mes, ano, psycopg2.Binary(pdf_bytes))
            )
            conn.commit()
            print(f"Documento {tipo} ({mes}/{ano}) armazenado com sucesso.")

        cur.close()
    except Exception as e:
        print("Erro ao inserir no banco:", e)

def processar_documentos():
    """ Processa os documentos da pasta e insere no banco apenas os que não existem. """
    pasta_pdfs = "C:/Users/TERMINAL-3/OneDrive/CONTABILIDADE/ERIKY_SIMOES/PROJETO_AUDITORIA/PROJETO_AUDITORIA_PDFS"
    
    conn = conectar_banco()  # Abrir conexão antes do loop

    for empresa in os.listdir(pasta_pdfs):
        caminho_empresa = os.path.join(pasta_pdfs, empresa)

        if os.path.isdir(caminho_empresa):
            print(f"Processando empresa: {empresa}")

            for arquivo in os.listdir(caminho_empresa):
                if arquivo.endswith(".pdf"):
                    partes = arquivo.replace(".pdf", "").split("_")

                    if len(partes) == 4:
                        funcionario, ano, mes, tipo = partes

                        if not (ano.isdigit() and mes.isdigit()):
                            print(f"Erro: Ano ou mês inválidos no arquivo {arquivo}. Pulando...")
                            continue

                        pdf_path = os.path.join(caminho_empresa, arquivo)
                        inserir_documento(conn, empresa, funcionario, int(ano), int(mes), tipo, pdf_path)
                    else:
                        print(f"Erro: Nome do arquivo {arquivo} não segue o padrão esperado.")

    conn.close()  # Fechar conexão ao final do processo

if __name__ == "__main__":
    processar_documentos()
