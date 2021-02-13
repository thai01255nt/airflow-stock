from datetime import timedelta

import json
import os
import requests
import time
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.db import create_session
from airflow.utils.trigger_rule import TriggerRule

MAX_RETRIES = 5


def get_system_config(env_path):
    with open(env_path) as json_data_file:
        data = json.load(json_data_file)
    return data


def get_default_args():
    default_args = {
        'owner': "airflow",
        'depends_on_past': False,
        'start_date': days_ago(1),
        'email': ['vmo@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
        'retry_delay': timedelta(seconds=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'dag': dag,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function,
        # 'on_success_callback': some_other_function,
        # 'on_retry_callback': another_function,
        # 'sla_miss_callback': yet_another_function,
        # 'trigger_rule': 'all_success'
    }
    return default_args


def api_task(api, method):
    method = method.lower()
    if method == "get":
        response = requests.get(api)
    elif method == "post":
        response = requests.post(api)
    elif method == "patch":
        response = requests.patch(api)
    else:
        raise Exception("method {} is not supported for api task".format(method))
    if int(int(response.status_code) / 100) != 2:
        raise Exception(response.content)
    print(response.content.decode('ascii'))
    return


def branch_decision(api, method, success_branch: str, fail_branch: str):
    try:
        api_task(api, method)
        return success_branch
    except Exception as e:
        print("Error with message: ", str(e))
        return fail_branch


def log(e: Exception):
    print("Dump error: " + str(e))  # log error before retry
    time.sleep(60)


def ping_request(url):  # need ping
    try:
        re = requests.get(url)
        if re.status_code == 404:
            raise Exception(f'{url} not found !')
    except Exception as e:
        log(e)
        raise e
    return


def create_transfer_dag(dag_config):
    # Extract dag config
    dag_id = dag_config["dag_id"]
    description = "This is a dynamic dag"
    if "description" in dag_config.keys():
        description = dag_config["description"]

    schedule_interval = dag_config["schedule_interval"]

    # Create dag
    dag = DAG(
        dag_id=dag_id,
        default_args=get_default_args(),
        description=f'''Tranfer dag: {description}''',
        schedule_interval=schedule_interval,
        catchup=False
    )

    prefix = dag_config["prefix"]

    update_newest = PythonOperator(
        task_id="update-newest",
        python_callable=api_task,
        op_kwargs={'api': os.path.join(prefix, 'histories-resolution-d/update-newest'), "method": "PATCH"},
        dag=dag,
        retries=MAX_RETRIES,
        retry_delay=timedelta(seconds=5),
    )

    return dag


# a db.Session object is used to run queries against
# the create_session() method will create (yield) a session
with create_session() as session:
    # By calling .query() with Variable, we are asking the airflow db
    # session to return all variables (select * from variables).
    # The result of this is an iterable item similar to a dict but with a
    # slightly different signature (object.key, object.val).
    airflow_vars = {}
    for var in session.query(Variable):
        if isinstance(var.val, str):
            airflow_vars[var.key] = eval(var.val)
        else:
            airflow_vars[var.key] = var.val

for key in airflow_vars.keys():
    dag_config = airflow_vars[key]
    dag_config["dag_id"] = key
    if dag_config["dag_type"] == "auto-update-history-resolution-d-vn":
        globals()[dag_config["dag_id"]] = create_transfer_dag(dag_config)
