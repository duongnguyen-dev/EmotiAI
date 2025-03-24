import tensorflow_hub as hub
import tensorflow as tf
from config import BertConfig

def build_bert_model(bert_preprocessor, bert_model):
    inputs = tf.keras.layers.Input(shape=(), dtype="string")
    encoder_inputs = bert_preprocessor(inputs)
    bert_outputs = bert_model(encoder_inputs)
    outputs = tf.keras.layers.Dense(BertConfig.NUM_CLASSES, activation="sigmoid")(bert_outputs["pooled_output"])
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    return model

def build_bert_preprocessor():
    preprocessor = hub.load(BertConfig.BERT_PREPROCESSOR)
    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
    tokenize = hub.KerasLayer(preprocessor.tokenize)
    tokenized_input = tokenize(text_input)
    packer = hub.KerasLayer(
        preprocessor.bert_pack_inputs,
        arguments=dict(seq_length=BertConfig.SEQUENCE_LENGTH)
    )
    encoder_inputs = packer([tokenized_input])

    return tf.keras.Model(text_input, encoder_inputs)