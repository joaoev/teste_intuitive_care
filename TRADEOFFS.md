# Decisoes Tecnicas e Trade-offs

Este documento registra as principais decisoes tecnicas do teste, com alternativas consideradas, escolha final e justificativa.

## Contexto

- Objetivo: entregar um pipeline de dados (Python), API e interface web (Vue) com foco em clareza, robustez e tempo de entrega.
- Base de dados: arquivos publicos da ANS com variacoes de estrutura entre periodos.
- Prioridade: funcionamento ponta a ponta com tratamento de inconsistencias e boa documentacao.

## 1) ETL e processamento de arquivos

### 1.1 Processamento em memoria vs incremental

- **Opcao A - em memoria**: carregar e transformar tudo em DataFrame de uma vez.
- **Opcao B - incremental**: processar arquivo a arquivo e consolidar ao final.
- **Escolha**: abordagem hibrida com processamento por arquivo e consolidacao final em DataFrame.
- **Justificativa**:
  - reduz risco de estouro de memoria em volumes maiores;
  - mantem simplicidade de implementacao para o escopo do teste;
  - facilita troubleshooting por etapa (download, extract, filter, consolidate).

### 1.2 Identificacao de estrutura heterogenea (CSV/TXT/XLSX)

- **Escolha**: deteccao automatica de encoding/separador + normalizacao de nomes de colunas (`slugify` + mapeamento canonico).
- **Justificativa**:
  - arquivos da ANS variam em layout;
  - evita regras fixas por arquivo;
  - melhora reuso para novos trimestres.

### 1.3 Tratamento de inconsistencias no consolidado

- Casos esperados:
  - CNPJ duplicado com razoes sociais diferentes;
  - valores zerados/negativos;
  - datas/trimestres inconsistentes.
- **Escolha aplicada**:
  - consolidacao por `RegistroANS + Ano + Trimestre` para reduzir duplicidade operacional;
  - validacao explicita com marcacao de erros (`Valido` e `ErrosValidacao`) em vez de descarte automatico;
  - parse de trimestre por data de referencia com fallback seguro.
- **Justificativa**:
  - preserva rastreabilidade;
  - evita perda silenciosa de dados;
  - permite politicas futuras (excluir, corrigir, auditar) sem reprocessar origem.

## 2) Validacao e enriquecimento

### 2.1 CNPJ invalido: excluir vs marcar

- **Opcao A**: excluir linhas invalidas.
- **Opcao B**: manter e marcar.
- **Escolha**: manter e marcar por padrao; opcionalmente excluir com `--reject-invalid`.
- **Justificativa**:
  - melhor para auditoria;
  - evita mascarar problemas de origem;
  - da flexibilidade para consumidores diferentes.

### 2.2 Chave de join: CNPJ vs Registro ANS

- **Opcao A**: join por CNPJ.
- **Opcao B**: join por Registro ANS.
- **Escolha**: join principal por `RegistroANS` (fonte contabil), retornando CNPJ e dados cadastrais.
- **Justificativa**:
  - os arquivos contabilizados usam `REG_ANS` de forma mais consistente;
  - CNPJ pode estar ausente ou formatado de formas diferentes em fontes distintas.

### 2.3 Sem match no cadastro

- **Escolha**: `left join` e coluna `StatusCadastro` (`OK`/`SEM_MATCH`).
- **Justificativa**:
  - nao perder despesas sem correspondencia;
  - evidenciar lacunas de qualidade de dados.

## 3) Banco de dados (SQL)

### 3.1 Modelo: desnormalizado vs normalizado

- **Opcao A**: tabela unica desnormalizada.
- **Opcao B**: tabelas separadas (`cadastro`, `despesas_consolidadas`, `despesas_agregadas`).
- **Escolha**: modelo normalizado simples.
- **Justificativa**:
  - reduz redundancia;
  - melhora manutencao de cadastro;
  - suficiente para consultas analiticas propostas.

### 3.2 Tipos de dados

- Valores monetarios: **DECIMAL(18,2)**.
- Datas de analise: **Ano + Trimestre** (inteiros), evitando ambiguidades de parsing.
- Chaves textuais: `VARCHAR`.
- **Justificativa**:
  - DECIMAL preserva precisao financeira;
  - ano/trimestre atende o dominio do problema com simplicidade.

## 4) Backend da API

### 4.1 Flask vs FastAPI

- **Escolha**: FastAPI.
- **Justificativa**:
  - tipagem e validacao de parametros nativas;
  - desenvolvimento rapido;
  - melhor experiencia para evoluir documentacao e contratos.

### 4.2 Estrategia de paginacao

- **Opcao A**: offset/page-limit.
- **Opcao B**: cursor/keyset.
- **Escolha**: offset (`page`, `limit`).
- **Justificativa**:
  - implementacao direta;
  - atende volume atual;
  - mais simples para consumo no frontend.

### 4.3 Cache de estatisticas

- **Opcao A**: calcular sempre.
- **Opcao B**: cache temporario.
- **Opcao C**: pre-calculo persistido.
- **Escolha**: cache em memoria (TTL de 5 minutos).
- **Justificativa**:
  - reduz custo de agregacao repetida;
  - sem aumentar complexidade operacional.

### 4.4 Formato de resposta paginada

- **Escolha**: retornar `data + metadados` (`total`, `page`, `limit`).
- **Justificativa**:
  - facilita UX de paginacao;
  - evita chamadas extras para contagem.

## 5) Frontend (Vue)

### 5.1 Busca no servidor vs cliente

- **Escolha**: busca no servidor (`search` na API).
- **Justificativa**:
  - escalavel para crescimento de dados;
  - evita carregar dataset completo no navegador.

### 5.2 Gerenciamento de estado

- **Opcao A**: store global (Pinia/Vuex).
- **Opcao B**: estado local + composables simples.
- **Escolha**: estado local por pagina/componente.
- **Justificativa**:
  - menor complexidade para o escopo atual;
  - fluxo de dados curto e previsivel.

### 5.3 Performance da tabela

- **Escolha**: paginacao server-side (sem virtualizacao neste MVP).
- **Justificativa**:
  - evita render de listas grandes;
  - atende requisitos com baixo custo de implementacao.

### 5.4 Loading, erros e vazio

- **Escolha**: estados explicitos por tela (`loading`, `error`, `empty`).
- **Justificativa**:
  - melhora clareza para usuario;
  - facilita manutencao e testes.

## 6) Limites conhecidos e proximos passos

- Adicionar testes automatizados (unitarios e integracao) para ETL/API.
- Parametrizar estrategia de validacao por ambiente (estrito vs tolerante).
- Evoluir paginacao para keyset se volume e taxa de atualizacao crescerem.
- Persistir estatisticas pre-calculadas para cenarios de alta concorrencia.

