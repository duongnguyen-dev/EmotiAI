import os
import nltk
import keras
import string
import numpy as np

nltk.download('wordnet')
nltk.download('stopwords')

from time import time
from loguru import logger
from nltk.corpus import stopwords
from src.dataset.base import BaseDataset


class OriginalDataset(BaseDataset):
    _max_token = 10000
    _sequence_length = None
    _lemmatizer = nltk.WordNetLemmatizer()
    _stopword = set(stopwords.words('english')) 
    _ds = None
    _vocabulary = None
    
    def __init__(self, dataset_path):
        super().__init__()
        
        _required_files = ["train.tsv", "test.tsv", "dev.tsv", "labels.txt"]
        _files = os.listdir(dataset_path)
        _processed = True

        for f in _required_files:
            if f not in _files:
                _processed = False
         
        OriginalDataset._ds = OriginalDataset._prepare(dataset_path, _required_files, _processed)

    @classmethod
    def _prepare(cls, dataset_path: str, required_files: list, processed: bool):
        start = time()
        if processed != True:
            logger.error(f"Missing {f.split('.')[0]} file. The input directory should include these files {required_files}.")
            return

        results = {
            x : None for x in range(len(required_files))
        }

        for i, f in enumerate(required_files):
            target_path = os.path.join(dataset_path, f)
            if "labels" not in f:
                cls.read_dataset(target_path, results, i)
            else:
                cls.read_labels(target_path, results, i)
        
        cls._preprocessing(results)

        end = time()
        execution_duration = end - start

        logger.info(f"It takes {execution_duration} to load all dataset and label files")

        return results
    
    @classmethod
    def _preprocessing(cls, results):
        for key in list(results.keys())[:-1]:
            corpus = [x["text"] for x in results[key]]
            
            stopped_tokens = []

            for c in corpus:
                lower = c.lower()
                translation_table = str.maketrans('', '', string.punctuation)
                stripped = lower.translate(translation_table)
                tokens = stripped.split(" ")
                filtered_tokens = [cls._lemmatizer.lemmatize(token) for token in tokens if token not in cls._stopword]
                stopped_tokens.append(filtered_tokens)
            
            if key == 0:
                sequence_length = cls._find_sequence_length(stopped_tokens)

            tonkenized_corpus = [' '.join(token) for token in stopped_tokens]

            vectorizer = keras.layers.TextVectorization(
                max_tokens=cls._max_token,
                output_mode="int",
                output_sequence_length=int(sequence_length),
                standardize=None
            )
            vectorizer.adapt(tonkenized_corpus)
            cls._vocabulary = vectorizer.get_vocabulary()
            vectorized_text = vectorizer(tonkenized_corpus)
            
            for i in range(len(results[key])):
                results[key][i]["vectorized_text"] = vectorized_text[i]

    # Find 95% length of all corpus
    def _find_sequence_length(corpus):
        length_corpus = [len(c) for c in corpus]
        percentile_95 = np.percentile(length_corpus, 95)

        return percentile_95
    
    def get_ds(self, key):
        return self._ds[key]
    
    def get_vocabulary(self):
        return self._vocabulary