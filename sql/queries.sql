-- ============================================
-- NutriInsights - Queries Analíticas
-- Perguntas de negócio respondidas via SQL
-- ============================================

USE nutri_insights;

-- 1. Quais categorias têm maior teor médio de açúcar?
-- Ajuda a identificar grupos alimentares mais prejudiciais
SELECT
    categoria,
    ROUND(AVG(acucar_100g), 2)    AS media_acucar,
    ROUND(AVG(calorias_100g), 2)  AS media_calorias,
    COUNT(*)                       AS total_alimentos
FROM alimentos
WHERE acucar_100g IS NOT NULL
GROUP BY categoria
ORDER BY media_acucar DESC
LIMIT 10;


-- 2. Como o sódio varia entre as categorias?
-- Sódio elevado está associado a hipertensão
SELECT
    categoria,
    ROUND(AVG(sodio_100g), 4)  AS media_sodio,
    ROUND(MAX(sodio_100g), 4)  AS max_sodio,
    COUNT(*)                    AS total_alimentos
FROM alimentos
WHERE sodio_100g IS NOT NULL
GROUP BY categoria
ORDER BY media_sodio DESC;


-- 3. Top 10 alimentos com maior índice proteico
-- Útil para recomendações de dietas ricas em proteína
SELECT
    nome,
    categoria,
    proteinas_100g,
    calorias_100g
FROM alimentos
WHERE proteinas_100g IS NOT NULL
ORDER BY proteinas_100g DESC
LIMIT 10;


-- 4. Correlação entre calorias e gorduras saturadas por categoria
-- Identifica categorias com perfil nutricional mais crítico
SELECT
    categoria,
    ROUND(AVG(calorias_100g), 2)     AS media_calorias,
    ROUND(AVG(gordura_sat_100g), 2)  AS media_gordura_sat,
    ROUND(AVG(fibras_100g), 2)       AS media_fibras
FROM alimentos
GROUP BY categoria
ORDER BY media_gordura_sat DESC;


-- 5. Ranking de categorias com melhor perfil nutricional
-- Score: alto em proteína e fibra, baixo em açúcar e gordura saturada
SELECT
    categoria,
    ROUND(AVG(proteinas_100g), 2)    AS media_proteina,
    ROUND(AVG(fibras_100g), 2)       AS media_fibra,
    ROUND(AVG(acucar_100g), 2)       AS media_acucar,
    ROUND(AVG(gordura_sat_100g), 2)  AS media_gordura_sat,
    COUNT(*)                          AS total_alimentos
FROM alimentos
GROUP BY categoria
ORDER BY media_proteina DESC, media_fibra DESC;