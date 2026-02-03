# Decisões Técnicas e Trade-offs

Este documento registra as principais decisões técnicas do teste, com alternativas consideradas, escolha final e justificativa.

## Contexto

- **Objetivo**: entregar um pipeline de dados (Python), API e interface web (Vue) com foco em clareza, robustez e tempo de entrega.
- **Base de dados**: arquivos públicos da ANS com variações de estrutura entre períodos.
- **Prioridade**: funcionamento ponta a ponta com tratamento de inconsistências e boa documentação.

## 1) ETL e processamento de arquivos

### 1.1 Processamento em memória vs incremental

- **Opção A - em memória**: carregar e transformar tudo em DataFrame de uma vez.
- **Opção B - incremental**: processar arquivo a arquivo e consolidar ao final.
- **Escolha**: abordagem híbrida com processamento por arquivo e consolidação final em DataFrame.
- **Justificativa**:
  - reduz risco de estouro de memória em volumes maiores;
  - mantém simplicidade de implementação para o escopo do teste;
  - facilita troubleshooting por etapa (download, extract, filter, consolidate).

### 1.2 Identificação de estrutura heterogênea (CSV/TXT/XLSX)

- **Escolha**: detecção automática de encoding/separador + normalização de nomes de colunas (`slugify` + mapeamento canônico).
- **Justificativa**:
  - arquivos da ANS variam em layout;
  - evita regras fixas por arquivo;
  - melhora reúso para novos trimestres.

### 1.3 Tratamento de inconsistências no consolidado

- Casos esperados:
  - CNPJ duplicado com razões sociais diferentes;
  - valores zerados/negativos;
  - datas/trimestres inconsistentes.
- **Escolha aplicada**:
  - consolidação por `RegistroANS + Ano + Trimestre` para reduzir duplicidade operacional;
  - validação explícita com marcação de erros (`Valido` e `ErrosValidacao`) em vez de descarte automático;
  - parse de trimestre por data de referência com *fallback* seguro.
- **Justificativa**:
  - preserva rastreabilidade;
  - evita perda silenciosa de dados;
  - permite políticas futuras (excluir, corrigir, auditar) sem reprocessar origem.

## 2) Validação e enriquecimento

### 2.1 CNPJ inválido: excluir vs marcar

- **Opção A**: excluir linhas inválidas.
- **Opção B**: manter e marcar.
- **Escolha**: manter e marcar por padrão; opcionalmente excluir com `--reject-invalid`.
- **Justificativa**:
  - melhor para auditoria;
  - evita mascarar problemas de origem;
  - dá flexibilidade para consumidores diferentes.

### 2.2 Chave de join: CNPJ vs Registro ANS

- **Opção A**: join por CNPJ.
- **Opção B**: join por Registro ANS.
- **Escolha**: join principal por `RegistroANS` (fonte contábil), retornando CNPJ e dados cadastrais.
- **Justificativa**:
  - os arquivos contabilizados usam `REG_ANS` de forma mais consistente;
  - CNPJ pode estar ausente ou formatado de formas diferentes em fontes distintas.

### 2.3 Sem match no cadastro

- **Escolha**: `left join` e coluna `StatusCadastro` (`OK`/`SEM_MATCH`).
- **Justificativa**:
  - não perder despesas sem correspondência;
  - evidenciar lacunas de qualidade de dados.

## 3) Banco de dados (SQL)

### 3.1 Modelo: desnormalizado vs normalizado

- **Opção A**: tabela única desnormalizada.
- **Opção B**: tabelas separadas (`cadastro`, `despesas_consolidadas`, `despesas_agregadas`).
- **Escolha**: modelo normalizado simples.
- **Justificativa**:
  - reduz redundância;
  - melhora manutenção de cadastro;
  - suficiente para consultas analíticas propostas.

### 3.2 Tipos de dados

- Valores monetários: **DECIMAL(18,2)**.
- Datas de análise: **Ano + Trimestre** (inteiros), evitando ambiguidades de parsing.
- Chaves textuais: `VARCHAR`.
- **Justificativa**:
  - DECIMAL preserva precisão financeira;
  - ano/trimestre atende o domínio do problema com simplicidade.

## 4) Backend da API

### 4.1 Flask vs FastAPI

- **Escolha**: FastAPI.
- **Justificativa**:
  - tipagem e validação de parâmetros nativas;
  - desenvolvimento rápido;
  - melhor experiência para evoluir documentação e contratos.

### 4.2 Estratégia de paginação

- **Opção A**: offset/page-limit.
- **Opção B**: cursor/keyset.
- **Escolha**: offset (`page`, `limit`).
- **Justificativa**:
  - implementação direta;
  - atende volume atual;
  - mais simples para consumo no frontend.

### 4.3 Cache de estatísticas

- **Opção A**: calcular sempre.
- **Opção B**: cache temporário.
- **Opção C**: pré-cálculo persistido.
- **Escolha**: cache em memória (TTL de 5 minutos).
- **Justificativa**:
  - reduz custo de agregação repetida;
  - sem aumentar complexidade operacional.

### 4.4 Formato de resposta paginada

- **Escolha**: retornar `data + metadados` (`total`, `page`, `limit`).
- **Justificativa**:
  - facilita UX de paginação;
  - evita chamadas extras para contagem.

## 5) Frontend (Vue)

### 5.1 Busca no servidor vs cliente

- **Escolha**: busca no servidor (`search` na API).
- **Justificativa**:
  - escalável para crescimento de dados;
  - evita carregar dataset completo no navegador.

### 5.2 Gerenciamento de estado

- **Opção A**: store global (Pinia/Vuex).
- **Opção B**: estado local + composables simples.
- **Escolha**: estado local por página/componente.
- **Justificativa**:
  - menor complexidade para o escopo atual;
  - fluxo de dados curto e previsível.

### 5.3 Performance da tabela

- **Escolha**: paginação server-side (sem virtualização neste MVP).
- **Justificativa**:
  - evita render de listas grandes;
  - atende requisitos com baixo custo de implementação.

### 5.4 Loading, erros e vazio

- **Escolha**: estados explícitos por tela (`loading`, `error`, `empty`).
- **Justificativa**:
  - melhora clareza para usuário;
  - facilita manutenção e testes.

## 6) Limites conhecidos e próximos passos

- Adicionar testes automatizados (unitários e integração) para ETL/API.
- Parametrizar estratégia de validação por ambiente (estrito vs tolerante).
- Evoluir paginação para keyset se volume e taxa de atualização crescerem.
- Persistir estatísticas pré-calculadas para cenários de alta concorrência.