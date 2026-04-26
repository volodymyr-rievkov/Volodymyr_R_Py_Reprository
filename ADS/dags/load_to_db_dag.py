from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import pendulum

from datasets import ds_location, ds_time, ds_fact, ds_warehouse_ready
from config import CONN_POSTGRES, Queries
from scripts.load_to_postgres import (
    load_dimension_location_task,
    load_dimension_time_task,
    load_fact_demographics_task,
    validate_data_task
)

with DAG(
    dag_id="load_to_db",
    schedule=[ds_location, ds_time, ds_fact],
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
) as dag:

    create_tables = PostgresOperator(
        task_id='create_tables_in_db',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.create_tables,
    )

    load_location = PythonOperator(
        task_id='load_location_to_db',
        python_callable=load_dimension_location_task,
    )

    load_time = PythonOperator(
        task_id='load_time_to_db',
        python_callable=load_dimension_time_task,
    )

    load_facts = PythonOperator(
        task_id='load_facts_to_db',
        python_callable=load_fact_demographics_task,
    )

    validate = PythonOperator(
        task_id='validate_data_in_db',
        python_callable=validate_data_task,
    )

    aggregate_region = PostgresOperator(
        task_id='aggregate_region',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.aggregate_region,
    )

    aggregate_income = PostgresOperator(
        task_id='aggregate_income',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.aggregate_income,
    )

    aggregate_trends = PostgresOperator(
        task_id='aggregate_trends',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.aggregate_trends,
    )

    warehouse_ready = EmptyOperator(
        task_id='warehouse_ready',
        outlets=[ds_warehouse_ready],
    )

    create_tables >> [load_location, load_time] >> load_facts >> validate >> [aggregate_region, aggregate_income, aggregate_trends] >> warehouse_ready
    