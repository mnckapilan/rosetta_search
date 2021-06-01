from datetime import datetime
from pathlib import Path

import click
from git import Repo

from rosetta_search.database import Database
from rosetta_search.nlp_server import get_similarities
from rosetta_search.nlp_utils import preprocess_message


class RosettaIndex:
    def __init__(self, repo_path, db_path):
        self.repo_obj = Repo(repo_path)
        self.database = Database(db_path)

    @classmethod
    def create_new_index(cls, repo_path, db_path=None):
        if db_path is None:
            db_path = Path(repo_path) / 'rosetta_index.db'

        index = RosettaIndex(repo_path, db_path)
        click.echo("Building your new index...")
        num_commits, build_time = index.build_index()
        click.echo("Index built!")
        return index, num_commits, build_time

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
        return num_commits, (end_time - start_time).total_seconds()

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

    def basic_search(self, query):
        return self.database.get_files_for_token(query)

    def get_last_updated(self):
        return self.database.get_last_updated()

    def similarity_search_index(self, query):
        all_ids, all_tokens = self.database.get_all_tokens()
        tokens = []
        for uuid, token in zip(all_ids, all_tokens):
            token = {"uuid": uuid, "token": token, "scores": get_similarities(token, query)}
            tokens.append(token)
        tokens = sorted(tokens, key=lambda x: x["scores"]["fasttext_similarity"], reverse=True)
        files = {}
        n = 5
        for tkn_obj in tokens[:n]:
            token = tkn_obj["token"]
            filepaths = self.database.get_files_for_token(token)
            for filepath in filepaths:
                try:
                    files[filepath].append(token)
                except KeyError:
                    files[filepath] = [token]
        return files
