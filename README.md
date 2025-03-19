# 📌 Auditoria de Documentos - Interface Gráfica

Este projeto permite processar documentos em PDF, armazená-los em um banco de dados PostgreSQL, gerar relatórios de auditoria e listar os documentos cadastrados por empresa e funcionário.

## 🛠️ Instalação e Configuração

### 1️⃣ **Clonar o repositório**
```bash
 git clone https://github.com/seu-repositorio/auditoria-documentos.git
 cd auditoria-documentos
```

### 2️⃣ **Instalar dependências**

Certifique-se de ter o Python 3 instalado. Em seguida, execute:
```bash
pip install -r requirements.txt
```
As dependências incluem:
- `psycopg2` (para conexão com o PostgreSQL)
- `pandas` (para manipulação de dados e geração do relatório)
- `openpyxl` (para exportação do relatório em Excel)
- `tkinter` (para a interface gráfica - já incluso no Python)

### 3️⃣ **Configurar o banco de dados**

Certifique-se de que o PostgreSQL está instalado e rodando.
Crie o banco de dados executando:
```sql
CREATE DATABASE auditoria_documentos;
```
Acesse o banco de dados criado:
```sql
\c auditoria_documentos
```
Criar tabelas:
```sql
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    empresa_id INT REFERENCES empresas(id) ON DELETE CASCADE
);

CREATE TABLE documentos (
    id SERIAL PRIMARY KEY,
    funcionario_id INT REFERENCES funcionarios(id) ON DELETE CASCADE,
    empresa_id INT REFERENCES empresas(id) ON DELETE CASCADE,
    tipo VARCHAR(20) CHECK (tipo IN ('FOLHA', 'FOLHA13', 'CONTRACHEQUE', 'CONTRACHEQUE13', 'FERIAS')),
    ano INT NOT NULL,
    mes INT NOT NULL,
    arquivo BYTEA NOT NULL,  -- Armazena o PDF diretamente no banco
    data_insercao TIMESTAMP DEFAULT NOW()
);
```

No arquivo `main.py`, configure as credenciais do PostgreSQL:
```python
DB_CONFIG = {
    'dbname': 'auditoria_documentos',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}
```
Caso necessário, altere as credenciais conforme sua configuração.

### 4️⃣ **Executar a aplicação**

Para iniciar a interface gráfica, execute:
```bash
python app.py
```

---

## 📂 Padrão dos Arquivos PDF

Os documentos precisam estar organizados da seguinte forma:
```
📁 PROJETO_AUDITORIA_PDFS/
 ├── 📁 ACIB/  (Empresa)
 │   ├── Carlos_2020_01_FOLHA_PAGAMENTO.pdf
 │   ├── Carlos_2020_02_CONTRACHEQUE.pdf
 │   ├── Ana_2021_03_CONTRACHEQUE.pdf
 │   └── ...
 ├── 📁 OUTRA_EMPRESA/
 │   ├── João_2022_05_FOLHA.pdf
 │   └── ...
```
Formato do nome do arquivo:
```
[FUNCIONARIO]_[ANO]_[MES]_[TIPO].pdf
```
Exemplo: `Carlos_2020_01_FOLHA.pdf`

Tipos de documento permitidos:
- `FOLHA`
- `FOLHA13`
- `CONTRACHEQUE`
- `CONTRACHEQUE13`
- `FERIAS`

---

## 🚀 Funcionalidades da Interface

✅ **Processar PDFs**: Armazena documentos no banco de dados.
✅ **Gerar Relatório de Auditoria**: Identifica documentos faltantes.
✅ **Buscar Documentos**: Filtra documentos por empresa e funcionário.
✅ **Exibir dados em tabela interativa**.

---

## 📊 Gerar Relatório de Auditoria

Clique no botão `Gerar Relatório`. O sistema verificará quais documentos estão faltando entre **Jan/2020 e Fev/2025** e salvará um arquivo Excel chamado `Relatorio_Auditoria.xlsx`.

---

## ❌ Possíveis Erros e Soluções

- **Erro de conexão com o banco**:
  - Verifique se o PostgreSQL está rodando.
  - Confirme se as credenciais no `DB_CONFIG` estão corretas.
- **Arquivos ignorados durante o processamento**:
  - Certifique-se de que seguem o padrão `[FUNCIONARIO]_[ANO]_[MES]_[TIPO].pdf`.

---

## 📌 Contato

Caso tenha dúvidas ou precise de suporte, entre em contato pelo e-mail: `contabilidade-total4@outlook.com`.

