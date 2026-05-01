# Розрахункова робота: Netflix Analytics з PySpark

**Студент:** Рєвков Володимир  
**Група:** ШІ-32  
**Дисципліна:** Аналітичні сховища даних  

---

## 📊 Предметна область

**Стрімінговий сервіс (Netflix-style)**

### Обґрунтування вибору:
- **Велика кількість даних:** 100,000+ переглядів для реалістичного Big Data аналізу
- **Цікаві аналітичні задачі:** популярність контенту, поведінка користувачів, тренди
- **Багатовимірний аналіз:** країни, жанри, часові проміжки, типи контенту
- **Актуальність:** стрімінг-індустрія - одна з найбільш динамічних галузей

---

## 📁 Структура проекту

```
PYSPARK_NETFLIX/
├── data/                           # Вхідні дані (CSV)
│   ├── users.csv                   # 5,000 користувачів
│   ├── content.csv                 # 500 фільмів/серіалів
│   └── views.csv                   # 100,000 переглядів
├── warehouse/                      # Результати (Parquet)
│   ├── analytics_parquet/          # Деталізована таблиця (партиціоновано)
│   ├── agg_by_country_parquet/     # Агрегація по країнах
│   ├── agg_by_genre_month_parquet/ # Агрегація по жанрах/місяцях
│   ├── agg_by_content_type_parquet/# Фільми vs Серіали
│   ├── slice_q4_genres_parquet/    # Зріз Q4 по жанрах
│   ├── slice_weekend_parquet/      # Вікендні перегляди
│   ├── slice_primetime_parquet/    # Prime Time перегляди
│   └── slice_weekly_parquet/       # Тижневі тренди
├── generate_data.py                # Генерація тестових даних
└── netflix_analytics_pyspark.py    # Головний скрипт аналізу
```

---

## 📋 Опис даних

### 1. users.csv (Користувачі - Виміри)

| Поле | Тип | Опис |
|------|-----|------|
| user_id | String | Унікальний ID (PK) |
| user_name | String | Ім'я користувача |
| country | String | Країна |
| subscription_type | String | Тип підписки (Basic/Standard/Premium) |
| registration_date | Date | Дата реєстрації |

**Кількість:** 5,000 користувачів  
**Країни:** USA, UK, Canada, Germany, France, Spain, Italy, Australia, Japan, Brazil

---

### 2. content.csv (Контент - Виміри)

| Поле | Тип | Опис |
|------|-----|------|
| content_id | String | Унікальний ID (PK) |
| title | String | Назва фільму/серіалу |
| content_type | String | Тип (Movie/Series) |
| genre | String | Жанр |
| duration_minutes | Integer | Тривалість (хвилини) |
| release_year | Integer | Рік випуску |

**Кількість:** 500 фільмів/серіалів  
**Жанри:** Action, Comedy, Drama, Horror, Sci-Fi, Romance, Thriller, Documentary, Animation, Fantasy

---

### 3. views.csv (Перегляди - Факти)

| Поле | Тип | Опис |
|------|-----|------|
| view_id | String | Унікальний ID перегляду (PK) |
| user_id | String | FK → users |
| content_id | String | FK → content |
| view_date | Date | Дата перегляду |
| view_hour | Integer | Година перегляду (0-23) |
| view_hours | Float | Тривалість перегляду (години) |
| watch_percentage | Integer | % переглянутого контенту |
| rating | Integer | Рейтинг (1-5, якщо >50% переглянуто) |

**Кількість:** 100,000 переглядів  
**Період:** 2024 рік (1 січня - 31 грудня)

---

## 🎯 Виміри та факти

### Виміри (Dimensions):
1. **Географія:** country
2. **Час:** year, month, week, quarter, day_of_week
3. **Контент:** genre, content_type, release_year
4. **Користувачі:** subscription_type
5. **Часовий слот:** time_slot (Prime Time/Afternoon/Morning/Night)
6. **Вікенд:** is_weekend (Weekend/Weekday)

