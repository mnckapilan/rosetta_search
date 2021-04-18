import sqlite3
from uuid import uuid4


def uuid():
    return str(uuid4())


class Database:
    def __init__(self, repo_path):
        self.db_location = repo_path + '/src.db'

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

    def insert_into_commits(self, commit, message):
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

    def insert_into_tokens_files(self, commit, tokens):
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

    def create_db_tables(self):
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
        cur = con.cursor()

        last_rev = cur.execute("SELECT end_rev FROM updates ORDER BY end_time LIMIT 1").fetchone()[0]

        con.commit()
        con.close()

        return last_rev

    def update_tfidf(self):
        con = sqlite3.connect(self.db_location)
        cur = con.cursor()
