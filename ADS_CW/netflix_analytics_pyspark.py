from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    count,
    lit,
    month,
    quarter,
    round as spark_round,
    sum as spark_sum,
    avg,
    to_date,
    weekofyear,
    year,
    dayofweek,
    when,
    hour
)
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
    DateType,
    DoubleType
)
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

PATH = Path.cwd()

USERS_CSV = PATH / "data" / "users.csv"
CONTENT_CSV = PATH / "data" / "content.csv"
VIEWS_CSV = PATH / "data" / "views.csv"


users_schema = StructType([
    StructField("user_id", StringType(), False),
    StructField("user_name", StringType(), True),
    StructField("country", StringType(), True),
    StructField("subscription_type", StringType(), True),
    StructField("registration_date", DateType(), True), 
])

content_schema = StructType([
    StructField("content_id", StringType(), False),
    StructField("title", StringType(), True),
    StructField("content_type", StringType(), True),
    StructField("genre", StringType(), True),
    StructField("duration_minutes", IntegerType(), True),
    StructField("release_year", IntegerType(), True),
])

views_schema = StructType([
    StructField("view_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("content_id", StringType(), False),
    StructField("view_date", DateType(), True),
    StructField("view_hour", IntegerType(), True),   
    StructField("view_hours", DoubleType(), True),
    StructField("watch_percentage", DoubleType(), True),
    StructField("rating", DoubleType(), True)
])


@contextmanager
def create_spark_session(name: str = "NetflixAnalyticsPySpark") -> Generator[SparkSession, None, None]:
    print(f"Creating Session with local mode for app {name}")
    spark = (
        SparkSession.builder
        .appName("NetflixAnalyticsPySpark")
        .master("local[3]")  # 3 threads
        .config("spark.sql.shuffle.partitions", "3")  # 3 partitions
        .getOrCreate()
    )
    print(f"Spark session created, version: {spark.version}")
    try:
        yield spark
    finally:
        spark.stop()

def load_csv(spark: SparkSession, path: str, schema: StructType) -> DataFrame:
    print("Loading data...")
    data_raw = spark.read.option("header", True).schema(schema).csv(str(path))
    print(f"Loaded {path}: {data_raw.count()} records")
    return data_raw

def clean_data(df_raw: DataFrame, entity_name: str, mandatory_columns: list, filters=None) -> DataFrame:
    null_filter = col(mandatory_columns[0]).isNull()
    for c in mandatory_columns[1:]:
        null_filter |= col(c).isNull()

    bad_conditions = null_filter
    if filters is not None:
        bad_conditions |= (~filters)

    bad_df = df_raw.filter(bad_conditions)
    bad_count = bad_df.count()

    clean_df = df_raw.dropna(subset=mandatory_columns)
    if filters is not None:
        clean_df = clean_df.filter(filters)

    print(f"--- {entity_name} Quality Control ---")
    print(f"Invalid records: {bad_count}")
    print(f"Valid records: {clean_df.count()}")
    print("-" * 30)

    return clean_df

def create_analytics_table(users_df: DataFrame, content_df: DataFrame, views_df: DataFrame) -> DataFrame:
    print("Creating analytics table...")
    analytics_df = (
        views_df.alias("v")
        .join(users_df.alias("u"), col("v.user_id") == col("u.user_id"), "inner")
        .join(content_df.alias("c"), col("v.content_id") == col("c.content_id"), "inner")
        .select(
            col("v.view_id"),
            col("v.view_date"),
            col("v.view_hour"),
            col("u.user_id"),
            col("u.user_name"),
            col("u.country"),
            col("u.subscription_type"),
            col("c.content_id"),
            col("c.title"),
            col("c.content_type"),
            col("c.genre"),
            col("c.duration_minutes"),
            col("c.release_year"),
            col("v.view_hours"),
            col("v.watch_percentage"),
            col("v.rating"),
        )
        .withColumn("year_num", year("view_date"))
        .withColumn("month_num", month("view_date"))
        .withColumn("week_num", weekofyear("view_date"))
        .withColumn("quarter_num", quarter("view_date"))
        .withColumn("day_of_week", dayofweek("view_date"))
        .withColumn("time_slot", 
            when((col("view_hour") >= 18) & (col("view_hour") <= 23), "Prime Time")
            .when((col("view_hour") >= 12) & (col("view_hour") <= 17), "Afternoon")
            .when((col("view_hour") >= 6) & (col("view_hour") <= 11), "Morning")
            .otherwise("Night")
        )
        .withColumn("is_weekend",
            when(col("day_of_week").isin([1, 7]), "Weekend")
            .otherwise("Weekday")
        )
    )

    count = analytics_df.count()
    print(f"Analytics table created: {count} records")
    
    print("\n--- Sample ---")
    analytics_df.select(
        "view_id", "country", "genre", "view_hours", "time_slot", "is_weekend"
    ).show(10, truncate=False)

    return analytics_df

def get_country_analytics(df: DataFrame) -> DataFrame:
    print("\n--- Aggregation: Countries ---")
    
    result = (
        df.groupBy("country")
        .agg(
            count("view_id").alias("views_count"),
            spark_round(spark_sum("view_hours"), 2).alias("total_hours"),
            spark_round(avg("watch_percentage"), 2).alias("avg_completion_rate"),
            count(when(col("rating").isNotNull(), 1)).alias("ratings_count"),
            spark_round(avg("rating"), 2).alias("avg_rating"),
        )
        .orderBy(col("total_hours").desc())
    )
    
    print("\n--- Sample ---")
    result.show(5, truncate=False)
    return result

def get_genre_monthly_analytics(df: DataFrame) -> DataFrame:
    print("\n--- Aggregation: Monthly Genres ---")
    
    result = (
        df.groupBy("year_num", "month_num", "genre")
        .agg(
            count("view_id").alias("views_count"),
            spark_round(spark_sum("view_hours"), 2).alias("total_hours"),
            count("user_id").alias("unique_users"),
        )
        .orderBy("year_num", "month_num", col("total_hours").desc())
    )
    
    print("\n--- Sample ---")
    result.show(10, truncate=False)
    return result

def get_content_type_comparison(df: DataFrame) -> DataFrame:
    print("\n--- Aggregation: Content Types ---")
    
    result = (
        df.groupBy("content_type")
        .agg(
            count("view_id").alias("views_count"),
            spark_round(spark_sum("view_hours"), 2).alias("total_hours"),
            spark_round(avg("watch_percentage"), 2).alias("avg_completion_rate"),
            count("content_id").alias("unique_content"),
        )
        .orderBy(col("total_hours").desc())
    )
    
    print("\n--- Sample ---")
    result.show(truncate=False)
    return result

def get_quarterly_genre_stats(df: DataFrame, start_date: str, end_date: str) -> DataFrame:
    print(f"\n--- Quarterly Genre Stats {start_date} - {end_date} ---")
    
    result = (
        df.filter((col("view_date") >= lit(start_date)) & (col("view_date") <= lit(end_date)))
        .groupBy("genre")
        .agg(
            count("view_id").alias("views_count"),
            spark_round(spark_sum("view_hours"), 2).alias("total_hours_period"),
            spark_round(avg("rating"), 2).alias("avg_rating"),
        )
        .orderBy(col("total_hours_period").desc())
    )
    
    print("\n--- Sample ---")
    result.show(truncate=False)
    return result

def get_weekend_stats(df: DataFrame) -> DataFrame:
    print("\n--- Weekend Stats ---")
    
    result = (
        df.filter(col("is_weekend") == "Weekend")
        .groupBy("country", "content_type")
        .agg(
            count("view_id").alias("weekend_views"),
            spark_round(spark_sum("view_hours"), 2).alias("weekend_hours"),
        )
        .orderBy(col("weekend_hours").desc())
    )
    
    print("\n--- Sample ---")
    result.show(10, truncate=False)
    return result

def get_primetime_stats(df: DataFrame) -> DataFrame:
    print("\n--- Prime Time Stats ---")
    
    result = (
        df.filter(col("time_slot") == "Prime Time")
        .groupBy("country", "genre")
        .agg(
            count("view_id").alias("primetime_views"),
            spark_round(spark_sum("view_hours"), 2).alias("primetime_hours"),
        )
        .orderBy(col("primetime_hours").desc())
    )
    
    print("\n--- Sample ---")
    result.show(10, truncate=False)
    return result

def get_weekly_trends(df: DataFrame, start_date: str, end_date: str) -> DataFrame:
    print(f"\n--- Weekly Trends ({start_date} - {end_date}) ---")
    
    result = (
        df.filter((col("view_date") >= lit(start_date)) & (col("view_date") <= lit(end_date)))
        .groupBy("year_num", "week_num", "country")
        .agg(
            count("view_id").alias("weekly_views"),
            spark_round(spark_sum("view_hours"), 2).alias("weekly_hours"),
        )
        .orderBy("year_num", "week_num", col("weekly_hours").desc())
    )
    
    print("\n--- Sample ---")
    result.show(15, truncate=False)
    return result

def save_parquet(df: DataFrame, path: str, partition_by: list[str] = []) -> None:
    df.write.mode("overwrite").partitionBy(*partition_by).parquet(path)

def main():
    with create_spark_session() as spark:
        users_raw = load_csv(spark, USERS_CSV, users_schema)
        content_raw = load_csv(spark, CONTENT_CSV, content_schema)
        views_raw = load_csv(spark, VIEWS_CSV, views_schema)

        users_prep = users_raw.withColumn("registration_date", to_date("registration_date", "yyyy-MM-dd"))
        users_clean = clean_data(
            users_prep, 
            "Users", 
            mandatory_columns=["user_id", "country"]
        )

        content_prep = content_raw.withColumn("release_year", col("release_year").cast("int"))
        content_filters = ((col("release_year") > 1888) & (col("duration_minutes") > 0))    
        content_clean = clean_data(
            content_prep,
            "Content",
            mandatory_columns=["content_id", "title"],
            filters=content_filters
        )

        views_prep = (
            views_raw
            .withColumn("view_date", to_date("view_date", "yyyy-MM-dd"))
            .withColumn("view_hour", col("view_hour").cast("int"))
            .withColumn("view_hours", col("view_hours").cast("double"))
            .withColumn("watch_percentage", col("watch_percentage").cast("double"))
            .withColumn("rating", col("rating").cast("double"))
        )
        views_filters = (
            (col("view_hours") > 0) & 
            (col("watch_percentage") >= 0) & 
            (col("watch_percentage") <= 100)
        )
        views_clean = clean_data(
        views_prep,
        "Views",
        mandatory_columns=["view_id", "user_id", "content_id", "view_date"],
        filters=views_filters
    )

        analytics_table = create_analytics_table(users_clean, content_clean, views_clean)
        country_stats = get_country_analytics(analytics_table)
        genre_stats   = get_genre_monthly_analytics(analytics_table)
        content_stats = get_content_type_comparison(analytics_table)

        q4_genres    = get_quarterly_genre_stats(analytics_table, "2024-10-01", "2024-12-31")
        weekend_data = get_weekend_stats(analytics_table)
        primetime    = get_primetime_stats(analytics_table)
        weekly_trend = get_weekly_trends(analytics_table, "2024-11-01", "2024-12-31")

        print("Saving analytics table partitioned by year and month...")
        save_parquet(analytics_table, f"{PATH}/warehouse/analytics_parquet", ["year_num", "month_num"])
        print("Saving aggregation tables...")
        save_parquet(country_stats, f"{PATH}/warehouse/country_stats_parquet")
        save_parquet(genre_stats, f"{PATH}/warehouse/genre_stats_parquet", ["year_num", "month_num"])
        save_parquet(content_stats, f"{PATH}/warehouse/content_stats_parquet")
        print("Saving slices...")
        save_parquet(q4_genres, f"{PATH}/warehouse/slice_q4_genres_parquet")
        save_parquet(weekend_data, f"{PATH}/warehouse/slice_weekend_parquet", ["country"])
        save_parquet(primetime, f"{PATH}/warehouse/slice_primetime_parquet", ["country"])
        save_parquet(weekly_trend, f"{PATH}/warehouse/slice_weekly_parquet", ["year_num", "week_num"])

if __name__ == "__main__":
    main()
