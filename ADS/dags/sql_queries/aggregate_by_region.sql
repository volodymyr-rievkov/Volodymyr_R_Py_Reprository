DROP TABLE IF EXISTS agg_demographics_by_region CASCADE;

CREATE TABLE agg_demographics_by_region AS
SELECT 
    dl.region,
    dt.year,
    COUNT(DISTINCT dl.country_key) as country_count,
    ROUND(AVG(fd.country_population)::numeric, 0) as avg_population,
    ROUND(AVG(fd.fertility_rate)::numeric, 2) as avg_fertility_rate,
    ROUND(AVG(fd.life_expectancy)::numeric, 2) as avg_life_expectancy,
    SUM(fd.country_population) as total_population
FROM fact_demographics fd
JOIN dim_location dl ON fd.country_key = dl.country_key
JOIN dim_time dt ON fd.time_key = dt.time_key
WHERE dl.region IS NOT NULL
GROUP BY dl.region, dt.year
ORDER BY dl.region, dt.year;

CREATE INDEX idx_agg_region ON agg_demographics_by_region(region, year);
