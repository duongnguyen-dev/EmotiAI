import argparse
import mlflow
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
        self.read = True

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        text = payload["text"]
        loaded_model = mlflow.pyfunc.load_model(self.registered_model)

        y_pred = loaded_model.predict(input.numpy().reshape(-1, len(input)))