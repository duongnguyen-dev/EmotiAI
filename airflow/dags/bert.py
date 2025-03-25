from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator

with DAG(
    dag_id="bert_feature_extraction_10_percent_experiment",
    start_date=datetime(2025, 3, 25),
) as dag:
    
    def train():
        import os
        os.environ['TF_USE_LEGACY_KERAS'] = '1'
        import tensorflow as tf
        import mlflow
        import numpy as np
        import tensorflow_hub as hub
        import tensorflow_text
        from mlflow.types import TensorSpec, Schema
        from mlflow.models import ModelSignature
        from utils import load_ds, set_tracking_uri, load_ds_10_percent
        from src.models.bert.bert import build_bert_model, build_bert_preprocessor
        from src.models.bert.config import BertConfig
        from src.metrics import classification_metrics
        
        # Connect with MLflow tracking URI and init autologging
        tracking_uri = Variable.get("mlflow_tracking_uri")
        experiment = Variable.get("mlflow_bucket_name")
        framework = "tensorflow"
        
        set_tracking_uri(experiment, framework, tracking_uri)

        # Load dataset from data lake        
        access_key = Variable.get("minio_access_key")
        secret_key = Variable.get("minio_secret_key")
        endpoint = Variable.get("minio_endpoint")

        train_ds_10_percent = load_ds_10_percent("train", key=access_key, secret=secret_key, endpoint_url=endpoint)
        dev_ds = load_ds("dev", key=access_key, secret=secret_key, endpoint_url=endpoint)

        metrics = classification_metrics("macro")
        bert_preprocessor = build_bert_preprocessor()
        bert_model = hub.KerasLayer(BertConfig.BERT_MODEL, trainable=False)
        model = build_bert_model(bert_preprocessor, bert_model)
    
        metrics = classification_metrics("macro")
        model.compile(
                loss="binary_crossentropy",
                optimizer="adam",
                metrics=metrics
            )
        input_schema = Schema(
            [TensorSpec(np.dtype(np.int32), (-1, 13), "input")]
        )
        signature = ModelSignature(input_schema)
        
        with mlflow.start_run() as run:
            mlflow.tensorflow.log_model(model, "bert_feature_extraction_10_percent", signature=signature)
        model.fit(train_ds_10_percent, epochs=10, validation_data=dev_ds)

    train_task = PythonOperator(
        task_id="train_bert_model",
        python_callable=train
    )