-- Query 1: top 5 operadoras com maior crescimento percentual
WITH primeiro AS (
  SELECT cnpj, MIN(ano * 10 + trimestre) AS p
  FROM despesas_consolidadas
  GROUP BY cnpj
),
ultimo AS (
  SELECT cnpj, MAX(ano * 10 + trimestre) AS u
  FROM despesas_consolidadas
  GROUP BY cnpj
),
inicio AS (
  SELECT d.cnpj, d.valor_despesas AS valor_inicio
  FROM despesas_consolidadas d
  JOIN primeiro p ON p.cnpj = d.cnpj AND (d.ano * 10 + d.trimestre) = p.p
),
fim AS (
  SELECT d.cnpj, d.valor_despesas AS valor_fim
  FROM despesas_consolidadas d
  JOIN ultimo u ON u.cnpj = d.cnpj AND (d.ano * 10 + d.trimestre) = u.u
)
SELECT c.razao_social, i.cnpj,
       ((f.valor_fim - i.valor_inicio) / NULLIF(i.valor_inicio, 0)) * 100 AS crescimento_pct
FROM inicio i
JOIN fim f ON f.cnpj = i.cnpj
JOIN operadoras_cadastro c ON c.cnpj = i.cnpj
WHERE i.valor_inicio > 0
ORDER BY crescimento_pct DESC
LIMIT 5;

-- Query 2: top 5 UFs por total + média por operadora na UF
SELECT uf,
       SUM(total_despesas) AS total_uf,
       AVG(total_despesas) AS media_por_operadora
FROM despesas_agregadas
GROUP BY uf
ORDER BY total_uf DESC
LIMIT 5;

-- Query 3: operadoras acima da média geral em pelo menos 2 trimestres
WITH media_geral AS (
  SELECT ano, trimestre, AVG(valor_despesas) AS media_tri
  FROM despesas_consolidadas
  GROUP BY ano, trimestre
),
acima_media AS (
  SELECT d.cnpj, COUNT(*) AS qtd_trimestres
  FROM despesas_consolidadas d
  JOIN media_geral m
    ON m.ano = d.ano AND m.trimestre = d.trimestre
  WHERE d.valor_despesas > m.media_tri
  GROUP BY d.cnpj
)
SELECT COUNT(*) AS operadoras_acima_media_2_ou_mais
FROM acima_media
WHERE qtd_trimestres >= 2;