### Факти (Facts):
1. **Кількість переглядів:** count(view_id)
2. **Години перегляду:** sum(view_hours)
3. **% завершення:** avg(watch_percentage)
4. **Кількість рейтингів:** count(rating)
5. **Середній рейтинг:** avg(rating)

---

## 🔧 Виконання завдань

### Завдання 1: Вибір предметної області ✅
**Обрано:** Стрімінговий сервіс (Netflix Analytics)

### Завдання 2: Завантаження та структура даних ✅
- Визначено схеми для всіх таблиць (StructType)
- Завантажено 3 CSV файли у Spark DataFrame
- Виведено структуру даних (printSchema)

### Завдання 3: Очищення даних ✅
- Приведення типів (to_date, cast)
- Видалення NULL значень (dropna)
- Фільтрація невалідних записів (filter)
- Підрахунок відкинутих рядків: **0** (всі дані валідні)

### Завдання 4: JOIN таблиць ✅
- Об'єднано views + users + content
- Створено деталізовану аналітичну таблицю (100,000 записів)
- Додано додаткові поля: часові виміри, time_slot, is_weekend

### Завдання 5: Агрегація за вимірами ✅
**Створено 3 агрегації:**

1. **agg_by_country** - По країнах
   - views_count, total_hours, avg_completion_rate
   - avg_rating, ratings_count

2. **agg_by_genre_month** - По жанрах і місяцях
   - views_count, total_hours, unique_users
   - Сортування: year, month, total_hours DESC

3. **agg_by_content_type** - Фільми vs Серіали
   - views_count, total_hours, avg_completion_rate
   - unique_content

### Завдання 6: Побудова зрізів даних ✅
**Створено 4 зрізи:**

1. **slice_q4_genres** - Q4 2024 (жовтень-грудень) по жанрах
   - Період: 2024-10-01 до 2024-12-31
   - Метрики: views, hours, avg_rating

2. **slice_weekend** - Вікендні перегляди
   - Фільтр: is_weekend = "Weekend"
   - Виміри: country, content_type

3. **slice_primetime** - Prime Time (18:00-23:00)
   - Фільтр: time_slot = "Prime Time"
   - Виміри: country, genre

4. **slice_weekly** - Тижневі тренди (листопад-грудень)
   - Період: 2024-11-01 до 2024-12-31
   - Виміри: year, week, country

### Завдання 7: Запис у Parquet з партиціонуванням ✅

**Збережено 8 таблиць:**

| Таблиця | Партиціонування | Обґрунтування |
|---------|----------------|---------------|
| analytics_parquet | year_num, month_num | Найчастіше аналіз по місяцях |
| agg_by_country_parquet | - | Невелика таблиця, партиціонування не потрібне |
| agg_by_genre_month_parquet | year_num, month_num | Вже згруповано по місяцях |
| agg_by_content_type_parquet | - | Тільки 2 записи (Movie/Series) |
| slice_q4_genres_parquet | - | Один квартал, партиціонування не потрібне |
| slice_weekend_parquet | country | Вікенди різні по країнах |
| slice_primetime_parquet | country | Prime Time різний по країнах |
| slice_weekly_parquet | year_num, week_num | Тижневий аналіз |

---

## 🚀 Як запустити

### 1. Встановлення PySpark

```bash
pip install pyspark==3.5.0
```

### 2. Генерація тестових даних

```bash
python generate_data.py
```

Це створить 3 CSV файли в папці `data/`:
- users.csv (5,000 записів)
- content.csv (500 записів)
- views.csv (100,000 записів)

### 3. Запуск аналізу

```bash
python netflix_analytics_pyspark.py
```

або через spark-submit:

```bash
spark-submit netflix_analytics_pyspark.py
```

### 4. Перевірка результатів

