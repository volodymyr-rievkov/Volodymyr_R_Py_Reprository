DROP TABLE IF EXISTS dm_income_groups CASCADE;

CREATE TABLE dm_income_groups AS
SELECT 
    dl.income_group,
    dt.year,
    COUNT(DISTINCT dl.country_key) as countries_count,
    
    ROUND(AVG(fd.country_population)::numeric, 0) as avg_population_per_country,
    SUM(fd.country_population) as total_population,
    ROUND(AVG(fd.fertility_rate)::numeric, 2) as avg_fertility_rate,
    ROUND(AVG(fd.life_expectancy)::numeric, 2) as avg_life_expectancy,
    
    ROUND(
        AVG(fd.life_expectancy) - (
            SELECT AVG(life_expectancy) 
            FROM fact_demographics f2 
            JOIN dim_time t2 ON f2.time_key = t2.time_key 
            WHERE t2.year = dt.year
        ), 2
    ) as life_exp_diff_from_global_avg,
    
    ROUND(
        (SUM(fd.country_population)::numeric / NULLIF(
            (SELECT SUM(country_population) FROM fact_demographics f2 
             JOIN dim_time t2 ON f2.time_key = t2.time_key 
             WHERE t2.year = dt.year), 0
        ) * 100), 2
    ) as population_share_pct,
    
    CURRENT_TIMESTAMP as updated_at
FROM fact_demographics fd
JOIN dim_location dl ON fd.country_key = dl.country_key
JOIN dim_time dt ON fd.time_key = dt.time_key
WHERE dl.income_group IS NOT NULL
GROUP BY dl.income_group, dt.year
ORDER BY dl.income_group, dt.year;

CREATE INDEX idx_dm_income_group ON dm_income_groups(income_group);
CREATE INDEX idx_dm_income_year ON dm_income_groups(year);
