import pandas as pd
import os
import json
from airflow.models import Variable
from airflow.hooks.base import BaseHook
from config import CONN_RAW_DATA, VAR_RAW_DATA
from datasets import ds_location, ds_time, ds_fact


def get_file_path():
    conn = BaseHook.get_connection(CONN_RAW_DATA)
    base_path = json.loads(conn.extra)['path']
    file_name = Variable.get(VAR_RAW_DATA)
    return os.path.join(base_path, file_name)


def transform_location_data(sheet, **context):
    path = get_file_path()
    df = pd.read_excel(path, sheet_name=sheet['name'])
    
    dim_location = df[sheet['columns']].drop_duplicates()
    
    dim_location.columns = ds_location.extra['columns']
    
    dim_location.insert(0, 'Country_Key', range(1, len(dim_location) + 1))
    
    dim_location.to_json(ds_location.uri, orient='records', indent=4)


def transform_time_data(sheet, **context):
    path = get_file_path()
    df = pd.read_excel(path, sheet_name=sheet['name'])
    
    years = [col for col in df.columns if str(col).isdigit()]
    
    dim_time = pd.DataFrame({'Year': years})
    dim_time['Year'] = dim_time['Year'].astype(int)
    dim_time = dim_time.drop_duplicates().sort_values('Year')
    
    dim_time.columns = ds_time.extra['columns']
    dim_time.insert(0, 'Time_Key', range(1, len(dim_time) + 1))
    
    dim_time.to_json(ds_time.uri, orient='records', indent=4)


def build_fact_table(sheets, **context):
    path = get_file_path()
    
    dim_l = pd.read_json(ds_location.uri)
    dim_t = pd.read_json(ds_time.uri)
    
    all_metrics = []

    for sheet in sheets:
        df = pd.read_excel(path, sheet_name=sheet['name'])
        
        id_vars = ['Country Code']
        year_cols = [col for col in df.columns if str(col).isdigit()]
        
        df_long = df.melt(id_vars=id_vars, value_vars=year_cols, 
                          var_name='Year', value_name=sheet['name'])
        df_long['Year'] = df_long['Year'].astype(int)
        all_metrics.append(df_long)

    fact_df = all_metrics[0]
    for next_df in all_metrics[1:]:
        fact_df = fact_df.merge(next_df, on=['Country Code', 'Year'], how='outer')

    fact_df = fact_df.merge(dim_l[['Country_Key', 'Country_Code']], left_on='Country Code', right_on='Country_Code')
    fact_df = fact_df.merge(dim_t[['Time_Key', 'Year']], on='Year')

    value_cols_names = [sheet['name'] for sheet in sheets] # sheet names which were assigned to columns
    value_cols_rename = ds_fact.extra['columns'][2:] # without country_key and time_key

    fact_df = fact_df.rename(columns=dict(zip(value_cols_names, value_cols_rename))) # rename columns
    
    final_fact = fact_df[ds_fact.extra['columns']]
    final_fact.insert(0, 'Fact_Key', range(1, len(final_fact) + 1))

    final_fact.to_json(ds_fact.uri, orient='records', indent=4)
