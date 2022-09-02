import os
import logging
import typing
import datetime
import pendulum

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context, Context
from gharchive import GHArchive
from core.dag_default_args import get_default_arguments
from core.tags import Tag
from datetime import timedelta


doc_md = """
### This DAG imports daily data from GitHub archive using GHArchive library.
It has catchup option **enabled**, so historical data can be imported (start_date needs to be adjusted).
The project adheres to ELT paradigm, so no transformations occur inside the DAG.
### This logic can be used with rather small or medium-sized data only.
To work with larger sets of data, there are few steps to take:
1) Use generators and yield data instead of saving everything into RAM (the whole list of data). However,
in this case GHArchive does not have a generator functionality.
2) Avoid using XCom and passing data between tasks. Instead, save data to the FS (filesystem) and
read it in other tasks using a given path to file.
3) And, of course, scale Airflow (add more workers) and/or use clustered Airflow in Kubernetes
"""

# path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")


def fetch_data(context: Context) -> typing.List:
    gh = GHArchive()

    date_start: pendulum.DateTime = context['data_interval_start']
    date_start_formatted: str = date_start.strftime('%m/%d/%Y')

    logging.info(f"Getting the data from {date_start} to {date_start}.")

    data = gh.get(date_start_formatted, date_start_formatted)  # extracting for single day
    daily_events: typing.List = data.to_dict_list()

    return daily_events


default_args = get_default_arguments(
    retry_delay=timedelta(minutes=1)
)


@dag(
    dag_id='github-archive-daily-import',
    doc_md=doc_md,
    description='Imports data from GitHub archive daily at 00:00 UTC',
    schedule_interval='@daily',
    start_date=datetime.datetime(2022, 9, 1),
    default_args=default_args,
    catchup=True,
    tags=[Tag.daily, Tag.github, Tag.with_catchup]
)
def create_dag():
    @task(task_id='fetch_github_data')
    def fetch_data_task():
        context = get_current_context()
        return fetch_data(context)

    @task(task_id='export_data_into_db')
    def export_data_task(data):
        return

    # Using XCom here, however with 'big' data might need to save data to the filesystem and read from there
    fetched_data = fetch_data_task()
    export_data_task(fetched_data)


created_dag = create_dag()


def main():
    """Main function for local script testing. Set LOCAL_DEBUG=1 option in run config for that to work."""
    gh = GHArchive()
    data = gh.get('6/8/2020', '6/8/2020')
    daily_events = data.to_dict_list()

    devs_with_more_than_one_commit = set()
    devs_with_less_than_one_commit = set()


if __name__ == '__main__':
    if os.environ.get('LOCAL_DEBUG'):
        exit(main())
