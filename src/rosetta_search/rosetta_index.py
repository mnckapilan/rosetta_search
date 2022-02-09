import itertools
import operator
from datetime import datetime
from pathlib import Path

from git import Repo
from tqdm import tqdm

from rosetta_search.database import Database
from rosetta_search.file_result import FileResult
from rosetta_search.nlp_utils import preprocess_message, tokenize_and_clean
from rosetta_search.similarity_result import SimilarityResult


class RosettaIndex:
    def __init__(self, repo_path, db_path):
        self.repo_obj = Repo(repo_path)
        self.database = Database(db_path)

    @classmethod
    def create_new_index(cls, repo_path, db_path=None, tqdm_disable=True):
        if db_path is None:
            db_path = Path(repo_path) / 'rosetta_index.db'

        index = RosettaIndex(repo_path, db_path)
        num_commits, build_time, vocab_size = index.build_index(tqdm_disable)
        return index, num_commits, build_time, vocab_size

    def build_index(self, tqdm_disable=True):
        start_time = datetime.now()
        num_commits = 0
        for commit in tqdm(self.repo_obj.iter_commits(), disable=tqdm_disable):
            start_rev = commit.hexsha
            num_commits += 1
            tokens, message = preprocess_message(commit.message)
            self.database.insert_into_commits(commit, message)
            self.database.insert_into_tokens_files(commit, tokens)
        # self.update_tf_idf()
        end_rev = self.repo_obj.head.commit.hexsha
        end_time = datetime.now()
        self.database.meta_update(start_time, end_time, start_rev, end_rev, num_commits)
        vocab_size = self.database.get_vocab_size()
        return num_commits, (end_time - start_time).total_seconds(), vocab_size

    def update_index(self):
        if self.database.get_last_indexed_rev() is None:
            pass
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
        # if num_commits > 0:
        # self.update_tf_idf()
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
        file_set = {}

        for query_token in tokenize_and_clean(query):
            similar_list: list[SimilarityResult] = self.get_similar_list(query_token)
            for similarity_result in similar_list[:n]:
                matched_token = similarity_result.matched_token
                similarity = similarity_result.similarity
                files_and_scores: list[(str, float)] = self.database.get_files_for_token(matched_token)
                for (filepath, tf_idf) in files_and_scores:
                    if filepath not in file_set:
                        file_set[filepath] = FileResult(filepath)
                    file_set[filepath].add_matched_token(matched_token, tf_idf, similarity)
                    file_set[filepath].add_query_token(query_token)

        results = dict(sorted(file_set.items(), key=operator.itemgetter(1), reverse=True))
        return dict(itertools.islice(results.items(), 20))

    def update_tf_idf(self):
        self.database.update_all_tf_idf()
