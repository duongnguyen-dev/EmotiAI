import nltk 
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import stopwords

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
