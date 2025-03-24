import tensorflow as tf

def classification_metrics(average: str = None):
    f1_name = f'_{average}'
    if average == None:
        f1_name = ''

    return [tf.keras.metrics.F1Score(
        name=f'f1_{f1_name}',
        average=average,
    ), tf.keras.metrics.BinaryAccuracy("binary_accuracy"), tf.keras.metrics.Precision(name="precision"), tf.keras.metrics.Recall(name="recall")]