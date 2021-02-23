from git import Repo
import pickle
from tqdm import tqdm
import time
import spacy

nlp = spacy.load('en_core_web_sm')


class Index:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo_stub = repo_path.rsplit('/', 1)[-1]
        self.repo_obj = Repo(repo_path)
        self.index = {}
        self.stats = {}
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
            self.stats["last_indexed_commit"] = commit.hexsha
            tokens = process_message(commit.message)
            for file in commit.stats.files.keys():
                self.add(tokens, file)
        self.stats["initial_build_time"] = time.time() - start_time
        print("Initial indexing complete. \n {} commits indexed in {} seconds".format(num_commits,
                                                                                      self.stats["initial_build_time"]))

    def update_index(self):
        rev_list_arg = '{}..HEAD'.format(self.stats["last_indexed_commit"])
        num_commits = 0
        for commit in tqdm(self.repo_obj.iter_commits(rev_list_arg)):
            num_commits += 1
            self.stats["last_indexed_commit"] = commit.hexsha
            tokens = process_message(commit.message)
            for file in commit.stats.files.keys():
                self.add(tokens, file)
        print("{} new commits indexed in {} seconds".format(num_commits, time.time() - self.stats["last_updated"]))
        self.stats["last_updated"] = time.time()

    def add(self, tokens, file):
        for token in tokens:
            try:
                self.index[token].add(file)
            except KeyError:
                self.index[token] = {file}

    def search(self, query):
        lemmas = process_query(query)
        doc = nlp(lemmas)
        results = []
        for word in lemmas:
            try:
                results.append(self.index[word])
            except KeyError:
                results.append("empty")
        return results

    def save_index(self, filepath):
        with open(filepath, "wb") as file:
            pickle.dump(self, file)


def process_message(message):
    doc = nlp(message)
    lemmas = []
    for token in doc:
        if not token.is_stop:
            lemmas.append(token.lemma_)
    return lemmas


def useful_token(token):
    return True


def process_query(query):
    doc = nlp(query)
    lemmas = []
    for token in doc:
        if not token.is_stop:
            lemmas.append(token.lemma_)
    return lemmas
