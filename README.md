# Teste Intuitive Care

__Autor__: João Evangelista

- ETL em Python para download/processamento/normalização dos dados ANS
- API em FastAPI para consulta das operadoras e despesas
- Frontend em Vue 3 para listagem, busca, paginação, gráfico por UF e detalhes
- Scripts SQL com estrutura e queries analíticas

## Estrutura

- `backend/etl`: pipeline de dados
- `backend/api`: servidor FastAPI
- `frontend`: aplicação Vue
- `sql`: DDL + queries analíticas

## 1) ETL (Python)

### Instalação

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Execução completa

```bash
python -m etl.cli run --base-dir ./data
```

Saídas principais em `backend/data/output`:

- `consolidado_despesas.csv`
- `consolidado_enriquecido.csv`
- `consolidado_validado.csv`
- `despesas_agregadas.csv`

## 2) API (FastAPI)

### Subir servidor

```bash
cd backend
venv\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

### Rotas

- `GET /api/operadoras?page=1&limit=10&search=...`
- `GET /api/operadoras/{cnpj}`
- `GET /api/operadoras/{cnpj}/despesas`
- `GET /api/estatisticas`

## 3) Frontend (Vue 3 + Vite)

```bash
cd frontend
npm install
npm run dev
```

App disponível em `http://localhost:5173`.

## 4) SQL

- Estrutura: `sql/schema.sql`
- Consultas analíticas: `sql/queries.sql`

## Trade-offs adotados

1. **Framework backend**: FastAPI, por produtividade, tipagem e documentação automática.
2. **Paginação**: offset-based (`page`, `limit`), simples para o cenário inicial.
3. **Estatísticas**: cache em memória por 5 minutos para reduzir custo da rota agregada.
4. **Validação de dados**: marcamos inválidos (`Valido=false` + `ErrosValidacao`) em vez de excluir por padrão.
5. **Join com cadastro**: `left join` por `RegistroANS`, preservando despesas sem match (`StatusCadastro=SEM_MATCH`).

Detalhamento completo das decisões: `TRADEOFFS.md`.
