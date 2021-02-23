from time import time  # To time our operations
import re
from gensim.parsing.preprocessing import remove_stopwords
import sys
import spacy

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])


def remove_puncts(s):
    return re.sub(r'[^\w\s]', " ", s)


def lemmatize(s):
    chunks = s.split(" ")
    doc = nlp(s)
    return " ".join([token.lemma_ for token in doc])


def remove_newlines(s):
    clean = s.replace('\n', " ")


def remove_number_strings(s):
    return re.sub(r'\w*\d\w*', " ", s).strip()


def remove_duplicate_whitespaces(s):
    return re.sub("\s\s+", " ", s)


def lowercase_all(s):
    return s.lower()


def word_count(s):
    return len(s.split())


def preprocess(data):
    data = remove_puncts(data)
    data = remove_number_strings(data)
    data = remove_duplicate_whitespaces(data)
    data = lowercase_all(data)
    data = remove_stopwords(data)
    data = lemmatize(data)
    return data


t = time()
filepath = sys.argv[1]
file = open(filepath, 'rt')
text = file.read()
file.close()

new_text = preprocess(text)

text_file = open(filepath + "_lemmatized", "w")
text_file.write(new_text)
text_file.close()
print('Time taken: {} mins'.format(round((time() - t) / 60, 2)))
