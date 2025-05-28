from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from src.train_model import train_model
from src.evaluate_model import evaluate_model
from src.s3_utils import download_model_from_s3, upload_model_to_s3

# Deploys new model to s3 bucket if new model is better based on accuracy
def deploy_if_better(**context):
    new_acc = context["ti"].xcom_pull(task_ids="evaluate_new_model")
    old_acc = context["ti"].xcom_pull(task_ids="evaluate_old_model")
    if new_acc > old_acc:
        download_model_from_s3("model/new_model.pkl", "best_model.pkl")
        upload_model_to_s3("best_model.pkl", "model/latest_model.pkl")
        print("New model deployed.")
    else:
        print("New model not better.")
with DAG("mlops_pipeline", start_date=datetime(2025, 5, 25)) as dag:
    train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
        op_kwargs={"s3_key": "model/new_model.pkl"}
    )

    eval_new = PythonOperator(
        task_id="evaluate_new_model",
        python_callable=evaluate_model,
        op_kwargs={"s3_key": "model/new_model.pkl"}
    )

    eval_old = PythonOperator(
        task_id="evaluate_old_model",
        python_callable=evaluate_model,
        op_kwargs={"s3_key": "model/latest_model.pkl"}
    )

    deploy = PythonOperator(
        task_id="deploy_if_better",
        python_callable=deploy_if_better,
        provide_context=True,
    )

    train >> [eval_new, eval_old] >> deploy