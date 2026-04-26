# Lab #4: Data Marts (Вітрини даних)

## Що робиться

Створення бізнес-орієнтованих вітрин даних для різних категорій користувачів на базі Data Warehouse.

## Візуалізація процесу

```
[Lab #3 Dataset]
ds_warehouse_ready
        │
        ▼
┌───────────────────────────┐
│  DWH Tables Available:    │
│  - fact_demographics      │
│  - dim_location           │
│  - dim_time               │
│  - agg_* (3 tables)       │
└───────────┬───────────────┘
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
   ┌────┐┌────┐┌────┐
   │ dm_││ dm_││ dm_│
   │reg ││inc ││trd │
   └──┬─┘└──┬─┘└──┬─┘
      │     │     │
      ▼     ▼     ▼
┌──────────────────────┐
│ dm_regional_         │
│ demographics         │
│ (~500 records)       │
│                      │
│ For: Geographers     │
└──────────────────────┘

┌──────────────────────┐
│ dm_income_groups     │
│ (~250 records)       │
│                      │
│ For: Economists      │
└──────────────────────┘

┌──────────────────────┐
│ dm_yearly_trends     │
│ (10 records)         │
│                      │
│ For: Strategists     │
└──────────────────────┘
```

## Створені таблиці (Data Marts)

### 1. dm_regional_demographics
**Призначення:** Демографія по географічних регіонах  
**Для кого:** Геоаналітики, регіональні менеджери

**Структура:**
```sql
CREATE TABLE dm_regional_demographics AS
SELECT 
    dl.region,
    dt.year,
    COUNT(DISTINCT dl.country_key) as countries_count,
    -- Населення
    ROUND(AVG(fd.country_population), 0) as avg_population,
    ROUND(MIN(fd.country_population), 0) as min_population,
    ROUND(MAX(fd.country_population), 0) as max_population,
    SUM(fd.country_population) as total_population,
    -- Фертильність
    ROUND(AVG(fd.fertility_rate), 2) as avg_fertility_rate,
    ROUND(MIN(fd.fertility_rate), 2) as min_fertility_rate,
    ROUND(MAX(fd.fertility_rate), 2) as max_fertility_rate,
    -- Тривалість життя
    ROUND(AVG(fd.life_expectancy), 2) as avg_life_expectancy,
    ROUND(MIN(fd.life_expectancy), 2) as min_life_expectancy,
    ROUND(MAX(fd.life_expectancy), 2) as max_life_expectancy,
    CURRENT_TIMESTAMP as updated_at
FROM fact_demographics fd
JOIN dim_location dl ON fd.country_key = dl.country_key
JOIN dim_time dt ON fd.time_key = dt.time_key
WHERE dl.region IS NOT NULL
GROUP BY dl.region, dt.year;
```

**Грануляція:** Регіон × Рік  
**Індекси:** region, year, (region, year)

---

### 2. dm_income_groups
**Призначення:** Порівняння демографії по економічних групах  
**Для кого:** Економісти, фінансові аналітики

**Структура:**
```sql
CREATE TABLE dm_income_groups AS
SELECT 
    dl.income_group,
    dt.year,
    COUNT(DISTINCT dl.country_key) as countries_count,
    -- Основні метрики
    ROUND(AVG(fd.country_population), 0) as avg_population_per_country,
    SUM(fd.country_population) as total_population,
    ROUND(AVG(fd.fertility_rate), 2) as avg_fertility_rate,
    ROUND(AVG(fd.life_expectancy), 2) as avg_life_expectancy,
    -- Відхилення від світового середнього
    ROUND(
        AVG(fd.life_expectancy) - (
            SELECT AVG(life_expectancy) 
            FROM fact_demographics f2 
            JOIN dim_time t2 ON f2.time_key = t2.time_key 
            WHERE t2.year = dt.year
        ), 2
    ) as life_exp_diff_from_global_avg,
    -- % населення від світу
    ROUND(
        (SUM(fd.country_population)::numeric / (
            SELECT SUM(country_population) 
            FROM fact_demographics f2 
            JOIN dim_time t2 ON f2.time_key = t2.time_key 
            WHERE t2.year = dt.year
        ) * 100), 2
    ) as population_share_pct,
    CURRENT_TIMESTAMP as updated_at
FROM fact_demographics fd
JOIN dim_location dl ON fd.country_key = dl.country_key
JOIN dim_time dt ON fd.time_key = dt.time_key
WHERE dl.income_group IS NOT NULL
GROUP BY dl.income_group, dt.year;
```

**Грануляція:** Income Group × Рік  
**Індекси:** income_group, year

---

