
import os
import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from postgresql_client import PostgresSQLClient
from configs.config import PROJECT_DIR

load_dotenv()

def load_label(file_path: str):
    label_dict = {}
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                label_dict[i] = line.replace("\n", "")
            logger.info(f"Loading labels successfully. There are {len(label_dict)} in total.")
    except FileNotFoundError as e:
        logger.error(e)
    return label_dict

def insert():
    pc = PostgresSQLClient(
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT")
    )

    # Get all columns from the devices table
    try:
        columns = pc.get_columns(table_name="label")
        logger.info(columns)
    except Exception as e:
        logger.error(f"Failed to get schema for table with error: {e}")

    
    ds = load_label(f"{PROJECT_DIR}/data/original/labels.txt")

    for index, data in ds.items():
        inserted_data = (index, 
                        data,
                        )
        
        pc.execute_query(f"""
            insert into label ({",".join(columns)})
            values (%s, %s)
        """, inserted_data)

if __name__ == "__main__":
    insert()
