import os
import json
from airflow import Dataset
from airflow.hooks.base import BaseHook

from config import CONN_PROCESSED_DATA, OuputJsonFiles

data_path = json.loads(BaseHook.get_connection(CONN_PROCESSED_DATA).extra)['path']

location_cols = ['Country_Name', 'Country_Code', 'Region', 'Income_Group', 'Special_Notes']
time_cols = ['Year']
fact_cols = ['Country_Key', 'Time_Key', 'Country_Population', 'Fertility_Rate', 'Life_Expectancy']

ds_location = Dataset(uri=os.path.join(data_path, OuputJsonFiles.dim_location), extra={'columns': location_cols})
ds_time = Dataset(uri=os.path.join(data_path, OuputJsonFiles.dim_time), extra={'columns': time_cols})
ds_fact = Dataset(uri=os.path.join(data_path, OuputJsonFiles.fact_demographics), extra={'columns': fact_cols})