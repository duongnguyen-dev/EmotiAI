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
        import h5py
        import keras
        import minio 
        from utils import load_ds, set_tracking_uri
        from src.models.mlp.mlp import MLP
        from src.models.mlp.config import MLPConfig
        from src.metrics import classification_metrics

        tracking_uri = Variable.get("mlflow_tracking_uri")
        experiment = Variable.get("mlflow_bucket_name")
        framework = "tensorflow"
        
        set_tracking_uri(experiment, framework, tracking_uri)
        
        access_key = Variable.get("minio_access_key")
        secret_key = Variable.get("minio_secret_key")
        endpoint = Variable.get("minio_endpoint")

        X_train, y_train = load_ds("train", key=access_key, secret=secret_key, endpoint_url=endpoint)
        X_dev, y_dev = load_ds("dev", key=access_key, secret=secret_key, endpoint_url=endpoint)

        vectorizer = keras.layers.TextVectorization(
            max_tokens=MLPConfig.MAX_TOKEN,
            output_mode=MLPConfig.OUTPUT_MODE,
            output_sequence_length=int(MLPConfig.SEQUENCE_LENGTH),
            standardize=None
        )

        vectorizer.adapt(X_train)
        
        vocabulary = vectorizer.get_vocabulary()

        current_dag_directory = os.path.dirname(os.path.abspath(__file__))
        output_directory = os.path.join(current_dag_directory, 'output')
        os.makedirs(output_directory, exist_ok=True)

        output_file_path = os.path.join(output_directory, "vocabulary.h5")

        with h5py.File(output_file_path, "w") as f:
            f.create_dataset('vocabulary', data=vocabulary)

        client = minio.Minio(
            endpoint=Variable.get("minio_endpoint"),
            access_key=Variable.get("minio_access_key"),
            secret_key=Variable.get("minio_secret_key"),
            secure=False,
        )

        client.fput_object(
            bucket_name="emotiai",
            object_name=os.path.join("goemotion", "vocabulary.h5"),
            file_path=output_file_path,
        )

        mlp = MLP(
            vectorizer=vectorizer,
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

        mlp.fit(X_train, y_train, epochs=10, validation_data=(X_dev, y_dev))

    train_task = PythonOperator(
        task_id="train_mlp_model",
        python_callable=train
    )