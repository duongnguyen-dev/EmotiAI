import nltk 
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import stopwords

def preprocess_features(raw_data: list[str]):
    '''
    Preprocessing training data with the following steps:
        - Remove extra space
        - Tokenize into single word (Sequence tokenization)
        - Remove stop word
        - Lemmatize 
    '''

    stopword = set(stopwords.words("english"))
    lemmatizer = nltk.WordNetLemmatizer()

    preprocessed_data = []
    # Process features
    for x in raw_data:
        # Remove extra space
        stripped_x = " ".join(x.split())

        # Word tokenization
        tokenized_x = stripped_x.split(" ")

        # Lemmatize + remove stopped words
        filtered_x = [lemmatizer.lemmatize(token) for token in tokenized_x if token not in stopword]
        preprocessed_data.append(filtered_x)
    
    return [' '.join(i) for i in preprocessed_data]

def preprocess_labels(encoder, key: str, value: list[list[int]]):
    """ 
        Use MultilabelBinarizer to encode label for each sample
    """
    # Process labels
    if key == "train":
        preprocessed_labels = encoder.fit_transform(value)
    else:
        preprocessed_labels = encoder.transform(value)

    return preprocessed_labels