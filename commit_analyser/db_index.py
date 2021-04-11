import pickle
import os
import time
from git import Repo
from tqdm import tqdm
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def preprocess_message(message):
    stop_words = stopwords.words('english')
    tokens = word_tokenize(message)
    tokens = [word.lower() for word in tokens if word not in stop_words and word.isalpha()]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens, ' '.join(tokens)


class DbIndex:
    def __init__(self, repo_path):
        self.repo_path = os.path.normpath(repo_path)
        self.repo_stub = os.path.basename(self.repo_path)
        self.repo_obj = Repo(repo_path)
        self.db_location = self.repo_path + '/semantic_search.db'
        self.index = {}
        self.stats = {}
        self.file_to_messages = {}
        self.message_index = {}
        if not self.repo_obj.bare:
            self.build_index()

    @classmethod
    def load_index(cls, filepath):
        with open(filepath, "rb") as file:
            return pickle.load(file)

    def build_index(self):
        print("Started indexing for " + self.repo_stub)
        start_time = time.time()
        self.stats["last_updated"] = start_time
        num_commits = 0
        for commit in tqdm(self.repo_obj.iter_commits()):
            num_commits += 1
            tokens, message = preprocess_message(commit.message)
            # Store hash -> processed message
            self.message_index[commit.hexsha] = message
            for file in commit.stats.files.keys():
                self.add(tokens, file)
                try:
                    self.file_to_messages[file] += ' ' + message
                except KeyError:
                    self.file_to_messages[file] = message
        self.stats["initial_build_time"] = time.time() - start_time
        self.stats["last_indexed_commit"] = self.repo_obj.head.commit.hexsha
        print("Initial indexing complete. \n {} commits indexed in {} seconds".format(num_commits,
                                                                                      self.stats["initial_build_time"]))

    def update_index(self):
        self.stats["last_updated"] = time.time()
        rev_list_arg = '{}..HEAD'.format(self.stats["last_indexed_commit"])
        num_commits = 0
        for commit in tqdm(self.repo_obj.iter_commits(rev_list_arg)):
            num_commits += 1
            tokens, message = preprocess_message(commit.message)
            self.message_index[commit.hexsha] = message
            for file in commit.stats.files.keys():
                self.add(tokens, file)
        print("{} new commits indexed in {} seconds".format(num_commits, time.time() - self.stats["last_updated"]))
        self.stats["last_indexed_commit"] = self.repo_obj.head.commit.hexsha

    def add(self, tokens, file):
        for token in tokens:
            try:
                self.index[token].add(file)
            except KeyError:
                self.index[token] = {file}


def search(self, query):
    try:
        tokens, message = preprocess_message(query)
    except KeyError:
        return "No results found"


def save_index(self, filepath):
    with open(filepath, "wb") as file:
        pickle.dump(self, file)
