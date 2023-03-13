# Data engineer challenge
## Infrastructure
For this challenge I decide to use a hybrid infrastructure design, using AWS S3 as Data Lake and using docker to create the infrastructure needed for data processing and data warehousing solutions. Also I have created IAC in case the migration to the cloud is needed, using one or more EC2 instances the solution is designed to host airflow and Postgres in the cloud.
![Infrastructure](images/DE-challenge.png)

## ETL
For the ETL design I followed a functional design under this 3 principles:
1. Atomicity: *One* function should only perform *one* Task.
2. Idempotency: If you run your code multiple times, the output should be the same.
3. No side effects: Your function shouldn't affect any external data (variable or other) besides its output.

So let's break the door2door-etl DAG: