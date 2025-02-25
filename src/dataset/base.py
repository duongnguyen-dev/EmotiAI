import string
from loguru import logger
from abc import ABC, abstractmethod

class BaseDataset(ABC):
    def read_dataset(file_path, result: dict, index: int):
        df = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for (i, line) in enumerate(lines):
                    line = line.strip()
                    items = line.split("\t")
                    text_a = items[0]
                    label = list(map(int, items[1].split(",")))
                    df.append({
                        "text": text_a, 
                        "label": label
                    })
                logger.info(f"Load {file_path} successfully")
        except FileNotFoundError as e:
            logger.error(e)
        
        result[index] = df
        
    def read_labels(file_path, result: dict, index: int):
        labels = []
        try:
            with open(file_path, 'r') as file:
                labels = file.readlines()
                logger.info(f"Loading labels successfully. There are {len(labels)} in total.")
        except FileNotFoundError as e:
            logger.error(e)
        result[index] = labels

    @classmethod
    @abstractmethod
    def _prepare():
        pass