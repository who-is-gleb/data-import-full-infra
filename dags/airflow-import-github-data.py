import os
import logging
import datetime
import pendulum

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context, Context
from gharchive import GHArchive
from core.dag_default_args import get_default_arguments
from core.clickhouse import ClickhouseLocalhost
from models.tags import Tag
from models.github_event import GithubEvent
from datetime import timedelta
from typing import List, Dict


doc_md = """
### This DAG imports daily data from GitHub archive using GHArchive library.
It has catchup option **enabled**, so historical data can be imported (start_date needs to be adjusted).
The project adheres to the ETL paradigm, so data is transformed here before inserted into the DB. Reason is because
we don't need all of the raw data for the analytics.
### This logic can be used with rather small or medium-sized data only.
To work with larger sets of data, there are few steps to take:
1) Use generators and yield data instead of saving everything into RAM (the whole list of data). However,
in this case GHArchive does not have a generator functionality.
2) Avoid using XCom and passing data between tasks. Instead, save data to the FS (filesystem) and
read it in other tasks using a given path to file.
3) And, of course, scale Airflow (add more workers) and/or use clustered Airflow in Kubernetes
"""


GITHUB_EVENT_TABLE_INFO = {
    'table_name': 'archive_events',
    'db_name': 'github_data',
    'partition_by': 'created_at',
    'order_by': 'id'
}


def fetch_data(context: Context) -> List[Dict]:
    gh = GHArchive()

    date_start: pendulum.DateTime = context['data_interval_start']
    date_start_formatted: str = date_start.strftime('%m/%d/%Y')

    logging.info(f"Getting the data from {date_start} to {date_start}.")

    data = gh.get(date_start_formatted, date_start_formatted)  # extracting for single day
    daily_events: List = data.to_dict_list()
    logging.info(f"Successfully got data.")

    return daily_events


def map_data(daily_events: List[Dict]) -> List[GithubEvent]:
    final_list = []
    for event in daily_events:
        mapped_event = GithubEvent(event)
        final_list.append(mapped_event)

    return final_list


def export_data(prepared_data: List[Dict]):
    client = ClickhouseLocalhost()
    schema = GithubEvent.get_ch_table_schema()

    client.create_github_entity_table(db_name=GITHUB_EVENT_TABLE_INFO['db_name'],
                                      table_name=GITHUB_EVENT_TABLE_INFO['table_name'],
                                      schema=schema,
                                      partition=GITHUB_EVENT_TABLE_INFO['partition_by'],
                                      order_by=GITHUB_EVENT_TABLE_INFO['order_by'])
    client.insert_data(db_name=GITHUB_EVENT_TABLE_INFO['db_name'],
                       table_name=GITHUB_EVENT_TABLE_INFO['table_name'],
                       data=prepared_data,
                       schema=schema)
    logging.info(f'Successfully completed task export_data_task')


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
    catchup=False,
    tags=[Tag.daily, Tag.github, Tag.with_catchup]
)
def create_dag():
    @task(task_id='fetch_github_data')
    def fetch_data_task() -> List[Dict]:
        context = get_current_context()
        return fetch_data(context)

    fetched_data = fetch_data_task()

    @task(task_id='map_data')
    def map_data_task(raw_data: List[Dict]) -> List[Dict]:
        final_list = [GithubEvent(github_event).to_dict() for github_event in raw_data]
        logging.info(f'Finished transforming all events, total length of events: {len(final_list)}')
        return final_list

    # Using XCom here, however with 'big' data might need to save data to the filesystem and read from there
    mapped_data = map_data_task(fetched_data)

    @task(task_id='export_data_into_db')
    def export_data_task(prepared_data: List[Dict]):
        export_data(prepared_data)

    export_data_task(mapped_data)


created_dag = create_dag()


def main():
    """Main function for local script testing. Set LOCAL_DEBUG=1 option in run config for that to work."""
    gh = GHArchive()
    # data = gh.get('6/8/2020', '6/8/2020')
    # daily_events = data.to_dict_list()
    test_data = [
        {"id": "1",
         "created_at": "2020-06-08T00:59:32+00:00",
         "type": "CreateEvent",
         "actor": {"id": 123},
         "repo": {"id": 111111},
         "payload": {"ref_type": 'repository', "push_id": 7878},
         "commits": [1, 2, 3]},
        {"id": "2",
         "created_at": "2020-06-07T01:59:32+00:00",
         "type": "CreateEvent",
         "actor": {"id": 123},
         "repo": {"id": 222222},
         "payload": {"ref_type": "repository", "push_id": 898989},
         "commits": []},
        {"id": "3",
         "created_at": "2020-06-06T00:59:32+00:00",
         "type": "CreateEvent",
         "actor": {"id": 22},
         "repo": {"id": 111111},
         "payload": {"ref_type": 'repository', "push_id": 7878},
         "commits": [1, 2]},
        {"id": "4",
         "created_at": "2020-06-05T00:59:32+00:00",
         "type": "PushEvent",
         "actor": {"id": 456},
         "repo": {"id": 222222},
         "payload": {"ref_type": "branch", "push_id": 898989},
         "commits": [1]},
        {"id": "5",
         "created_at": "2020-06-04T00:59:32+00:00",
         "type": "PushEvent",
         "actor": {"id": 456},
         "repo": {"id": 111111},
         "payload": {"ref_type": None, "push_id": 7878},
         "commits": [1, 2, 3, 4, 5]},
        {"id": "6",
         "created_at": "2020-06-03T00:59:32+00:00",
         "type": "PushEvent",
         "actor": {"id": 22},
         "repo": {"id": 222222},
         "payload": {"ref_type": "branch", "push_id": 898989},
         "commits": []}
    ]

    transformed_list = [GithubEvent(github_event).to_dict() for github_event in test_data]
    test_result = transformed_list[0] == {
            "id": "1",
            "created_at": "2020-06-08 00:59:32",
            "type": "CreateEvent",
            "actor_id": 123,
            "repo_id": 111111,
            "ref_type": 'repository',
            "push_id": 7878,
            "commit_amount": 3,
        }
    print(f"TEST RESULT: {test_result}")


if __name__ == '__main__':
    if os.environ.get('LOCAL_DEBUG'):
        exit(main())
