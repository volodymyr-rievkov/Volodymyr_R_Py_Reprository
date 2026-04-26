DROP TABLE IF EXISTS dm_regional_demographics CASCADE;

CREATE TABLE dm_regional_demographics AS
SELECT 
    dl.region,
    dt.year,
    COUNT(DISTINCT dl.country_key) as countries_count,
    
    ROUND(AVG(fd.country_population)::numeric, 0) as avg_population,
    ROUND(MIN(fd.country_population)::numeric, 0) as min_population,
    ROUND(MAX(fd.country_population)::numeric, 0) as max_population,
    SUM(fd.country_population) as total_population,
    
    ROUND(AVG(fd.fertility_rate)::numeric, 2) as avg_fertility_rate,
    ROUND(MIN(fd.fertility_rate)::numeric, 2) as min_fertility_rate,
    ROUND(MAX(fd.fertility_rate)::numeric, 2) as max_fertility_rate,
    
    ROUND(AVG(fd.life_expectancy)::numeric, 2) as avg_life_expectancy,
    ROUND(MIN(fd.life_expectancy)::numeric, 2) as min_life_expectancy,
    ROUND(MAX(fd.life_expectancy)::numeric, 2) as max_life_expectancy,
    
    CURRENT_TIMESTAMP as updated_at
FROM fact_demographics fd
JOIN dim_location dl ON fd.country_key = dl.country_key
JOIN dim_time dt ON fd.time_key = dt.time_key
WHERE dl.region IS NOT NULL
GROUP BY dl.region, dt.year
ORDER BY dl.region, dt.year;

CREATE INDEX idx_dm_regional_region ON dm_regional_demographics(region);
CREATE INDEX idx_dm_regional_year ON dm_regional_demographics(year);
CREATE INDEX idx_dm_regional_region_year ON dm_regional_demographics(region, year);
