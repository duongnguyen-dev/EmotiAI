import os

from dotenv import load_dotenv
from postgresql_client import PostgresSQLClient
from loguru import logger
load_dotenv()


def main():
    pc = PostgresSQLClient(
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS label (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    """

    try:
        pc.execute_query(create_table_query, params=None)
        logger.info("Create table successfully")
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()