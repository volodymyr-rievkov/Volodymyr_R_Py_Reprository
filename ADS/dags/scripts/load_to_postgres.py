import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datasets import ds_location, ds_time, ds_fact
from config import CONN_POSTGRES, TableNames


def load_dimension_location_task(**context):
    print("Start load_dimension_location")
    df = pd.read_json(ds_location.uri)
    df.columns = [col.lower() for col in df.columns]
    
    pg_hook = PostgresHook(postgres_conn_id=CONN_POSTGRES)
    pg_hook.run(f"TRUNCATE TABLE {TableNames.dim_location} CASCADE")
    engine = pg_hook.get_sqlalchemy_engine()
    
    df.to_sql(TableNames.dim_location, con=engine, if_exists='append', index=False)
    print(f"Finish load_dimension_location. Loaded {len(df)} countries")


def load_dimension_time_task(**context):
    print("Start load_dimension_time")
    df = pd.read_json(ds_time.uri)
    df.columns = [col.lower() for col in df.columns]
    
    pg_hook = PostgresHook(postgres_conn_id=CONN_POSTGRES)
    pg_hook.run(f"TRUNCATE TABLE {TableNames.dim_time} CASCADE")
    engine = pg_hook.get_sqlalchemy_engine()
    
    df.to_sql(TableNames.dim_time, con=engine, if_exists='append', index=False)
    print(f"Finish load_dimension_time. Loaded {len(df)} years")


def load_fact_demographics_task(**context):
    print("Start load_fact_demographics")
    df = pd.read_json(ds_fact.uri)
    df.columns = [col.lower() for col in df.columns]
    
    pg_hook = PostgresHook(postgres_conn_id=CONN_POSTGRES)
    pg_hook.run(f"TRUNCATE TABLE {TableNames.fact_demographics} CASCADE")
    engine = pg_hook.get_sqlalchemy_engine()
    
    df.to_sql(TableNames.fact_demographics, con=engine, if_exists='append', index=False)
    print(f"Finish load_fact_demographics. Loaded {len(df)} facts")


def validate_data_task(**context):
    print("Start validate_data")
    pg_hook = PostgresHook(postgres_conn_id=CONN_POSTGRES)
    
    for table in TableNames.list_names():
        count = pg_hook.get_first(f"SELECT COUNT(*) FROM {table}")[0]
        print(f"{table}: {count} records")
        if count == 0:
            raise ValueError(f"Table {table} is empty!")
    
    null_count = pg_hook.get_first(
        f"SELECT COUNT(*) FROM {TableNames.fact_demographics} WHERE country_key IS NULL OR time_key IS NULL"
    )[0]
    if null_count > 0:
        raise ValueError(f"For {null_count} records country_key or time_key is NULL!")
    
    print("Finish validate_data")
