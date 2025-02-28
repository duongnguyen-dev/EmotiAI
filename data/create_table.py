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
        port=os.getenv("POSTGRES_PORT")
    )

    for i in ["train", "test", "dev"]:
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {i} (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                label INTEGER[] NOT NULL
            )
        """

        try:
            pc.execute_query(create_table_query, params=None)
            logger.info("Create table successfully")
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    main()