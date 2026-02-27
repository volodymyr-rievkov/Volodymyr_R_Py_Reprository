from dataclasses import dataclass


# Airflow connections
CONN_RAW_DATA = "raw_data_path"
CONN_PROCESSED_DATA = "processed_data_path"


# Airflow variables
VAR_RAW_DATA = "raw_data_name"


# Raw data excel sheets
class DemographicSheets:
    countries_meta: dict = {
        'name': 'Metadata - Countries', 
        'columns': ['Country Name', 'Country Code', 'Region', 'IncomeGroup', 'SpecialNotes']
    }
    countries_population: dict = {
        'name': 'Country population',
        'columns': ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'] # Next columns - years(1960-2013)
    }
    life_expectancy: dict = {
        'name': 'Life-Expectancy-At-Birth',
        'columns': ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'] # Next columns - years(1960-2013)
    }
    fertility_rate: dict = {
        'name': 'Fertility-Rate',
        'columns': ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'] # Next columns - years(1960-2013)
    }


@dataclass(frozen=True)
class OuputJsonFiles:
    dim_location: str = 'dim_location.json'
    dim_time: str = 'dim_time.json'
    fact_demographics: str = 'fact_demographics.json'
