from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract_weather_data():
    import sys
    sys.path.insert(0, "/opt/airflow/project")
    from src.ingestion.weather_api import main
    main()


def combine_weather_data():
    import sys
    sys.path.insert(0, "/opt/airflow/project")
    from src.transformation.combine_data import main
    main()


def clean_weather_data():
    import subprocess
    subprocess.run(
        ["python", "/opt/airflow/project/src/transformation/clean_data.py"],
        check=True,
    )


def validate_weather_data():
    import subprocess
    subprocess.run(
        ["python", "/opt/airflow/project/src/validation/validate_data.py"],
        check=True,
    )


def run_dbt():
    import subprocess
    subprocess.run(
        [
            "dbt",
            "build",
            "--project-dir",
            "/opt/airflow/project/dbt/weather_air_quality",
            "--profiles-dir",
            "/home/airflow/.dbt",
        ],
        check=True,
    )


with DAG(
    dag_id="weather_air_quality_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    tags=["weather", "air-quality"],
) as dag:

    extract_weather = PythonOperator(
        task_id="extract_weather_data",
        python_callable=extract_weather_data,
    )

    combine_data = PythonOperator(
        task_id="combine_data",
        python_callable=combine_weather_data,
    )

    clean_data = PythonOperator(
        task_id="clean_data",
        python_callable=clean_weather_data,
    )

    validate_data = PythonOperator(
        task_id="validate_data",
        python_callable=validate_weather_data,
    )

    dbt_build = PythonOperator(
        task_id="dbt_build",
        python_callable=run_dbt,
    )

    extract_weather >> combine_data >> clean_data >> validate_data >> dbt_build