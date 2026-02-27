from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models import Variable
import pendulum

from config import CONN_RAW_DATA, VAR_RAW_DATA, DemographicSheets
from scripts.transform_logic import transform_location_data, transform_time_data, build_fact_table
from datasets import ds_location, ds_time, ds_fact

with DAG(
    dag_id="load_demographics_datasets",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1),
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
        python_callable=transform_location_data,
        op_kwargs={
        'sheet': DemographicSheets.countries_meta,
        },
        outlets=[ds_location],
        dag=dag
        )
    
    load_and_transform_time_data = PythonOperator(
        task_id="load_and_transform_time_data",
        python_callable=transform_time_data,
        op_kwargs={
        'sheet': DemographicSheets.countries_population,
        },
        outlets=[ds_time],
        dag=dag
        )
    
    build_fact_table = PythonOperator(
        task_id="build_fact_table",
        python_callable=build_fact_table,
        op_kwargs={
            'sheets': [DemographicSheets.countries_population, DemographicSheets.life_expectancy, DemographicSheets.fertility_rate],
        },
        outlets=[ds_fact],
        dag=dag
        )


is_raw_data_file_exists >> [load_and_transform_location_data, load_and_transform_time_data] >> build_fact_table