### 3. dm_yearly_trends
**Призначення:** Глобальні тренди за останні 10 років  
**Для кого:** Топ-менеджмент, стратеги

**Структура:**
```sql
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
        ROUND(avg_population, 0) as avg_population,
        ROUND(avg_fertility_rate, 2) as avg_fertility_rate,
        ROUND(avg_life_expectancy, 2) as avg_life_expectancy,
        total_population,
        -- YoY зміни
        LAG(avg_population) OVER (ORDER BY year) as prev_avg_population,
        LAG(avg_fertility_rate) OVER (ORDER BY year) as prev_avg_fertility,
        LAG(avg_life_expectancy) OVER (ORDER BY year) as prev_avg_life_exp,
        -- % зміни
        ROUND((
            (avg_population - LAG(avg_population) OVER (ORDER BY year)) / 
            LAG(avg_population) OVER (ORDER BY year) * 100
        ), 2) as population_change_pct,
        ROUND((
            (avg_fertility_rate - LAG(avg_fertility_rate) OVER (ORDER BY year)) / 
            LAG(avg_fertility_rate) OVER (ORDER BY year) * 100
        ), 2) as fertility_change_pct,
        ROUND((avg_life_expectancy - LAG(avg_life_expectancy) OVER (ORDER BY year)), 2) 
            as life_exp_change_years
    FROM yearly_stats
)
SELECT 
    *,
    -- Класифікація трендів
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
WHERE year >= (SELECT MAX(year) - 10 FROM trends);
```

**Грануляція:** Рік (глобально)  
**Індекси:** year

---

## Як запустити

**Автоматично:** Lab #4 запускається автоматично після Lab #3 (через Dataset `ds_warehouse_ready`)

**Вручну:**
```bash
# В Airflow UI
DAGs → update_datamarts → Trigger DAG

# Або через CLI
docker exec ads-airflow-scheduler-1 airflow dags trigger update_datamarts
```

## Налаштування

**DAG ID:** `update_datamarts`  
**Schedule:** `[ds_warehouse_ready]` (Dataset-driven)  
**Tasks:** 3 tasks (паралельно)  
**Стратегія оновлення:** Full Refresh (DROP + CREATE)

## Роль та відповідальність

**Роль:** BI Developer  

**Обов'язки:**
- Моніторинг оновлення вітрин
- Оптимізація запитів
- Створення нових вітрин за запитом
- Документування бізнес-логіки

## Порівняння Data Marts

| Mart | Аудиторія | Грануляція | Записів | Задачі |
|------|-----------|------------|---------|--------|
| dm_regional_demographics | Геоаналітики | Регіон × Рік | ~500 | Регіональні тренди |
| dm_income_groups | Економісти | Income × Рік | ~250 | Економічна нерівність |
| dm_yearly_trends | Стратеги | Рік | 10 | Глобальні YoY зміни |

## Приклади використання

### Регіональна демографія
```sql
-- ТОП-3 регіони за тривалістю життя у 2020
SELECT region, avg_life_expectancy
FROM dm_regional_demographics
WHERE year = 2020
ORDER BY avg_life_expectancy DESC
LIMIT 3;
```

### Економічні групи
```sql
-- Різниця між High/Low income у 2020
SELECT 
    income_group,
    avg_life_expectancy,
    life_exp_diff_from_global_avg
FROM dm_income_groups
WHERE year = 2020
ORDER BY avg_life_expectancy DESC;
```

### Річні тренди
```sql
-- Останні 5 років з трендами
SELECT 
    year,
    avg_life_expectancy,
    life_exp_change_years,
    health_trend
FROM dm_yearly_trends
ORDER BY year DESC
LIMIT 5;
```

## Перевірка результатів

```sql
-- Підключитись до PostgreSQL
docker exec -it ads-postgres-1 psql -U airflow -d airflow

-- Перевірити вітрини
SELECT 
    'dm_regional_demographics' as mart,
    COUNT(*) as rows,
    MAX(updated_at) as last_update
FROM dm_regional_demographics
UNION ALL
SELECT 'dm_income_groups', COUNT(*), MAX(updated_at)
FROM dm_income_groups
UNION ALL
SELECT 'dm_yearly_trends', COUNT(*), MAX(updated_at)
FROM dm_yearly_trends;

-- Перевірити свіжість даних
SELECT 
    CURRENT_TIMESTAMP - MAX(updated_at) as age
FROM dm_regional_demographics;
-- Має бути < 5 хвилин
```

**Критерії успішності:**
- ✅ 3 вітрини створені
- ✅ updated_at свіжий (< 5 хв)
- ✅ Всі індекси створені
