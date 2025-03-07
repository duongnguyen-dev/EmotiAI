import tensorflow as tf
import keras
from keras.api.models import Model

class MLPConfig:
    MAX_TOKEN=20000
    SEQUENCE_LENGTH=13
    EMBEDDING_SIZE=128
    NUM_CLASSES=28
    INITIALIZER="uniform"
    OUTPUT_MODE="int"

class MLP(Model):
    def __init__(self,
                 max_token=MLPConfig.MAX_TOKEN,
                 sequence_length=MLPConfig.SEQUENCE_LENGTH,
                 embedding_size=MLPConfig.EMBEDDING_SIZE, 
                 num_classes=MLPConfig.NUM_CLASSES,
                 initializer=MLPConfig.INITIALIZER,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_token = max_token
        self.sequence_length = sequence_length
        self.embedding_size = embedding_size
        self.initializer = initializer
        self.num_classes = num_classes

        self.vectorizer = keras.layers.TextVectorization(
            max_tokens=MLPConfig.MAX_TOKEN,
            output_mode=MLPConfig.OUTPUT_MODE,
            output_sequence_length=int(MLPConfig.SEQUENCE_LENGTH),
            standardize=None
        )
        
        self.embedding = keras.layers.Embedding(input_dim=self.max_token, # set input shape
                                            output_dim=self.embedding_size, # set size of embedding vector
                                            embeddings_initializer=self.initializer, # default, intialize randomly
                                            input_length=self.sequence_length, # how long is each input
                                            name="embedding_1") 
        self.dense_layer_1 = keras.layers.Dense(512, activation="relu")
        self.dense_layer_2 = keras.layers.Dense(256, activation="relu")
        self.global_average_1d = keras.layers.GlobalAveragePooling1D()
        self.output_layer = keras.layers.Dense(self.num_classes, activation="sigmoid")
        self.input_shape = (sequence_length,)  

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
            'max_token': self.max_token,
            'sequence_length': self.sequence_length,
            'embedding_size': self.embedding_size,
            'num_classes': self.num_classes,
            'initializer': self.initializer,
        }

    @classmethod
    def from_config(cls, config):
        return cls(**config)