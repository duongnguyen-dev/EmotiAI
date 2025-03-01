from abc import ABC, abstractmethod

class BaseDataset(ABC):
    @abstractmethod
    def _preprocessing():
        pass

    @abstractmethod
    def get_preprocessed_data():
        pass

    @abstractmethod
    def get_vocabulary():
        pass

    @abstractmethod
    def get_vocabulary_length():
        pass