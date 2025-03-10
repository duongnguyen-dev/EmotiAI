from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator

with DAG(
    dag_id="mlp_experiment",
    start_date=datetime(2025, 3, 7),
) as dag:
    
    def train():
        import os
        import mlflow
        import pandas as pd
        import keras
        import minio 
        import numpy as np
        from mlflow.types import TensorSpec, Schema
        from mlflow.models import ModelSignature
        from utils import load_ds, set_tracking_uri
        from src.models.mlp.mlp import MLP, mlp_model
        from src.models.mlp.config import MLPConfig
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

        X_train, y_train = load_ds("train", key=access_key, secret=secret_key, endpoint_url=endpoint)
        X_dev, y_dev = load_ds("dev", key=access_key, secret=secret_key, endpoint_url=endpoint)

        # Vectorize dataset
        vectorizer = keras.layers.TextVectorization(
            max_tokens=MLPConfig.MAX_TOKEN,
            output_mode=MLPConfig.OUTPUT_MODE,
            output_sequence_length=int(MLPConfig.SEQUENCE_LENGTH),
            standardize=None
        )

        vectorizer.adapt(X_train)
        X_train = vectorizer(X_train)
        X_dev = vectorizer(X_dev)

        # Store vocabulary
        vocabulary = vectorizer.get_vocabulary()

        current_dag_directory = os.path.dirname(os.path.abspath(__file__))
        output_directory = os.path.join(current_dag_directory, 'output')
        os.makedirs(output_directory, exist_ok=True)

        output_file_path = os.path.join(output_directory, "vocabulary.parquet")
        vocab_df = pd.DataFrame({"vocabulary" : vocabulary})
        vocab_df.to_parquet(output_file_path, engine="pyarrow", index=False)
        
        client = minio.Minio(
            endpoint=endpoint.split("://")[-1],
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

        client.fput_object(
            bucket_name="emotiai",
            object_name=os.path.join("goemotion", "vocabulary.parquet"),
            file_path=output_file_path,
        )

        # Create tensorflow model
        mlp = mlp_model(
            max_token=MLPConfig.MAX_TOKEN,
            sequence_length=MLPConfig.SEQUENCE_LENGTH,
            embedding_size=MLPConfig.EMBEDDING_SIZE,
            num_classes=MLPConfig.NUM_CLASSES,
            initializer=MLPConfig.INITIALIZER
        )

        metrics = classification_metrics("macro")
        mlp.compile(
                loss="binary_crossentropy",
                optimizer="adam",
                metrics=metrics
            )
        input_schema = Schema(
            [TensorSpec(np.dtype(np.int32), (-1, 13), "input")]
        )
        signature = ModelSignature(input_schema)
        
        with mlflow.start_run() as run:
            mlflow.tensorflow.log_model(mlp, "mlp", signature=signature)
        mlp.fit(X_train, y_train, epochs=10, validation_data=(X_dev, y_dev))

    train_task = PythonOperator(
        task_id="train_mlp_model",
        python_callable=train
    )