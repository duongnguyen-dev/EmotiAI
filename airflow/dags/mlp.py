from datetime import datetime
from airflow import DAG
from airflow.models import Variable

with DAG(
    dag_id="mlp_experiment",
    start_date=datetime(2025, 3, 7),
) as dag:
    
    def train():
        import mlflow
        import tensorflow as tf
        from utils import load_ds, set_tracking_uri
        from src.models.mlp.mlp import MLP
        from src.metrics import classification_metrics

        key = Variable()