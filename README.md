# Teste Intuitive Care

![Python](https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?logo=vuedotjs&logoColor=%234FC08D)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?logo=vite&logoColor=white)

**Autor**: João Evangelista

Solução completa para extração, transformação, carregamento (ETL) e visualização de dados da ANS (Agência Nacional de Saúde Suplementar). O projeto processa arquivos de demonstrações contábeis e disponibiliza uma interface interativa para consulta de despesas por operadora.

## 🚀 Funcionalidades

- **ETL em Python**: Pipeline robusto para download, normalização e enriquecimento de dados da ANS.
- **API RESTful**: Backend em FastAPI para servir dados paginados e estatísticas agregadas.
- **Frontend Moderno**: Aplicação Vue 3 + PrimeVue com gráficos interativos e tabelas de busca.
- **SQL Analítico**: Scripts prontos com estrutura de banco e queries de análise de performance.

## 📂 Estrutura do Projeto

- `backend/etl`: Módulos do pipeline de dados (extração, transformação, carga).
- `backend/api`: Servidor da API.
- `frontend`: Aplicação Web.
- `sql`: DDL (Schema) e queries analíticas (SQL).

---

## 1) ETL (Pipeline de Dados)

O pipeline baixa automaticamente os dados do FTP da ANS, trata inconsistências de encoding e gera arquivos CSV consolidados.

### Instalação

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt

```

### Execução Completa

Para rodar o pipeline ponta a ponta (Download -> Extração -> Tratamento -> Consolidação):

```bash
python -m etl.cli run --base-dir ./data

```

**Saídas geradas em `backend/data/output`:**

* `consolidado_validado.csv`: Dados limpos e enriquecidos com o cadastro da operadora.
* `despesas_agregadas.csv`: Dados sumarizados por operadora e UF.

---

## 2) API (Backend)

Servidor FastAPI que expõe os dados processados pelo ETL.

### Inicialização

```bash
cd backend
# Certifique-se de que o venv está ativo
uvicorn api.main:app --reload --port 8000

```

### Endpoints Principais

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/operadoras` | Lista operadoras com paginação e busca |
| `GET` | `/api/operadoras/{cnpj}` | Detalhes de uma operadora específica |
| `GET` | `/api/operadoras/{cnpj}/despesas` | Histórico trimestral de despesas |
| `GET` | `/api/estatisticas` | Dashboard com totais e Top 5 (Cache de 5min) |

---

## 3) Frontend (Interface Web)

Interface desenvolvida com Vue 3, TypeScript e Vite.

### Configuração e Execução

```bash
cd frontend
npm install
npm run dev

```

Acesse a aplicação em: `http://localhost:5173`

---

## 4) SQL e Análise

Arquivos localizados na pasta `sql/`:

* **`sql/schema.sql`**: Definição das tabelas (`operadoras_cadastro`, `despesas_consolidadas`).
* **`sql/queries.sql`**: Consultas analíticas solicitadas, incluindo:
1. Top 5 operadoras com maior crescimento de despesas.
2. Total e média de despesas por UF.
3. Operadoras acima da média em múltiplos trimestres.



---

## 🛠️ Trade-offs e Decisões de Arquitetura

Para detalhes sobre as escolhas técnicas (como o uso de `pandas` para ETL, estratégia de cache na API e validação de dados), que pedia no teste, consulte o arquivo:

📄 [TRADEOFFS.md](./TRADEOFFS.md)
