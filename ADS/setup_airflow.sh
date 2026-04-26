#!/bin/bash
echo "🔧 Configuring Airflow Variables and Connections..."

# Variable
echo "Adding  Variable: raw_data_name"
airflow variables set raw_data_name "Population_fertility_rate_Life_expectancy.xls"

# Connections
echo "Adding Connection: raw_data_path"
airflow connections add 'raw_data_path' \
    --conn-type 'file' \
    --conn-extra '{"path": "/opt/airflow/dags/data/raw"}' \
    2>/dev/null || echo "Already exists"

echo "Adding Connection: processed_data_path"
airflow connections add 'processed_data_path' \
    --conn-type 'file' \
    --conn-extra '{"path": "/opt/airflow/dags/data/processed"}' \
    2>/dev/null || echo "Already exists"

echo "Adding Connection: postgres_default"
airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema 'airflow' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-port 5432 \
    2>/dev/null || echo "Already exists"

echo "✅ Done!"
echo ""
echo "Checking:"
airflow variables list
echo ""
airflow connections list | grep -E "(raw_data_path|processed_data_path|postgres_default)"
