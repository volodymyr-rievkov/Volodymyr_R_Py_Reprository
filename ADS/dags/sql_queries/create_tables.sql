CREATE TABLE IF NOT EXISTS dim_location (
    country_key SERIAL PRIMARY KEY,
    country_name VARCHAR(255),
    country_code VARCHAR(10) UNIQUE,
    region VARCHAR(100),
    income_group VARCHAR(100),
    special_notes TEXT
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_key SERIAL PRIMARY KEY,
    year INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_demographics (
    fact_key SERIAL PRIMARY KEY,
    country_key INTEGER REFERENCES dim_location(country_key),
    time_key INTEGER REFERENCES dim_time(time_key),
    country_population BIGINT,
    fertility_rate NUMERIC(10, 2),
    life_expectancy NUMERIC(5, 2),
    UNIQUE(country_key, time_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_country ON fact_demographics(country_key);
CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_demographics(time_key);
