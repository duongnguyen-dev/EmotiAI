import mlflow
import tensorflow as tf
from utils import *
from keras import layers, models

class DatasetConfig:
    MAX_TOKEN = 20000
    SEQUENCE_LENGTH = 13
    LABEL_SIZE=28

def main():
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("/mlp")
    mlflow.tensorflow.autolog()

    X_train, y_train = load_ds("train")
    X_test, y_test = load_ds("test")
    X_eval, y_eval = load_ds("dev")

    tf.random.set_seed(42)
    embedding = layers.Embedding(input_dim=DatasetConfig.MAX_TOKEN, # set input shape
                                output_dim=128, # set size of embedding vector
                                embeddings_initializer="uniform", # default, intialize randomly
                                input_length=DatasetConfig.SEQUENCE_LENGTH, # how long is each input
                                name="embedding_1") 
    
    inputs = layers.Input(shape=(13,)) 
    x = embedding(inputs)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(DatasetConfig.LABEL_SIZE, activation="sigmoid")(x)
    model = models.Model(inputs, outputs, name="MLP")

    model.compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["binary_accuracy"]
    )


    model.fit(X_train, y_train, epochs=3, validation_data=(X_eval, y_eval))

if __name__ == "__main__":
    main()