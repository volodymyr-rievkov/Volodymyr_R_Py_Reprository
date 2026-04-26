## Quick start

### 1. Start
```bash
docker-compose up -d
```

### 2. Configuring Variables and Connections

```bash
docker exec -it ads-airflow-scheduler-1 bash /opt/airflow/setup_airflow.sh
```

## Check db

```bash
docker exec -it ads-postgres-1 psql -U airflow -d airflow
```
