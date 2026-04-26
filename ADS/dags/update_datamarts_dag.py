from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.external_task import ExternalTaskSensor
import pendulum
from datasets import ds_warehouse_ready
from config import CONN_POSTGRES, Queries

with DAG(
    dag_id="update_datamarts",
    schedule=[ds_warehouse_ready],
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
) as dag:

    build_regional_mart = PostgresOperator(
        task_id='build_regional_demographics_mart',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.datamart_regional,
    )

    build_income_mart = PostgresOperator(
        task_id='build_income_groups_mart',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.datamart_income,
    )

    build_trends_mart = PostgresOperator(
        task_id='build_yearly_trends_mart',
        postgres_conn_id=CONN_POSTGRES,
        sql=Queries.datamart_trends,
    )

    [build_regional_mart, build_income_mart, build_trends_mart]