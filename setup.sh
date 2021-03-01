#!/bin/bash
pip install -r requirements.txt
export AIRFLOW_HOME=pwd
airflow db init
airflow users create \
        --username admin \
        -p admin \
        --firstname thai \
        --lastname dao \
        --role Admin \
        --email thai0125nt@gmail.com