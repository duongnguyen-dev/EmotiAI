from keras.api.metrics import F1Score, Precision, Recall

def classification_metrics(average: str = None):
    f1_name = f'_{average}'
    if average == None:
        f1_name = ''

    return [F1Score(
        name=f'f1_{f1_name}',
        average=average,
    ), 'binary_accuracy', Precision(name="precision"), Recall(name="recall")]
    