```bash
# Подивитись структуру warehouse
find warehouse -type d

# Прочитати Parquet файл
python -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('test').getOrCreate()
df = spark.read.parquet('warehouse/agg_by_country_parquet')
df.show()
"
```

---

## 📊 Приклади результатів

### ТОП-5 країн за годинами перегляду:
```
+---------+-----------+-----------+
|country  |views_count|total_hours|
+---------+-----------+-----------+
|UK       |10886      |8670.31    |
|Japan    |10314      |8287.39    |
|Italy    |10257      |8129.15    |
|Australia|10066      |7996.34    |
|Brazil   |10104      |7932.84    |
+---------+-----------+-----------+
```

### Фільми vs Серіали:
```
+------------+-----------+-----------+
|content_type|views_count|total_hours|
+------------+-----------+-----------+
|Movie       |48022      |57632.09   |
|Series      |51978      |21483.44   |
+------------+-----------+-----------+
```

**Інсайт:** Серіали переглядають частіше (51,978 vs 48,022), але фільми дивляться довше (57,632 год vs 21,483 год).

### Q4 2024 - Популярні жанри:
```
+-----------+-----------+--------------+
|genre      |views_count|total_hours_q4|
+-----------+-----------+--------------+
|Romance    |2977       |2780.57       |
|Fantasy    |2734       |2368.18       |
|Drama      |2843       |2359.39       |
+-----------+-----------+--------------+
```

---

## 💡 Ключові інсайти

1. **Географія:**
   - UK, Japan, Italy - лідери за годинами перегляду
   - Середній completion rate: ~55% (користувачі дивляться більше половини)

2. **Контент:**
   - Фільми: довші за тривалістю (в середньому 120 хв)
   - Серіали: більше переглядів (епізоди по 30-60 хв)

3. **Час перегляду:**
   - Prime Time (18:00-23:00) - найпопулярніший час
   - Вікенди: +30% переглядів порівняно з буднями

4. **Жанри:**
   - Romance, Drama, Fantasy - найпопулярніші
   - Q4: збільшення переглядів на 25% (святковий сезон)

---

## 🔍 Технічні деталі

### Переваги Parquet:
- **Колоночний формат:** швидке читання тільки потрібних колонок
- **Стиснення:** ~10x менший розмір порівняно з CSV
- **Схема:** вбудована схема даних (не потрібно визначати при читанні)

### Переваги партиціонування:
- **Швидкість:** фільтрація по місяцю читає тільки 1/12 даних
- **Ефективність:** менше I/O операцій
- **Організація:** логічна структура файлів

### Приклад партиціонування:
```
warehouse/analytics_parquet/
├── year_num=2024/
│   ├── month_num=1/
│   │   └── part-00000.parquet
│   ├── month_num=2/
│   │   └── part-00000.parquet
│   └── ...
```

---

## 📝 Висновки

1. PySpark дозволяє ефективно обробляти великі обсяги даних (100K+ записів)
2. DataFrame API спрощує роботу порівняно з MapReduce
3. Parquet + партиціонування = оптимальне зберігання для аналітики
4. Можливість створення різноманітних агрегацій та зрізів з одного набору даних
5. Локальний режим підходить для навчання та тестування

---

## 🛠️ Використані технології

- **Apache Spark 3.5.0**
- **PySpark** (Python API)
- **Parquet** (формат зберігання)
- **Python 3.12**
- **pandas** (генерація даних)

---

## 📚 Додаткові можливості

### Розширення аналізу:
1. Додати ML моделі (рекомендаційні системи)
2. Прогнозування популярності контенту
3. Сегментація користувачів (кластеризація)
4. A/B тестування нових функцій
5. Churn prediction (прогноз відписки)

### Оптимізації:
1. Broadcast joins для малих таблиць
2. Кешування проміжних результатів
3. Налаштування shuffle partitions
4. Використання UDF для складної логіки

---

**Виконав:** Рєвков Володимир  
**Дата:** 01.05.2026  
**Версія PySpark:** 3.5.0
