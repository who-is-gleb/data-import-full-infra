import os
import logging
import datetime
import pathlib

from airflow.decorators import dag, task
from airflow.sensors.external_task import ExternalTaskSensor
from core.dag_default_args import get_default_arguments
from core.clickhouse import ClickhouseLocalhost
from models.tags import Tag
from datetime import timedelta
from typing import Dict


doc_md = """
### This DAG creates views that will be able to show the needed metrics.
The dashboard can select * from a view to get the result. It will only need to show the result.
"""

DAG_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

METRICS_QUERIES = {
    'devs_own_more_than_one_repo': {
        'query': (DAG_DIR / pathlib.Path('queries/devs_own_more_than_one_repo.sql')).open().read(),
        'view_name': 'devs_own_more_than_one_repo'
    },
    'devs_more_than_one_commit_daily': {
        'query': (DAG_DIR / pathlib.Path('queries/devs_more_than_one_commit_daily.sql')).open().read(),
        'view_name': 'devs_more_than_one_commit_daily'
    },
    'devs_less_than_one_commit_daily': {
        'query': (DAG_DIR / pathlib.Path('queries/devs_less_than_one_commit_daily.sql')).open().read(),
        'view_name': 'devs_less_than_one_commit_daily'
    },
    'repo_more_than_ten_members': {
        'query': (DAG_DIR / pathlib.Path('queries/projects_more_than_ten_members.sql')).open().read(),
        'view_name': 'repo_more_than_ten_members'
    },
}

default_args = get_default_arguments(
    retry_delay=timedelta(minutes=1)
)


@dag(
    dag_id='github-archive-create-metrics',
    doc_md=doc_md,
    description='Creates needed metrics once a day',
    schedule_interval='@daily',
    start_date=datetime.datetime(2022, 9, 1),
    default_args=default_args,
    catchup=False,
    tags=[Tag.daily, Tag.github, Tag.metrics]
)
def create_dag():
    wait_for_data = ExternalTaskSensor(
        task_id='wait_for_data',
        external_dag_id='github-archive-daily-import',
        external_task_id=None,
        timeout=60 * 60,
        allowed_states=['success'],
        failed_states=['failed'],
        mode='reschedule',
        poke_interval=30
    )
    for metric_name, metrics_config in METRICS_QUERIES.items():
        @task(task_id=f'create-view-{metric_name}')
        def create_views_task(_metrics_config: Dict):
            view_name = _metrics_config['view_name']
            query = _metrics_config['query']
            logging.info(f'This task is about to create view github_data.{view_name}')
            logging.info(f'The query is:\n{query}')

            client = ClickhouseLocalhost()
            client.create_view(db_name='github_data', view_name=view_name, query=query)

        wait_for_data >> create_views_task(metrics_config)


created_dag = create_dag()


def main():
    pass


if __name__ == '__main__':
    if os.environ.get('LOCAL_DEBUG'):
        exit(main())
