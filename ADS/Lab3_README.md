# Lab #3: Data Warehouse (PostgreSQL)

## Що робиться

Завантаження даних з JSON файлів у PostgreSQL, створення Star Schema, побудова агрегаційних таблиць.

## Візуалізація процесу

```
[Lab #2 Datasets]
ds_location, ds_time, ds_fact
        │
        ▼
┌────────────────────────┐
│  create_tables         │
│  (Star Schema DDL)     │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      ▼           ▼
┌─────────┐   ┌─────────┐
│ load_   │   │ load_   │
│ location│   │ time    │
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            ▼
     ┌─────────────┐
     │ load_facts  │
     └──────┬──────┘
            ▼
     ┌─────────────┐
     │  validate   │
     └──────┬──────┘
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
   ┌────┐┌────┐┌────┐
   │agg_││agg_││agg_│
   │reg ││inc ││trd │
   └──┬─┘└──┬─┘└──┬─┘
      └─────┼─────┘
            ▼
   ┌─────────────────┐
   │ warehouse_ready │
   │  (EmptyOp)      │
   └────────┬────────┘
            │
            ▼
     [ds_warehouse_ready]
            │
            ▼
        Lab #4
```

## Створені таблиці PostgreSQL

### Dimensions (Виміри)

#### 1. dim_location
```sql
CREATE TABLE dim_location (
    country_key VARCHAR(32) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(3),
    region VARCHAR(50),
    income_group VARCHAR(50)
);
```
**Оновлення:** Full Refresh (TRUNCATE CASCADE + INSERT)

#### 2. dim_time
```sql
CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,
    year INTEGER NOT NULL
);
```
**Оновлення:** Full Refresh

### Fact (Факти)

#### 3. fact_demographics
```sql
CREATE TABLE fact_demographics (
    country_key VARCHAR(32) REFERENCES dim_location(country_key),
    time_key INTEGER REFERENCES dim_time(time_key),
    country_population BIGINT,
    fertility_rate FLOAT,
    life_expectancy FLOAT,
    PRIMARY KEY (country_key, time_key)
);
```
**Грануляція:** Країна × Рік  
**Оновлення:** Full Refresh

### Aggregates (Агрегації)

#### 4. agg_demographics_by_region
```sql
CREATE TABLE agg_demographics_by_region AS
SELECT 
    dl.region,
    dt.year,
    COUNT(*) as countries_count,
    AVG(fd.country_population) as avg_population,
    AVG(fd.fertility_rate) as avg_fertility_rate,
    AVG(fd.life_expectancy) as avg_life_expectancy
FROM fact_demographics fd
JOIN dim_location dl ON fd.country_key = dl.country_key
JOIN dim_time dt ON fd.time_key = dt.time_key
GROUP BY dl.region, dt.year;
```
**Грануляція:** Регіон × Рік

#### 5. agg_demographics_by_income
```sql
-- Структура аналогічна до by_region
-- але GROUP BY dl.income_group, dt.year
```
**Грануляція:** Income Group × Рік

#### 6. agg_yearly_trends
```sql
-- Глобальні тренди
-- GROUP BY dt.year (без регіонів)
```
**Грануляція:** Рік (глобально)

## Як запустити

**Автоматично:** Lab #3 запускається автоматично після Lab #2 (через Datasets)

**Вручну:**
```bash
# В Airflow UI
DAGs → load_to_db → Trigger DAG

# Або через CLI
docker exec ads-airflow-scheduler-1 airflow dags trigger load_to_db
```

## Налаштування

**DAG ID:** `load_to_db`  
**Schedule:** `[ds_location, ds_time, ds_fact]` (Dataset-driven)  
**Tasks:** 9 tasks  

**Connection:**
- Host: `postgres`
- Port: `5432`
- Database: `airflow`
- User: `airflow`
- Connection ID: `postgres_default`

## Роль та відповідальність

**Роль:** DWH Administrator   

**Обов'язки:**
- Моніторинг завантаження даних
- Валідація Foreign Keys
- Перевірка цілісності даних
- Моніторинг розміру БД

## Schema: Star Schema

```
         dim_location                 dim_time
      ┌──────────────┐            ┌──────────┐
      │ country_key  │PK          │ time_key │PK
      │ country_name │            │ year     │
      │ region       │            └────┬─────┘
      │ income_group │                 │
      └──────┬───────┘                 │
             │                         │
             │ FK                   FK │
             │        ┌────────────────┤
             └───────>│ fact_demographics
                      │──────────────────┐
                      │ country_key   FK │
                      │ time_key      FK │
                      │ population       │
                      │ fertility_rate   │
                      │ life_expectancy  │
                      └──────────────────┘
```

## Outputs → Inputs для Lab #4

**Dataset створений:** `ds_warehouse_ready`  
Створюється task `warehouse_ready` (EmptyOperator) після завершення всіх 3 агрегацій.

Lab #4 запуститься автоматично після цього датасету.

## Перевірка результатів

```sql
-- Підключитись до PostgreSQL
docker exec -it ads-postgres-1 psql -U airflow -d airflow

-- Перевірити таблиці
\dt

-- Порахувати записи
SELECT 
    'dim_location' as table_name, 
    COUNT(*) as rows 
FROM dim_location
UNION ALL
SELECT 'dim_time', COUNT(*) FROM dim_time
UNION ALL
SELECT 'fact_demographics', COUNT(*) FROM fact_demographics
UNION ALL
SELECT 'agg_by_region', COUNT(*) FROM agg_demographics_by_region;

-- Перевірити FK integrity
SELECT COUNT(*) FROM fact_demographics f
LEFT JOIN dim_location l ON f.country_key = l.country_key
WHERE l.country_key IS NULL;
-- Має бути 0
```

**Критерії успішності:**
- ✅ 6 таблиць створені
- ✅ Немає NULL в Foreign Keys
- ✅ Агрегації містять дані
- ✅ Dataset `ds_warehouse_ready` створено
