import mlflow
import h5py
import s3fs
import os
import keras
from kserve import Model, ModelServer
from typing import Union, Dict
from utils import preprocess

class MultiLayerPerceptronModel(Model):
    def __init__(self, name, tracking_uri, registered_model):
        super().__init__(name)
        self.name = name
        self.tracking_uri = tracking_uri
        self.registered_model = registered_model
        self.load()
    
    def load(self):
        mlflow.set_tracking_uri(self.tracking_uri)
        self.model = mlflow.pyfunc.load_model(self.registered_model)
        s3 = s3fs.S3FileSystem(
            anon=False, 
            key=os.getenv("MINIO_ACCESS_KEY"), 
            secret=os.getenv("MINIO_SECRET_KEY"), 
            endpoint_url=os.getenv("MINIO_ENDPOINT_URL")
        )

        with s3.open(f's3://emotiai/goemotion/vocabulary.h5', 'rb') as f:
            h5_file = h5py.File(f, 'r')

            # Stack all tensors into a single tensor (if they have the same shape)
        self.vocabulary = h5_file["vocabulary"]

        self.read = True

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        text = payload["text"]
        loaded_model = mlflow.pyfunc.load_model(self.registered_model)
        preprocessed_text = preprocess(text)

        vectorizer = keras.layers.TextVectorization(
            max_tokens=len(self.vocabulary),
            output_mode='int',
            vocabulary=self.vocabulary
        )

        vectorized_text = vectorizer(preprocessed_text)
        y_pred = loaded_model.predict(vectorized_text)
        return {"predictions": y_pred}
    
if __name__ == "__main__":
    model = MultiLayerPerceptronModel(
        "mlp_v1",
        os.getenv("MLFLOW_TRACKING_URI"),
        os.getenv("MLFLOW_REGISTERED_MODEL"),
    )

    ModelServer().start([model])
