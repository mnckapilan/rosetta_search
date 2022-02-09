import math
import sqlite3
from uuid import uuid4

from git import Commit


def uuid():
    return str(uuid4())


class Database:
    def __init__(self, db_path):
        self.db_location = db_path
        if self.db_is_empty() or self.index_is_empty():
            self.create_tables()

    def db_is_empty(self):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        tables = cur.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'commits'").fetchall()

        con.commit()
        con.close()

        if not tables:
            return True
        else:
            return False

    def index_is_empty(self):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        count = cur.execute("SELECT COUNT(*) FROM commits").fetchone()[0]

        con.commit()
        con.close()

        if count == 0:
            return True
        else:
            return False

    def insert_into_commits(self, commit: Commit, message: str):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        sql = "INSERT INTO commits " \
              "(hash, datetime, message, author, additions, deletions)" \
              "VALUES (?,?,?,?,?,?)"

        commit_hash = commit.hexsha
        datetime = commit.committed_datetime.isoformat()
        message = message
        author = commit.author.name
        additions = commit.stats.total['insertions']
        deletions = commit.stats.total['deletions']

        values = (commit_hash, datetime, message, author, additions, deletions)

        cur.execute(sql, values)

        con.commit()
        con.close()

    def insert_into_tokens_files(self, commit: Commit, tokens: list[str]):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        files_sql = "INSERT OR IGNORE INTO files " \
                    "(file_id, filepath)" \
                    "VALUES (?,?)"

        file_list = list(commit.stats.files.keys())
        files_values = [(uuid(), filepath) for filepath in file_list]
        cur.executemany(files_sql, files_values)

        file_ids = cur.execute(
            "SELECT file_id FROM files WHERE filepath in ({0})".format(', '.join('?' for _ in file_list)),
            file_list).fetchall()

        tokens_sql = "INSERT OR IGNORE INTO tokens " \
                     "(token_id, token_string)" \
                     "VALUES (?,?)"

        tokens_values = [(uuid(), token) for token in tokens]
        cur.executemany(tokens_sql, tokens_values)

        token_ids = cur.execute(
            "SELECT token_id FROM tokens WHERE token_string in ({0})".format(', '.join('?' for _ in tokens)),
            tokens).fetchall()

        tokens_files_values = [(uuid(), token_id[0], file_id[0]) for token_id in token_ids for file_id in file_ids]
        cur.executemany("INSERT INTO tokens_files (token_file_id, token_id, file_id) VALUES (?,?,?)",
                        tokens_files_values)

        commits_files_values = [(uuid(), commit.hexsha, file_id[0]) for file_id in file_ids]
        cur.executemany("INSERT INTO commits_files (commit_file_id, commit_hash, file_id) VALUES (?,?,?)",
                        commits_files_values)

        con.commit()
        con.close()

    def meta_update(self, start_time, end_time, start_rev, end_rev, number_of_commits):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        sql = "INSERT INTO updates " \
              "(update_id, start_time, end_time, start_rev, end_rev, number_of_commits) " \
              "VALUES (?,?,?,?,?,?)"

        values = (uuid(), start_time.isoformat(), end_time.isoformat(), start_rev, end_rev, number_of_commits)

        cur.execute(sql, values)

        con.commit()
        con.close()

    def create_tables(self):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS commits ("
                    "hash BLOB PRIMARY KEY, "
                    "datetime TEXT, "
                    "message TEXT, "
                    "author TEXT,"
                    "additions INTEGER,"
                    "deletions INTEGER"
                    ")")

        cur.execute("CREATE TABLE IF NOT EXISTS tokens ("
                    "token_id BLOB PRIMARY KEY,"
                    "token_string TEXT UNIQUE "
                    ")")

        cur.execute("CREATE TABLE IF NOT EXISTS files ("
                    "file_id BLOB PRIMARY KEY,"
                    "filepath TEXT UNIQUE"
                    ")")

        cur.execute("CREATE TABLE IF NOT EXISTS tokens_files ("
                    "token_file_id BLOB PRIMARY KEY,"
                    "token_id BLOB,"
                    "file_id BLOB,"
                    "tf_idf_score REAL,"
                    "FOREIGN KEY(token_id) REFERENCES tokens(token_id),"
                    "FOREIGN KEY (file_id) REFERENCES files(file_id)"
                    ")")

        cur.execute("CREATE TABLE IF NOT EXISTS commits_files ("
                    "commit_file_id BLOB PRIMARY KEY,"
                    "commit_hash BLOB,"
                    "file_id BLOB,"
                    "FOREIGN KEY(commit_hash) REFERENCES commits(hash),"
                    "FOREIGN KEY (file_id) REFERENCES  files(file_id)"
                    ")")

        cur.execute("CREATE TABLE IF NOT EXISTS updates ("
                    "update_id BLOB PRIMARY KEY,"
                    "start_time TEXT,"
                    "end_time TEXT,"
                    "start_rev TEXT,"
                    "end_rev TEXT,"
                    "number_of_commits INTEGER"
                    ")")

        con.commit()
        con.close()

    def get_last_indexed_rev(self):
        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        row = cur.execute("SELECT end_rev FROM updates ORDER BY end_time LIMIT 1").fetchone()

        con.commit()
        con.close()

        if row is not None:
            last_rev = row["end_rev"]
        else:
            last_rev = None

        return last_rev

    def get_last_updated(self):
        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        row = cur.execute("SELECT end_time FROM updates ORDER BY end_time LIMIT 1").fetchone()
        if row is not None:
            last_updated = row["end_time"]
        else:
            last_update = None

        con.commit()
        con.close()

    def get_files_for_token(self, token: str) -> list[(str, float)]:
        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        rows = cur.execute(
            "SELECT f.filepath, tf.file_id, tf.token_id "
            "FROM tokens "
            "JOIN tokens_files tf "
            "ON tokens.token_id = tf.token_id "
            "JOIN files f "
            "ON tf.file_id = f.file_id "
            "WHERE token_string like :query "
            "GROUP BY f.filepath",
            {"query": token}).fetchall()

        con.commit()
        con.close()

        files: list[(str, float)] = []
        for row in rows:
            tf_idf_score = self.get_tf_idf_for_token_file(row['token_id'], row['file_id'])
            files.append((row['filepath'], tf_idf_score))
        return files

    def get_all_commits(self):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()

        commit_messages = cur.execute("SELECT message from commits")

        con.commit()
        con.close()

        return commit_messages

    def get_all_tokens(self) -> list[(str, str)]:
        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        rows = cur.execute("SELECT token_id, token_string FROM tokens")
        result = []
        for row in rows:
            result.append((row["token_id"], row["token_string"]))

        con.commit()
        con.close()

        return result

    def get_tf_idf_for_token_file(self, token_id, file_id):
        tf_idf_query = '''
                 WITH tf(tf) as (SELECT COUNT(token_id) as tf
                         from tokens_files
                         WHERE token_id = :token_id
                           and file_id = :file_id ),
              df(df) as (
                  SELECT COUNT(*) as document_freq
                  from (SELECT 0 as df
                        from tokens_files
                        WHERE token_id = :token_id
                        GROUP BY file_id)),
              n(n) as (SELECT COUNT(file_id) as number
                       from files)
         SELECT ((SELECT tf from tf) * (log((SELECT n from n) / ((SELECT df from df) + 1)))) as tfidf

                 '''

        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        con.create_function('log', 1, math.log2)
        cur = con.cursor()

        returned_rows = cur.execute(tf_idf_query,
                                    {"token_id": token_id, "file_id": file_id}).fetchall()
        tf_idf_score = [d['tfidf'] for d in returned_rows][0]
        con.commit()
        con.close()
        return tf_idf_score

    def update_all_tf_idf(self):

        tf_idf_query = '''
                WITH tf(tf) as (SELECT COUNT(token_id) as tf
                        from tokens_files
                        WHERE token_id = :token_id
                          and file_id = :file_id ),
             df(df) as (
                 SELECT COUNT(*) as document_freq
                 from (SELECT 0 as df
                       from tokens_files
                       WHERE token_id = :token_id
                       GROUP BY file_id)),
             n(n) as (SELECT COUNT(file_id) as number
                      from files)
        SELECT ((SELECT tf from tf) * (log((SELECT n from n) / ((SELECT df from df) + 1)))) as tfidf

                '''

        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        con.create_function('log', 1, math.log2)
        cur = con.cursor()

        rows = cur.execute("SELECT token_file_id, token_id, file_id from tokens_files").fetchall()

        for row in rows:
            returned_rows = cur.execute(tf_idf_query,
                                        {"token_id": row["token_id"], "file_id": row["file_id"]}).fetchall()
            tf_idf_score = [d['tfidf'] for d in returned_rows][0]
            cur.execute("UPDATE tokens_files SET tf_idf_score = :tf_idf WHERE token_file_id = :token_file_id",
                        {"tf_idf": tf_idf_score, "token_file_id": row["token_file_id"]})
            con.commit()
        con.close()

    def get_vocab_size(self):
        con = sqlite3.connect(self.db_location)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        row = cur.execute("SELECT COUNT(*) as vocab_size FROM main.tokens").fetchone()
        return row["vocab_size"]
