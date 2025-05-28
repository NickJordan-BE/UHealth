From apache/airflow

USER root
COPY requirements.txt /
RUN pip install - /requirements.txt

USER airflow
COPY dags/ /opt/airflow/dags
COPY src/ /opt/airflow/src