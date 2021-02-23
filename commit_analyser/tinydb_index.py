from git import Repo
from tinydb import TinyDB, Query
from nltk import word_tokenize
from tqdm import tqdm
import time


class Index:
    def __init__(self, repo_path):
        self.repo_stub = repo_path.rsplit('/', 1)[-1]
        self.repo_path = repo_path
        self.repo_obj = Repo(repo_path)
        self.stats = {}

        self.db = TinyDB(self.repo_stub + '_db.json')

        if not self.repo_obj.bare and self.db:
            self.build_index()

    def build_index(self):
        print("Started indexing for " + self.repo_stub)
        start_time = time.time()
        self.stats["last_updated"] = start_time
        num_commits = 0
        for commit in tqdm(self.repo_obj.iter_commits()):
            num_commits += 1
            self.stats["last_indexed_commit"] = commit.hexsha
            self.db.upsert({'last_indexed_commit': commit.hexsha})
            for file in commit.stats.files.keys():
                self.add(commit.message, file)
        self.stats["initial_build_time"] = time.time() - start_time
        print("Initial indexing complete. \n {} commits indexed in {} minutes".format(num_commits,
                                                                                      self.stats["initial_build_time"]))

    def update_index(self):
        rev_list_arg = '{}..HEAD'.format(self.stats["last_indexed_commit"])
        num_commits = 0
        for commit in tqdm(self.repo_obj.iter_commits(rev_list_arg)):
            num_commits += 1
            self.stats["last_indexed_commit"] = commit.hexsha
            for file in commit.stats.files.keys():
                self.add(commit.message, file)
        print("{} new commits indexed in {} seconds".format(num_commits, time.time() - self.stats["last_updated"]))
        self.stats["last_updated"] = time.time()

    def add(self, message, file):
        tokens = word_tokenize(message)
        for token in tokens:
            try:
                self.index[token].add(file)
            except KeyError:
                self.index[token] = {file}

    def search(self, query):
        lemma = Word(query).lemmatize()
        try:
            return self.index[lemma]
        except KeyError:
            return "No results found"

    def save_index(self, filepath):
        with open(filepath, "wb") as file:
            pickle.dump(self, file)
