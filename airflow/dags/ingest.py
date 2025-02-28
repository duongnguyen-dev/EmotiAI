from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

with DAG(
    dag_id="etl_postgres_to_minio",
    start_date=datetime(2025, 2, 28),
) as dag:
    def extract(**kwargs):
        ti = kwargs["ti"]

        engine = create_engine("postgresql+psycopg2://emotiai:emotiai@127.0.0.1:5437/goemotion")
        Session = sessionmaker(bind=engine)
        session = Session()

        Base = declarative_base()

        for i in ["train", "test", "dev"]:
            
            class Table(Base):
                __tablename__ = i
                id = Column(Integer, primary_key=True)
                text = Column(String)
                label = Column(ARRAY(Integer))

            data = session.query(Table).all()
            extracted_data = {
                "text": [x for x in data.text],
                "label": [y for y in data.label]
            }

            ti.xcom_push(i, extracted_data)

    def trainsform(**kwargs):
        ti = kwargs["ti"]
        extracted_data = ti.xcom_pull(task_ids=)