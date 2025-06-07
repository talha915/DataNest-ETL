from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'description': "A DAG to Orchestrate data",
    'start_date': datetime(2025, 6, 7),
    'catchup': False
}

def print_hello():
    print("Hello from PythonOperator!")

dag = DAG(
    dag_id = "weather-api-orchestrator",
    default_args = default_args,
    schedule = timedelta(minutes=1)
)

with dag:
    python_task = PythonOperator(
        task_id='print_hello_task',
        python_callable=print_hello
    )