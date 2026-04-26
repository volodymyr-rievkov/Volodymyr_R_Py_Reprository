from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models import Variable
import pendulum

from config import CONN_RAW_DATA, VAR_RAW_DATA
from scripts.transform_to_json import transform_location_data_task, transform_time_data_task, build_fact_table_task
from datasets import ds_location, ds_time, ds_fact

with DAG(
    dag_id="transform_to_json",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
) as dag:
 
    is_raw_data_file_exists = FileSensor(
        task_id='is_raw_data_file_exists',
        filepath=Variable.get(VAR_RAW_DATA),
        fs_conn_id=CONN_RAW_DATA,
        poke_interval=3,
        timeout=9,
        dag=dag
    )

    load_and_transform_location_data = PythonOperator(
        task_id="load_and_transform_location_data",
        python_callable=transform_location_data_task,
        outlets=[ds_location],
        dag=dag
        )
    
    load_and_transform_time_data = PythonOperator(
        task_id="load_and_transform_time_data",
        python_callable=transform_time_data_task,
        outlets=[ds_time],
        dag=dag
        )
    
    load_and_build_fact_table = PythonOperator(
        task_id="load_and_build_fact_table",
        python_callable=build_fact_table_task,
        outlets=[ds_fact],
        dag=dag
        )


is_raw_data_file_exists >> [load_and_transform_location_data, load_and_transform_time_data] >> load_and_build_fact_table