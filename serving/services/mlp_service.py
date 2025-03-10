import os
import mlflow
import s3fs
import keras
import tensorflow as tf
import numpy as np
import pandas as pd
import nltk 
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import stopwords
from typing import Dict

class MultiLayerPerceptronService:
    def __init__(self, name, output_sequence_length, output_mode):
        self.name = name
        self.output_sequence_length = output_sequence_length
        self.output_mode = output_mode
        self.load()
        
    def load(self):
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        self.model = mlflow.tensorflow.load_model(os.getenv("MLFLOW_REGISTERED_MODEL"))
        s3 = s3fs.S3FileSystem(
            anon=True, 
            key=os.getenv("MINIO_ACCESS_KEY"), 
            secret=os.getenv("MINIO_SECRET_KEY"), 
            endpoint_url=os.getenv("MINIO_ENDPOINT_URL")
        )

        with s3.open(f's3://emotiai/goemotion/vocabulary.parquet', 'rb') as f:
            df = pd.read_parquet(f, engine="pyarrow")

            # Stack all tensors into a single tensor (if they have the same shape)
        self.vocabulary = df["vocabulary"]

        self.read = True
    
    def preprocess(self, raw_data):
        '''
        Preprocessing training data with the following steps:
            - Remove extra space
            - Tokenize into single word (Sequence tokenization)
            - Remove stop word
            - Lemmatize 
        '''

        stopword = set(stopwords.words("english"))
        lemmatizer = nltk.WordNetLemmatizer()

        # Remove extra space
        stripped_x = " ".join(raw_data.split())

        # Word tokenization
        tokenized_x = stripped_x.split(" ")

        # Lemmatize + remove stopped words
        filtered_x = [lemmatizer.lemmatize(token) for token in tokenized_x if token not in stopword]
        
        preprocessed_text = ' '.join(filtered_x)
        vectorizer = keras.layers.TextVectorization(
            vocabulary=self.vocabulary,
            output_mode=self.output_mode,
            output_sequence_length=self.output_sequence_length
        )
        
        vectorized_text = vectorizer(preprocessed_text)
        return tf.expand_dims(vectorized_text, axis=0)

    def predict(self, text: str, headers: Dict[str, str] = None) -> Dict:
        preprocessed_text = self.preprocess(text)
        y_pred = self.model.predict(preprocessed_text)
        return {"predictions": y_pred}

    def postprocess(self):
        pass