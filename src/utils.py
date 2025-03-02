import os
import h5py
import tensorflow as tf 
import s3fs
from dotenv import load_dotenv

load_dotenv()

def load_ds(dataset_type: str):
    s3 = s3fs.S3FileSystem(
        anon=False, 
        key=os.getenv("MINIO_ACCESS_KEY"), 
        secret=os.getenv("MINIO_SECRET_KEY"), 
        endpoint_url="http://localhost:9000"
    )

    features = []
    labels = []

    with s3.open(f's3://emotiai/goemotion/{dataset_type}.h5', 'rb') as f:
        h5_file = h5py.File(f, 'r')

        features_group = h5_file["features"]

        features = []
        for name, dataset in features_group.items():
            features.append(dataset[:])

        # Stack all tensors into a single tensor (if they have the same shape)
        tensored_features = tf.convert_to_tensor(features)

        labels_dataset = h5_file['labels']
        tensored_labels = tf.convert_to_tensor(labels_dataset[:])  
 
    return tensored_features, tensored_labels