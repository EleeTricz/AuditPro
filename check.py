import psycopg2
import pandas as pd

# Configuração do banco PostgreSQL
DB_CONFIG = {
    'dbname': 'auditoria_documentos',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

# Período de auditoria: Janeiro/2020 a Fevereiro/2025
PERIODO_INICIO = (2020, 1)
PERIODO_FIM = (2025, 2)

def obter_documentos_existentes():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT e.nome AS empresa, f.nome AS funcionario, d.ano, d.mes, d.tipo
            FROM documentos d
            LEFT JOIN funcionarios f ON d.funcionario_id = f.id
            JOIN empresas e ON d.empresa_id = e.id
        """)
        
        documentos = cur.fetchall()
        cur.close()
        conn.close()
        
        return set(documentos)
    except Exception as e:
        print("Erro ao buscar documentos existentes:", e)
        return set()

def obter_funcionarios_por_empresa():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT e.nome AS empresa, f.nome AS funcionario
            FROM funcionarios f
            JOIN empresas e ON f.empresa_id = e.id
        """)
        
        funcionarios = cur.fetchall()
        cur.close()
        conn.close()
        
        empresas = {}
        for empresa, funcionario in funcionarios:
            if empresa not in empresas:
                empresas[empresa] = []
            empresas[empresa].append(funcionario)
        
        return empresas
    except Exception as e:
        print("Erro ao buscar funcionários:", e)
        return {}

def gerar_relatorio():
    """ Função chamada pela interface para gerar o relatório de auditoria. """
    documentos_existentes = obter_documentos_existentes()
    empresas_funcionarios = obter_funcionarios_por_empresa()
    documentos_faltantes = []
    
    for empresa, funcionarios in empresas_funcionarios.items():
        for ano in range(PERIODO_INICIO[0], PERIODO_FIM[0] + 1):
            for mes in range(1, 13):
                if (ano == PERIODO_FIM[0] and mes > PERIODO_FIM[1]):
                    break  
                
                
                
                # Regras para CONTRACHEQUE e FÉRIAS
                for funcionario in funcionarios:
                    tem_ferias = (empresa, funcionario, ano, mes, "FERIAS") in documentos_existentes
                    tem_contracheque = (empresa, funcionario, ano, mes, "CONTRACHEQUE") in documentos_existentes
                    
                    # Se não há FÉRIAS e não há CONTRACHEQUE, então está faltando
                    if not tem_ferias and not tem_contracheque:
                        documentos_faltantes.append([empresa, funcionario, ano, mes, "CONTRACHEQUE"])
                
                # Regras para 13º Salário (meses 11 e 12)
                if mes in [11, 12]:
                    if (empresa, None, ano, mes, "FOLHA13") not in documentos_existentes:
                        documentos_faltantes.append([empresa, "TODOS", ano, mes, "FOLHA13"])
                    
                    for funcionario in funcionarios:
                        if (empresa, funcionario, ano, mes, "CONTRACHEQUE13") not in documentos_existentes:
                            documentos_faltantes.append([empresa, funcionario, ano, mes, "CONTRACHEQUE13"])
    
    df = pd.DataFrame(documentos_faltantes, columns=["Empresa", "Funcionário", "Ano", "Mês", "Tipo de Documento"])
    
    nome_arquivo = "Relatorio_Auditoria.xlsx"
    df.to_excel(nome_arquivo, index=False)
    print(f"Relatório gerado com sucesso: {nome_arquivo}")

if __name__ == "__main__":
    gerar_relatorio()
