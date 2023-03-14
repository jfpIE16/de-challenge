"""
NAME
    door2door ETL pipeline

DESCRIPTION
    This dag is intended to execute and ETL pipeline
    for the door2door data engineering challenge.

FUNCTIONS
    _extract(ds)
        Download all the json files for an specific date from 
        a public s3 bucket.
    
    _transform(ds)
        Read each json file for an specific date and transform all
        the entries in each file (dict like entries) into a readable
        comma separated line that is appended to a csv file.

    _load(ds)
        Read the output CSV file for an specific date and create a
        INSERT INTO VALUES () statement to insert the data into the
        data warehouse.

    _get_update_location_data(line: dict)
        Receives a dictionary object and returns a comma separated
        line string with only the filtered rows needed.
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
    """
    Helper function to extract vehicle location update from dictionary.
    Input: dict -> 
        {
        "event": "update",
        "on": "vehicle",
        "at": "2019-06-01T18:17:12.105Z",
        "data": {
            "id": "bac5188f-67c6-4965-81dc-4ef49622e280",
            "location": {
                "lat": 52.45176,
                "lng": 13.45989,
                "at": "2019-06-01T18:17:12.105Z"
            }
        },
        "organization_id": "org-id"
        }
    Output:
        Comma separated string
        bac5188f-67c6-4965-81dc-4ef49622e280,52.4517613.45989,"2019-06-01T18:17:12.105Z"
    """
    return f"""{line['data']['id']},\
            {line['data']['location']['lat']},\
            {line['data']['location']['lng']},\
            {line['data']['location']['at']}\n"""


def _extract(ds):
    """
    Function to get the data from S3 bucket and download it to a temporary folder.
    """
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
    """
    Function to read file by file in a line level and get an CSV output file with the filtered
    events: 
    Filtered event -> update, vehicle
    """
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
    """
    Function to load the data into PostgreSQL.
    Input: Search for an specific date output file in /temp/csv/ folder.
    Output: Execute INSERT INTO tablename VALUES () for each line of the CSV file.
    """
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
