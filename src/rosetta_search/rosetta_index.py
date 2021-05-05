from datetime import datetime
from git import Repo
from .database import Database
from .nlp_utils import preprocess_message


class RosettaIndex:
    def __init__(self, repo_path, db_path=None):
        self.repo_obj = Repo(repo_path)
        self.database = Database(db_path)
        if self.database.index_is_empty():
            raise Exception("Index is empty")

    def build_index(self):
        start_time = datetime.now()
        num_commits = 0
        for commit in self.repo_obj.iter_commits():
            start_rev = commit.hexsha
            num_commits += 1
            tokens, message = preprocess_message(commit.message)
            self.database.insert_into_commits(commit, message)
            self.database.insert_into_tokens_files(commit, tokens)
        end_rev = self.repo_obj.head.commit.hexsha
        end_time = datetime.now()
        self.database.meta_update(start_time, end_time, start_rev, end_rev, num_commits)
        print("Initial indexing complete. \n {} commits indexed in {} seconds".format(num_commits, (
                end_time - start_time).total_seconds()))

    def update_index(self):
        rev_list_arg = '{}..HEAD'.format(self.database.get_last_indexed_rev())
        start_time = datetime.now()
        num_commits = 0
        start_rev = None
        for commit in self.repo_obj.iter_commits(rev_list_arg):
            start_rev = commit.hexsha
            num_commits += 1
            tokens, message = preprocess_message(commit.message)
            self.database.insert_into_commits(commit, message)
            self.database.insert_into_tokens_files(commit, tokens)
        end_rev = self.repo_obj.head.commit.hexsha
        end_time = datetime.now()
        if start_rev is not None:
            self.database.meta_update(start_time, end_time, start_rev, end_rev, num_commits)
        return num_commits, end_time

    def search_index(self, query):
        return self.database.search(query)

    def get_last_updated(self):
        return self.database.get_last_updated()
