#!/bin/bash
export AIRFLOW_HOME=pwd
airflow db init
cp -r dags pwd
airflow users create \
    --username admin \
    -p admin \
    --firstname Thai \
    --lastname Dao \
    --role Admin \
    --email thai0125nt@gmail.com