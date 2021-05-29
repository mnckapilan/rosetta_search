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
        click.echo("No existing index found.")
        return None
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