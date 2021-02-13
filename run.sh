#!/bin/bash
export AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW__CORE__CATCHUP_BY_DEFAULT=false
#export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
airflow webserver --port 8080 &
airflow scheduler &
wait