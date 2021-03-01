#!/bin/bash
export AIRFLOW_HOME=pwd
export AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW__CORE__CATCHUP_BY_DEFAULT=false
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=5000
#export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
airflow webserver &
airflow scheduler &
wait