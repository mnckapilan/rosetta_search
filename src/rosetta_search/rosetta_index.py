import operator
from datetime import datetime
from pathlib import Path

import click
from git import Repo

from rosetta_search.database import Database
from rosetta_search.file_result import FileResult
from rosetta_search.nlp_utils import preprocess_message
from rosetta_search.similarity_result import SimilarityResult


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
        self.update_tf_idf()
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
        self.update_tf_idf()
        end_rev = self.repo_obj.head.commit.hexsha
        end_time = datetime.now()
        if start_rev is not None:
            self.database.meta_update(start_time, end_time, start_rev, end_rev, num_commits)
        return num_commits, end_time

    def basic_search(self, query):
        return self.database.get_files_for_token(query)

    def get_last_updated(self):
        return self.database.get_last_updated()

    def get_similar_list(self, query_token) -> list[SimilarityResult]:
        similar_set: list[SimilarityResult] = []
        for matched_token_id, matched_token in self.database.get_all_tokens():
            similar_set.append(SimilarityResult(query_token, matched_token, matched_token_id))
        return sorted(similar_set, key=operator.attrgetter('similarity'), reverse=True)

    def similarity_search_index(self, query: str, n=3):
        file_set: dict[str, FileResult] = {}

        for query_token in query.split():
            similar_list: list[SimilarityResult] = self.get_similar_list(query_token)
            for similarity_result in similar_list[:n]:
                matched_token = similarity_result.matched_token
                files_and_scores: list[(str, float)] = self.database.get_files_for_token(matched_token)
                for (filepath, tf_idf) in files_and_scores:
                    if filepath not in file_set:
                        file_set[filepath] = FileResult(filepath)
                    file_set[filepath].add_matched_token(matched_token, tf_idf)
                    file_set[filepath].add_query_token(query_token)

        return sorted(file_set.items(), key=lambda item: item[1], reverse=True)[:10]

    def update_tf_idf(self):
        self.database.update_all_tf_idf()
