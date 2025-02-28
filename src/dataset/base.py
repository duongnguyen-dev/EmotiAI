from abc import ABC, abstractmethod

class BaseDataset(ABC):
    @abstractmethod
    def _preprocessing():
        pass

    @abstractmethod
    def _load_labels_dict():
        pass

    @abstractmethod
    def _load_raw_dataset():
        pass

    @abstractmethod
    def get_raw_dataset():
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