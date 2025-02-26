import nltk
import keras
import string
nltk.download('wordnet')
nltk.download('stopwords')

from loguru import logger
from nltk.corpus import stopwords
from src.dataset.base import BaseDataset
from src.dataset.config import DatasetConfig
from sklearn.preprocessing import MultiLabelBinarizer

class GoEmotionDataset(BaseDataset):
    def __init__(self, dataset_path: str):
        super().__init__()

        # Init variables
        self.stopword = set(stopwords.words('english')) 
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.mlb = MultiLabelBinarizer()
        self.vectorizer = keras.layers.TextVectorization(
            max_tokens=DatasetConfig.MAX_TOKEN,
            output_mode="int",
            output_sequence_length=int(DatasetConfig.SEQUENCE_LENGTH),
            standardize=None
        )

        self._dataset_path = dataset_path

        self._dataset_types = ["train", "test", "dev"]

        self._label_dict = {}

        self._raw_data = {key : None for key in self._dataset_types}

        # Fully prepared dataset pipeline
        self._load_labels_dict()
        self._load_raw_dataset()
        self._ds, self._vocabulary = self._preprocessing()
        
    def _preprocessing(self):
        '''
        Preprocessing training data with the following steps:
        1, Features:
            - Lower text
            - Strip punctuation
            - Tokenize into single word (Sequence tokenization)
            - Remove stop word
            - Lemmatize 
        2, Label: 
            - Use MultilabelBinarizer to encode label for each sample
        '''
        
        # 1, Process features
        ds = {x : {} for x in self._dataset_types}
        
        for key, samples in self._raw_data.items():
            X = [sample["text"] for sample in samples]
            y = [sample["label"] for sample in samples]
            
            stopped_x = []

            for x in X:
                lowered_x = x.lower()
                translated_table = str.maketrans('', '', string.punctuation)
                stripped_x = lowered_x.translate(translated_table)
                tokenized_x = stripped_x.split(" ")
                filtered_tokenized_x = [self.lemmatizer.lemmatize(token) for token in tokenized_x if token not in self.stopword]
                stopped_x.append(filtered_tokenized_x)

            preprocessed_data = [' '.join(token) for token in stopped_x]

            if key == "train":
                self.vectorizer.adapt(preprocessed_data)
                vocabulary = self.vectorizer.get_vocabulary()

            vectorized_text = self.vectorizer(preprocessed_data)

            ds[key]["features"] = vectorized_text
        
            # 2, Process label
            if key == "train":
                ds[key]["labels"] = self.mlb.fit_transform(y)
            else:
                ds[key]["labels"] = self.mlb.transform(y)
        
        return ds, vocabulary

    def _load_labels_dict(self):
        try:
            with open(self._dataset_path + "/labels.txt", 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    self._label_dict[i] = line.replace("\n", "")
                logger.info(f"Loading labels successfully. There are {len(self._label_dict)} in total.")
        except FileNotFoundError as e:
            logger.error(e)

    def _load_raw_dataset(self):
        try:
            for ds in self._dataset_types:
                df = []
                with open(self._dataset_path + f"/{ds}.tsv", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for (i, line) in enumerate(lines):
                        line = line.strip()
                        items = line.split("\t")
                        text_a = items[0]
                        label = list(map(int, items[1].split(",")))
                        df.append({
                            "text": text_a, 
                            "label": label
                        })
                logger.info(f"Load {ds} dataset successfully")
                self._raw_data[ds] = df

        except FileNotFoundError as e:
            logger.error(e)
    
    def get_raw_dataset(self, type: str):
        '''
        This method is used to get raw dataset.
        Args:
            type: Only accept "train", "test" or "dev".
        '''

        if type not in self._dataset_types:
            logger.error(f'Unable to get raw dataset of type {type}. Only accept "train", "test" or "dev"')

        return self._raw_data[type]

    def get_preprocessed_data(self, type):
        '''
        This method is used to get preprocessed dataset.
        Args:
            type: Only accept "train", "test" or "dev".
        '''
        if type not in self._dataset_types:
            logger.error(f'Unable to get raw dataset of type {type}. Only accept "train", "test" or "dev"')

        return self._ds[type]

    def get_vocabulary(self):
        return self._vocabulary
    
    def get_vocabulary_length(self):
        return len(self._vocabulary)