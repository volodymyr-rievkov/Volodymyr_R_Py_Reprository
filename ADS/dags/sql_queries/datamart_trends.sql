DROP TABLE IF EXISTS dm_yearly_trends CASCADE;

CREATE TABLE dm_yearly_trends AS
WITH yearly_stats AS (
    SELECT 
        dt.year,
        COUNT(DISTINCT fd.country_key) as countries_count,
        AVG(fd.country_population) as avg_population,
        AVG(fd.fertility_rate) as avg_fertility_rate,
        AVG(fd.life_expectancy) as avg_life_expectancy,
        SUM(fd.country_population) as total_population
    FROM fact_demographics fd
    JOIN dim_time dt ON fd.time_key = dt.time_key
    GROUP BY dt.year
),
trends AS (
    SELECT 
        year,
        countries_count,
        ROUND(avg_population::numeric, 0) as avg_population,
        ROUND(avg_fertility_rate::numeric, 2) as avg_fertility_rate,
        ROUND(avg_life_expectancy::numeric, 2) as avg_life_expectancy,
        total_population,
        
        LAG(avg_population) OVER (ORDER BY year) as prev_avg_population,
        LAG(avg_fertility_rate) OVER (ORDER BY year) as prev_avg_fertility,
        LAG(avg_life_expectancy) OVER (ORDER BY year) as prev_avg_life_exp,
        
        ROUND((
            (avg_population - LAG(avg_population) OVER (ORDER BY year)) / 
            NULLIF(LAG(avg_population) OVER (ORDER BY year), 0) * 100
        )::numeric, 2) as population_change_pct,
        
        ROUND((
            (avg_fertility_rate - LAG(avg_fertility_rate) OVER (ORDER BY year)) / 
            NULLIF(LAG(avg_fertility_rate) OVER (ORDER BY year), 0) * 100
        )::numeric, 2) as fertility_change_pct,
        
        ROUND((avg_life_expectancy - LAG(avg_life_expectancy) OVER (ORDER BY year))::numeric, 2) 
            as life_exp_change_years
    FROM yearly_stats
)
SELECT 
    year,
    countries_count,
    avg_population,
    avg_fertility_rate,
    avg_life_expectancy,
    total_population,
    prev_avg_population,
    prev_avg_fertility,
    prev_avg_life_exp,
    population_change_pct,
    fertility_change_pct,
    life_exp_change_years,
    
    CASE 
        WHEN population_change_pct > 0 THEN 'Зростання'
        WHEN population_change_pct < 0 THEN 'Спад'
        ELSE 'Стабільно'
    END as population_trend,
    
    CASE 
        WHEN life_exp_change_years > 0 THEN 'Покращення'
        WHEN life_exp_change_years < 0 THEN 'Погіршення'
        ELSE 'Стабільно'
    END as health_trend,
    
    CURRENT_TIMESTAMP as updated_at
FROM trends
WHERE year >= (SELECT MAX(year) - 10 FROM trends)
ORDER BY year DESC;

CREATE INDEX idx_dm_trends_year ON dm_yearly_trends(year);
