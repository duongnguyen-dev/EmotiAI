import os
import mlflow
import s3fs
import keras
import tensorflow as tf
import numpy as np
import pandas as pd
import nltk 
import kserve
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import stopwords
from typing import Dict
from kserve import Model
from src.models.mlp.config import MLPConfig

class MLPModel(Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.model = None
        self.ready = False
        self.load()
    
    def load(self):
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        self.model = mlflow.tensorflow.load_model(os.getenv("MLFLOW_REGISTERED_MODEL"))
        self.ready = True

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
    
    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        raw_data = payload["instances"][0]["text"]

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
            output_mode=MLPConfig.OUTPUT_MODE,
            output_sequence_length=MLPConfig.SEQUENCE_LENGTH
        )
        
        vectorized_text = vectorizer(preprocessed_text)
        tensor_vectorized_text = tf.expand_dims(vectorized_text, axis=0)
        y_pred = self.model.predict(tensor_vectorized_text)
        result = np.argwhere(y_pred > 0.5)

        classnames = [
            "admiration",
            "amusement",
            "anger",
            "annoyance",
            "approval",
            "caring",
            "confusion",
            "curiosity",
            "desire",
            "disappointment",
            "disapproval",
            "disgust",
            "embarrassment",
            "excitement",
            "fear",
            "gratitude",
            "grief",
            "joy",
            "love",
            "nervousness",
            "optimism",
            "pride",
            "realization",
            "relief",
            "remorse",
            "sadness",
            "surprise",
            "neutral"
        ]

        postprocessed_result = [classnames[i] for i in result[0]]

        return {"prediction": postprocessed_result}

if __name__ == "__main__":
    model = MLPModel("mlp-model")
    model.load()
    kserve.ModelServer().start([model])
