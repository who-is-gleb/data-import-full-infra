import logging
import os
import textwrap
import typing
from clickhouse_driver import Client

ch_host = os.environ.get('CH_HOST')


class ClickhouseLocalhost:
    conn_id: str = ch_host
    port: int = 9000
    _client: Client = None

    def __init__(self):
        pass

    def get_client(self) -> Client:
        if self._client is None:
            client = Client(self.conn_id, port=self.port, database='default', user='default', password='')
            self._client = client
        return self._client

    def execute(self, query, *args, **kwargs):
        logging.info(f'Will be executing:\n{query}')
        return self.get_client().execute(query, *args, **kwargs)

    def _create_github_data_db(self, db_name: str):
        logging.info(f'Will be creating database {db_name} if not exists.')
        query = f"""
        CREATE DATABASE IF NOT EXISTS {db_name}
        """
        self.get_client().execute(query)
        logging.info('Database was successfully created.')

    def create_github_entity_table(self,
                                   db_name: str,
                                   table_name: str,
                                   schema: typing.Dict,
                                   partition: str,
                                   order_by: str):
        logging.info(f'\nWill be creating table {db_name}.{table_name} '
                     f'with schema:\n{schema}\n'
                     f'Partitioned by {partition} and ordered by {order_by}')

        fields = ',\n'.join((f'{field_name} {field_type}' for field_name, field_type in schema.items()))

        self._create_github_data_db(db_name)

        query = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {db_name}.{table_name} (
            {{fields}}
        )
        ENGINE = MergeTree
        PARTITION BY {partition}
        ORDER BY {order_by}
        """).format_map(
            {'fields': textwrap.indent(fields, '  ')}
        )

        logging.info(f'Final query:\n{query}')
        self.get_client().execute(query)
        logging.info('Successfully created table')

    def insert_data(self, db_name: str, table_name: str, data: typing.List[typing.Dict], schema: typing.Dict):
        logging.info(f'About to insert data into {db_name}.{table_name}')

        def generate_rows():
            for row in data:
                yield row

        self.get_client().execute(f"INSERT INTO {db_name}.{table_name} VALUES", generate_rows(), types_check=True)
        logging.info('Successfully inserted data.')

    def create_view(self, db_name: str, view_name: str, query: str):
        logging.info(f'About to create view {db_name}.{view_name}')

        ddl = textwrap.dedent(f"""
        CREATE OR REPLACE VIEW {db_name}.{view_name} AS
        {{query}}
        """).format_map({'query': query}).strip()

        self.get_client().execute(ddl)
        logging.info('Successfully created view.')
