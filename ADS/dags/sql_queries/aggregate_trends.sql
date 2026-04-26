DROP TABLE IF EXISTS agg_yearly_trends CASCADE;

CREATE TABLE agg_yearly_trends AS
WITH yearly_data AS (
    SELECT 
        dt.year,
        AVG(fd.country_population) as avg_population,
        AVG(fd.fertility_rate) as avg_fertility_rate,
        AVG(fd.life_expectancy) as avg_life_expectancy,
        SUM(fd.country_population) as total_population
    FROM fact_demographics fd
    JOIN dim_time dt ON fd.time_key = dt.time_key
    GROUP BY dt.year
)
SELECT 
    year,
    ROUND(avg_population::numeric, 0) as avg_population,
    ROUND(avg_fertility_rate::numeric, 2) as avg_fertility_rate,
    ROUND(avg_life_expectancy::numeric, 2) as avg_life_expectancy,
    total_population,
    ROUND((
        (avg_population - LAG(avg_population) OVER (ORDER BY year)) / 
        NULLIF(LAG(avg_population) OVER (ORDER BY year), 0) * 100
    )::numeric, 2) as population_change_pct
FROM yearly_data
ORDER BY year;

CREATE INDEX idx_agg_trends ON agg_yearly_trends(year);
