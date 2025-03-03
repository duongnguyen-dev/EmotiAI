import mlflow
import tensorflow as tf
from utils import *
from src.models.mlp import MLP
from src.metrics import classification_metrics

def train():
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("/mlp")
    mlflow.tensorflow.autolog()

    X_train, y_train = load_ds("train")
    X_eval, y_eval = load_ds("dev")

    metrics = classification_metrics("macro")

    model = MLP()

    model.compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=metrics
    )

    model.fit(X_train, y_train, epochs=2, validation_data=(X_eval, y_eval))

if __name__ == "__main__":
    train()