import os
import nltk
import keras
import string
import numpy as np
import matplotlib.pyplot as plt 


nltk.download('wordnet')
nltk.download('stopwords')

from time import time
from loguru import logger
from collections import Counter
from nltk.corpus import stopwords

MAX_TOKEN = 20000 # A very solid threshold. According to Google research, model's performance often peaks at 20.000 features 

def prepare_dataset(file_path: str, result: dict, index: int):
    df = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for (i, line) in enumerate(lines):
                line = line.strip()
                items = line.split("\t")
                text_a = items[0]
                label = list(map(int, items[1].split(",")))
                for l in label:
                    df.append({
                        "text": text_a, 
                        "label": l
                    })
            logger.info(f"Load {file_path} successfully")
    except FileNotFoundError as e:
        logger.error(e)
    
    result[index] = df

def prepare_label(file_path, result: dict, index: int):
    labels = []
    try:
        with open(file_path, 'r') as file:
            labels = file.readlines()
            logger.info(f"Loading labels successfully. There are {len(labels)} in total.")
    except FileNotFoundError as e:
        logger.error(e)
    result[index] = labels

def load_dataset(dataset_path: str):
    start = time()

    required_files = ["train.tsv", "test.tsv", "dev.tsv", "labels.txt"] 
    files = os.listdir(dataset_path)    
    processed = True

    for f in required_files:
        if f not in files:
            processed = False

    if processed != True:
        logger.error(f"Missing {f.split('.')[0]} file. The input directory should include these files {required_files}.")
        return

    results = {
        x : None for x in range(len(required_files))
    }

    for i, f in enumerate(required_files):
        target_path = os.path.join(dataset_path, f)
        if "labels" not in f:
            prepare_dataset(target_path, results, i)
        else:
            prepare_label(target_path, results, i)

    end = time()
    execution_duration = end - start

    logger.info(f"It takes {execution_duration} to load all dataset and label files")

    return results

def visualize(sample: dict, labels: dict):
    print("Text: ", sample["text"])

    s = ""
    for label in sample["label"]:
        s += f"{labels[label]} "

    print("Label: ", s)

def visualize_class_distribution(ds, index):
    count = []
    
    for x in ds[index]:
        for label in x["label"]:
            count.append(ds[3][label])
        
    counter = Counter(count)

    plt.figure(figsize=(22, 8))
    plt.bar(list(counter.keys()), list(counter.values()), color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Classes")
    plt.ylabel("Frequency")
    plt.title("Number of samples per class")
    plt.tight_layout()  
    plt.show()
        
def find_number_of_words_per_sample(ds: dict):
    for x in list(ds.keys())[:-1]:
        length_text = [len(y['text'].split(" ")) for y in ds[x]]
        median = np.median(length_text)
        percentile_95 = np.percentile(length_text, q=95)
        if x == 0:
            print(f"Median length in train ds: {median}")
            print(f"95% length in train ds: {percentile_95}")
        elif x == 1:
            print(f"Median length in test ds: {median}")
            print(f"95% length in test ds: {percentile_95}")
        if x == 2:
            print(f"Median length in dev ds: {median}")
            print(f"95% length in dev ds: {percentile_95}")

def preprocessing(ds: dict):
    
    for key in list(ds.keys())[:-1]:
        corpus = [x["text"] for x in ds[key]]
        stopword = set(stopwords.words('english')) 
        lemmatizer = nltk.WordNetLemmatizer()

        stopped_tokens = []

        for c in corpus:
            lower = c.lower()
            translation_table = str.maketrans('', '', string.punctuation)
            stripped = lower.translate(translation_table)
            tokens = stripped.split(" ")
            filtered_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stopword]
            stopped_tokens.append(filtered_tokens)
        
        if key == 0:
            sequence_length = find_sequence_length(stopped_tokens)

        tonkenized_corpus = [' '.join(token) for token in stopped_tokens]

        vectorizer = keras.layers.TextVectorization(
            max_tokens=MAX_TOKEN,
            output_mode="int",
            output_sequence_length=int(sequence_length),
            standardize=None
        )
        vectorizer.adapt(tonkenized_corpus)
        vocabulary = vectorizer.get_vocabulary()
        vectorized_text = vectorizer(tonkenized_corpus)
        
        for i in range(len(ds[key])):
            ds[key][i]["vectorized_text"] = vectorized_text[i]
        
        return vocabulary

def find_sequence_length(corpus):
    length_corpus = [len(c) for c in corpus]
    percentile_95 = np.percentile(length_corpus, 95)

    return percentile_95

def get_embedding_index(path_to_glove_file):
    embeddings_index = {}
    with open(path_to_glove_file) as f:
        for line in f:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            embeddings_index[word] = coefs
    
    return embeddings_index

def prepare_embedding_matrix(embedding_dim, vocabulary_length, word_index, embedding_index):
    hits = 0
    misses = 0

    # Prepare embedding matrix
    embedding_matrix = np.zeros((vocabulary_length, embedding_dim))
    for word, i in word_index.items():
        embedding_vector = embedding_index.get(word)
        if embedding_vector is not None:
            # Words not found in embedding index will be all-zeros.
            # This includes the representation for "padding" and "OOV"
            embedding_matrix[i] = embedding_vector
            hits += 1
        else:
            misses += 1
    print("Converted %d words (%d misses)" % (hits, misses))
    return embedding_matrix