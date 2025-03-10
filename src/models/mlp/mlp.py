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


@keras.saving.register_keras_serializable(package="MLP")
class MLP(Model):
    def __init__(self,
                 vectorizer,
                 max_token,
                 sequence_length,
                 embedding_size, 
                 num_classes,
                 initializer,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_token = max_token
        self.sequence_length = sequence_length
        self.embedding_size = embedding_size
        self.initializer = initializer
        self.num_classes = num_classes

        self.vectorizer = vectorizer
        
        self.embedding = keras.layers.Embedding(input_dim=self.max_token, # set input shape
                                            output_dim=self.embedding_size, # set size of embedding vector
                                            embeddings_initializer=self.initializer, # default, intialize randomly
                                            input_length=self.sequence_length, # how long is each input
                                            name="embedding_1") 
        self.dense_layer_1 = keras.layers.Dense(256, activation="relu")
        self.dense_layer_2 = keras.layers.Dense(128, activation="relu")
        self.global_average_1d = keras.layers.GlobalAveragePooling1D()
        self.output_layer = keras.layers.Dense(self.num_classes, activation="sigmoid")
        self.input_shape = (1,)  

    def call(self, inputs):
        tf.random.set_seed(42)

        x = self.vectorizer(inputs)
        x = self.embedding(x)
        x = self.dense_layer_1(x)
        x = self.dense_layer_2(x)
        x = self.global_average_1d(x)
        outputs = self.output_layer(x)
        
        return outputs

    def get_config(self):
        # Return only custom parameters
        return {
            'vectorizer': self.vectorizer,
            'max_token': self.max_token,
            'sequence_length': self.sequence_length,
            'embedding_size': self.embedding_size,
            'num_classes': self.num_classes,
            'initializer': self.initializer,
        }

    @classmethod
    def from_config(cls, config):
        return cls(**config)