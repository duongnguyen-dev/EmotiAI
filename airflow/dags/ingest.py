import os
import json
import h5py
import minio 

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dataset.goemotion import GoEmotionDataset

with DAG(
    dag_id="etl_postgres_to_minio",
    start_date=datetime(2025, 2, 28),
) as dag:
    def extract(**kwargs):
        ti = kwargs["ti"]

        engine = create_engine("postgresql+psycopg2://emotiai:emotiai@172.18.0.1:5437/goemotion")
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
        ti = kwargs["ti"]

        extracted_data = ti.xcom_pull(task_ids="extract", key="extracted_data")
        # json_extracted_data = json.loads(extracted_data)
        ge = GoEmotionDataset(extracted_data)

        current_dag_directory = os.path.dirname(os.path.abspath(__file__))
        output_directory = os.path.join(current_dag_directory, 'output')

        os.makedirs(output_directory, exist_ok=True)

        for i in ["train", "test", "dev"]:
            ds = ge.get_preprocessed_data(i)
            output_file_path = os.path.join(output_directory, f"{i}.h5")

            with h5py.File(output_file_path, "w") as f:
                features_group = f.create_group('features')
                for idx, tensor in enumerate(ds["features"]):
                    features_group.create_dataset(f'tensor_{idx}', data=tensor)
                f.create_dataset('labels', data=ds["labels"])

            kwargs['ti'].xcom_push(key=f'{i}_h5_file_path', value=output_file_path)
            kwargs['ti'].xcom_push(key="temp_data_storage_dir", value=output_directory)

    def load(**kwargs):
        ti = kwargs["ti"]
        client = minio.Minio(
            endpoint="172.18.0.1:9000",
            access_key="minio_access_key",
            secret_key="minio_secret_key",
            secure=False,
        )
        for i in ["train", "test", "dev"]:
            transformed_data = ti.xcom_pull(task_ids="transform", key=f'{i}_h5_file_path')
            client.fput_object(
                bucket_name="emotiai",
                object_name=os.path.join("goemotion", f"{i}.h5"),
                file_path=transformed_data,
            )

        # Remove temporary dir
        

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