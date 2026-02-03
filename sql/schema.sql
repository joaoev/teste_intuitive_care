-- PostgreSQL

CREATE TABLE IF NOT EXISTS operadoras_cadastro (
  cnpj VARCHAR(14) PRIMARY KEY,
  registro_ans VARCHAR(20),
  razao_social VARCHAR(255),
  modalidade VARCHAR(120),
  uf VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS despesas_consolidadas (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cnpj VARCHAR(14) NOT NULL,
  registro_ans VARCHAR(20),
  ano INTEGER NOT NULL,
  trimestre INTEGER NOT NULL,
  valor_despesas DECIMAL(18, 2) NOT NULL,
  FOREIGN KEY (cnpj) REFERENCES operadoras_cadastro(cnpj)
);

CREATE INDEX IF NOT EXISTS idx_despesas_cnpj_ano_tri
  ON despesas_consolidadas (cnpj, ano, trimestre);

CREATE TABLE IF NOT EXISTS despesas_agregadas (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  razao_social VARCHAR(255) NOT NULL,
  uf VARCHAR(2),
  total_despesas DECIMAL(18, 2) NOT NULL,
  media_despesas_trimestre DECIMAL(18, 2),
  desvio_padrao_despesas DECIMAL(18, 2)
);
