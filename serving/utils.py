import mlflow   
import nltk 
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import stopwords


def make_prediction(input, registered_model: str, tracking_uri: str = "http://localhost:5000"):

    mlflow.set_tracking_uri(tracking_uri)
    loaded_model = mlflow.pyfunc.load_model(registered_model)

    y_pred = loaded_model.predict(input.numpy().reshape(-1, len(input)))

    return y_pred

def preprocess(raw_data: str):
    '''
    Preprocessing training data with the following steps:
        - Remove extra space
        - Tokenize into single word (Sequence tokenization)
        - Remove stop word
        - Lemmatize 
    '''

    stopword = set(stopwords.words("english"))
    lemmatizer = nltk.WordNetLemmatizer()

    # Remove extra space
    stripped_x = " ".join(raw_data.split())

    # Word tokenization
    tokenized_x = stripped_x.split(" ")

    # Lemmatize + remove stopped words
    filtered_x = [lemmatizer.lemmatize(token) for token in tokenized_x if token not in stopword]
    
    return ' '.join(filtered_x)
