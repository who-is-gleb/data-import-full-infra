# Disregarded

FROM apache/superset:latest
USER root
RUN pip install clickhouse-sqlalchemy
RUN superset-localhost superset fab create-admin \
--username gleb \
--firstname Superset \
--lastname Admin \
--email admin@superset.com \
--password gleb
RUN superset-localhost superset db upgrade
# RUN superset-localhost superset load_examples
RUN superset-localhost superset init
USER superset