from nltk import word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords


def preprocess_message(message):
    stop_words = stopwords.words('english')
    tokens = word_tokenize(message)
    tokens = [word.lower() for word in tokens if word not in stop_words and word.isalpha()]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens, ' '.join(tokens)
