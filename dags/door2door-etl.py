"""
door2door ETL pipeline
"""
import os

import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator

S3_BUCKET = os.environ['BUCKET_NAME']
WAREHOUSE_USER = os.environ['WAREHOUSE_USER']
WAREHOUSE_PASSWORD = os.environ['WAREHOUSE_PASSWORD']
WAREHOUSE_DB = os.environ['WAREHOUSE_DB']
WAREHOUSE_HOST = os.environ['WAREHOUSE_HOST']
WAREHOUSE_PORT = os.environ['WAREHOUSE_PORT']


def _get_update_location_data(line: dict):
    return f"""{line['data']['id']},\
            {line['data']['location']['lat']},\
            {line['data']['location']['lng']},\
            {line['data']['location']['at']}\n"""


def _extract(ds):
    import s3fs

    fs = s3fs.S3FileSystem(anon=True)
    file_list = fs.ls(S3_BUCKET)
    for i in file_list:
        name = i.split("/")[2]
        if ds in i:
            fs3 = fs.open(i, 'r')
            with open(f"temp/{name}", 'w') as f:
                f.write(fs3.read())


def _transform(ds):
    import json

    _csvFile = open(f"temp/csv/output_{ds}.csv", "w")
    json_filter = [f for f in os.listdir("temp/") if f.endswith(".json")]
    for filename in json_filter:
        f = open(os.path.join("temp/", filename), 'r')
        data = f.readlines()
        for line in data:
            res = json.loads(line)
            if res["event"] == "update" and res["on"] == "vehicle":
                _csvFile.write(_get_update_location_data(res))


def _load(ds):
    import csv

    import psycopg2

    try:
        conn = psycopg2.connect(
            database=WAREHOUSE_DB,
            user=WAREHOUSE_USER,
            password=WAREHOUSE_PASSWORD,
            host=WAREHOUSE_HOST,
            port=WAREHOUSE_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()
        with open(f'temp/csv/output_{ds}.csv', 'r') as f:
            reader = csv.reader(f, skipinitialspace=True)
            for row in reader:
                cursor.execute(
                    "INSERT INTO vehicle.locationupdate \
                        VALUES(%s, %s, %s, %s)",
                    row,
                )
        conn.commit()
    except Exception as err:
        print(f"Error with the connection to Warehouse, {err}")
    finally:
        conn.close()


def _print_execution_date(ds):
    pass


with DAG(
    'door2door-etl',
    catchup=True,
    start_date=pendulum.datetime(2019, 6, 1),
    end_date=pendulum.datetime(2019, 6, 1),
) as dag:
    extract = PythonOperator(
        task_id='extract', python_callable=_extract, dag=dag
    )

    transform = PythonOperator(
        task_id='transform', python_callable=_transform, dag=dag
    )

    load = PythonOperator(task_id='load', python_callable=_load, dag=dag)

extract >> transform >> load
