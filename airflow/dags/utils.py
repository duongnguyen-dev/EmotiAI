import mlflow
import s3fs
import h5py
import tensorflow as tf
import numpy as np
from skmultilearn.model_selection import iterative_train_test_split
from src.models.bert.config import BertConfig

def set_tracking_uri(experiment: str, framework: str, tracking_uri: str):
    """
    Connect to experiment tracking uri. There are two accepted parameters:
    - experiment: Model experiment name, for example '/mlp' to track Multi layer perceptron experiments.
    - framework: It can be either 'tensorflow', 'sklearn', etc.
    """
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)

    if framework == 'tensorflow':
        mlflow.tensorflow.autolog()
    elif framework == 'sklearn':
        mlflow.sklearn.autolog()

def load_ds(dataset_type: str, key: str, secret: str, endpoint_url: str):
    s3 = s3fs.S3FileSystem(
        anon=False, 
        key=key, 
        secret=secret, 
        endpoint_url=endpoint_url
    )

    with s3.open(f's3://emotiai/goemotion/{dataset_type}.h5', 'rb') as f:
        h5_file = h5py.File(f, 'r')

        # Stack all tensors into a single tensor (if they have the same shape)
        features = h5_file["features"]
        tensored_features = tf.convert_to_tensor(features)

        labels_dataset = h5_file['labels']
        tensored_labels = tf.convert_to_tensor(labels_dataset[:], dtype=tf.float32)  
 
    return tf.data.Dataset.from_tensor_slices((tensored_features, tensored_labels)).shuffle(BertConfig.SHUFFLE).batch(BertConfig.BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

def load_ds_10_percent(dataset_type: str, key: str, secret: str, endpoint_url: str):
    s3 = s3fs.S3FileSystem(
        anon=False, 
        key=key, 
        secret=secret, 
        endpoint_url=endpoint_url
    )

    with s3.open(f's3://emotiai/goemotion/{dataset_type}.h5', 'rb') as f:
        h5_file = h5py.File(f, 'r')

        features = np.array(h5_file["features"]).reshape(-1, 1)
        labels = np.array(h5_file['labels'][:])
        
        _, _, X_subset, y_subset = iterative_train_test_split(features, labels, test_size=0.1)
        
        tensored_features = tf.convert_to_tensor(X_subset)
        tensored_labels = tf.convert_to_tensor(y_subset, dtype=tf.float32)

    return tf.data.Dataset.from_tensor_slices((tensored_features, tensored_labels)).shuffle(BertConfig.SHUFFLE).batch(BertConfig.BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
