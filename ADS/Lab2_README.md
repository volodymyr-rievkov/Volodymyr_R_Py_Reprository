# Lab #2: ETL Pipeline (Excel → JSON)

## Що робиться

Витягування даних з Excel файлу, трансформація та збереження у JSON формат для подальшого завантаження в Data Warehouse.

## Візуалізація процесу

```
┌────────────────────────┐
│  Excel Source File     │
│  (demographics.xls)    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  extract_data          │
│  (Read Excel sheets)   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  transform_data        │
│  (Clean, normalize)    │
└───────┬────────────────┘
        │
        ├──────────────┬─────────────┐
        ▼              ▼             ▼
┌─────────────┐  ┌──────────┐  ┌──────────┐
│ save_       │  │ save_    │  │ save_    │
│ location    │  │ time     │  │ facts    │
└──────┬──────┘  └────┬─────┘  └────┬─────┘
       │              │             │
       ▼              ▼             ▼
┌─────────────┐  ┌──────────┐  ┌──────────┐
│ dim_        │  │ dim_     │  │ fact_    │
│ location    │  │ time     │  │ demo-    │
│ .json       │  │ .json    │  │ graphics │
│             │  │          │  │ .json    │
└─────────────┘  └──────────┘  └──────────┘
       │              │             │
       └──────────────┴─────────────┘
                      │
                      ▼
              [Datasets Created]
           ds_location, ds_time, ds_fact
```

## Створені файли

### 1. dim_location.json
**Структура:**
```
{
    "Country_Key":1,
    "Country_Name":"Aruba",
    "Country_Code":"ABW",
    "Region":"Latin America & Caribbean",
    "Income_Group":"High income: nonOECD",
    "Special_Notes":"SNA data for 2000-2011 are updated from official government statistics; 1994-1999 from UN databases. Base year has changed from 1995 to 2000."
},
```
**Записів:** ~200 країн

### 2. dim_time.json
**Структура:**
```
{
    "Time_Key":1,
    "Year":1960
},
```
**Записів:** ~50 років

### 3. fact_demographics.json
**Структура:**
```
{
    "Fact_Key":1,
    "Country_Key":1,
    "Time_Key":1,
    "Country_Population":54208.0,
    "Fertility_Rate":65.5693658537,
    "Life_Expectancy":4.82
},
```
**Записів:** ~50,000

## Як запустити

```bash
# 1. Помістити Excel файл
cp Population_fertility_rate_Life_expectancy.xls dags/data/raw/


# 2. В Airflow UI увімкнути DAG
transform_to_json

# 3. Trigger DAG вручну
```

**Або через CLI:**
```bash
docker exec ads-airflow-scheduler-1 airflow dags trigger transform_to_json
```

## Налаштування

**DAG ID:** `transform_to_json`  
**Schedule:** `manual trigger`
**Tasks:** 5 tasks (extract → transform → save×3)  

## Роль та відповідальність

**Роль:** Data Engineer  

**Обов'язки:**
- Моніторинг завантаження Excel файлів
- Перевірка якості трансформації
- Валідація створених JSON файлів

## Outputs → Inputs для Lab #3

Створені Datasets автоматично запускають Lab #3:
- `ds_location` → сигнал що dim_location готовий
- `ds_time` → сигнал що dim_time готовий
- `ds_fact` → сигнал що fact_demographics готовий

Lab #3 запуститься автоматично коли всі 3 datasets будуть створені.

## Перевірка результатів

```bash
# Перевірити чи створились файли
ls -lh dags/data/processed/

# Подивитись вміст
cat dags/data/processed/dim_location.json | jq '.' | head -20
```

**Критерії успішності:**
- ✅ 3 JSON файли створені
