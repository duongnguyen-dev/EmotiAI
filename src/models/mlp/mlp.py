import tensorflow as tf
import keras
from keras.api.models import Model

def mlp_model(max_token,
            sequence_length,
            embedding_size, 
            num_classes,
            initializer):
    input = keras.Input(shape=(13,))
    x = keras.layers.Embedding(input_dim=max_token, # set input shape
                                output_dim=embedding_size, # set size of embedding vector
                                embeddings_initializer=initializer, # default, intialize randomly
                                input_length=sequence_length, # how long is each input
                                name="embedding_1")(input)
    x = keras.layers.Dense(256, activation="relu")(x)
    x = keras.layers.Dense(128, activation="relu")(x)
    x = keras.layers.GlobalAveragePooling1D()(x)
    output = keras.layers.Dense(num_classes, activation="sigmoid")(x)
    model = keras.Model(input, output)

    return model