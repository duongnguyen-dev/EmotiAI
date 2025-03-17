import os
import json
import h5py

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

with DAG(
    dag_id="etl_postgres_to_minio",
    start_date=datetime(2025, 2, 28),
) as dag:

    def extract(**kwargs):
        from sqlalchemy import create_engine, Column, Integer, String, ARRAY
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        ti = kwargs["ti"]

        engine = create_engine(Variable.get("postgres_conn"))
        Session = sessionmaker(bind=engine)
        session = Session()

        Base = declarative_base()
        extracted_data = {x: {} for x in ["train", "test", "dev"]}
        for i in ["train", "test", "dev"]:
            class Table(Base):
                __tablename__ = i
                id = Column(Integer, primary_key=True)
                text = Column(String)
                label = Column(ARRAY(Integer))

            data = session.query(Table).all()
            queried_data = {
                "text": [x.text for x in data],
                "label": [y.label for y in data]
            }
            extracted_data[i] = queried_data
        ti.xcom_push("extracted_data", extracted_data)

    def transform(**kwargs):
        from sklearn.preprocessing import MultiLabelBinarizer
        from src.dataset.preprocess import preprocess_features, preprocess_labels
        
        ti = kwargs["ti"]

        extracted_data = ti.xcom_pull(task_ids="extract", key="extracted_data")

        preprocessed_data = {x: {} for x in ["train", "test", "dev"]}
        
        mlb = MultiLabelBinarizer()

        for key, value in extracted_data.items():
            preprocessed_data[key]["features"] = preprocess_features(value["text"])
            preprocessed_data[key]["labels"] = preprocess_labels(mlb, key, value["label"])

        current_dag_directory = os.path.dirname(os.path.abspath(__file__))
        output_directory = os.path.join(current_dag_directory, 'output')
        
        os.makedirs(output_directory, exist_ok=True)

        for i in ["train", "test", "dev"]:
            output_file_path = os.path.join(output_directory, f"{i}.h5")

            with h5py.File(output_file_path, "w") as f:
                f.create_dataset('features', data=preprocessed_data[i]["features"])
                f.create_dataset('labels', data=preprocessed_data[i]["labels"])

            kwargs['ti'].xcom_push(key=f'{i}_h5_file_path', value=output_file_path)
            kwargs['ti'].xcom_push(key="temp_data_storage_dir", value=output_directory)

    def load(**kwargs):
        import minio 

        ti = kwargs["ti"]
        client = minio.Minio(
            endpoint=Variable.get("minio_endpoint").split("://")[-1],
            access_key=Variable.get("minio_access_key"),
            secret_key=Variable.get("minio_secret_key"),
            secure=False,
        )
        for i in ["train", "test", "dev"]:
            transformed_data = ti.xcom_pull(task_ids="transform", key=f'{i}_h5_file_path')
            client.fput_object(
                bucket_name="emotiai",
                object_name=os.path.join("goemotion", f"{i}.h5"),
                file_path=transformed_data,
            )

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
    )


    extract_task >> transform_task >> load_task