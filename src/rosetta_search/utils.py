import json
import os
import fnmatch
import sqlite3
from urllib.request import pathname2url
import click
from git import Repo


def json_echo(dictionary):
    click.echo(json.dumps(dictionary, indent=2))


def normalise_paths(*paths):
    results = []
    for path in paths:
        if path is not None:
            results.append(os.path.normpath(path))
        else:
            results.append(path)
    return tuple(results)


def check_index_path(repo_path, index_path=None):
    if not index_path:
        index_path = look_for_existing_index(repo_path)
    if not index_path:
        raise click.UsageError("No existing index found. Use create to create an index.")
    try:
        check_db_path(index_path)
    except Exception:
        raise click.UsageError("Index path provided is not a valid Rosetta Index.")
    return index_path


def check_repo_path(repo_path):
    if repo_path is None:
        raise click.UsageError("No repo path provided")
    repo_obj = Repo(repo_path)
    if repo_obj.bare:
        raise click.UsageError(f"No git repo found at {repo_path}")


def look_for_existing_index(path):
    for root, dirs, files in os.walk(path):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.db"):
                return os.path.join(root, filename)


def check_db_path(db_path):
    try:
        database_uri = f"file:{pathname2url(db_path)}?mode=rw"
        conn = sqlite3.connect(database_uri, uri=True)
    except sqlite3.OperationalError:
        raise Exception(f"{db_path} is not a valid Rosetta index.")
