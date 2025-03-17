
import os
import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from postgresql_client import PostgresSQLClient
from configs.config import PROJECT_DIR

load_dotenv()

def load_dataset(file_path: str):
    ds = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for (i, line) in enumerate(lines):
                line = line.strip()
                items = line.split("\t")
                text_a = items[0]
                label = list(map(int, items[1].split(",")))
                ds.append({
                    "text": text_a, 
                    "label": label
                })
            logger.info(f"Load {file_path} successfully")
    except FileNotFoundError as e:
        logger.error(e)
    
    return ds

def insert():
    pc = PostgresSQLClient(
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT"),
        host=os.getenv("POSTGRES_HOST")
    )

    for i in ["train", "test", "dev"]:

        # Get all columns from the devices table
        try:
            columns = pc.get_columns(table_name=i)
            logger.info(columns)
        except Exception as e:
            logger.error(f"Failed to get schema for table with error: {e}")

        
        ds = load_dataset(f"{PROJECT_DIR}/data/original/{i}.tsv")

        for index, data in enumerate(ds):
            inserted_data = (index, 
                            data['text'],
                            data['label']
                            )
            
            pc.execute_query(f"""
                insert into {i} ({",".join(columns)})
                values (%s, %s, %s)
            """, inserted_data)

if __name__ == "__main__":
    insert()
