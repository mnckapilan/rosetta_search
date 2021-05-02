import click

from .rosetta_index import RosettaIndex
from .utils import check_repo_path, normalise_paths, check_index_path


class Context:
    def __init__(self):
        self.repo_path = None
        self.index_path = None


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.argument('repo-path', type=click.Path())
@click.option('--index-path', type=click.Path())
@pass_context
def rosetta(ctx, repo_path, index_path):
    repo_path, index_path = normalise_paths(repo_path, index_path)
    check_repo_path(repo_path)
    index_path = check_index_path(repo_path, index_path)
    ctx.repo_path = repo_path
    ctx.index_path = index_path


@rosetta.command()
@click.option('--update/--noupdate', default=False)
@pass_context
def load(ctx, update):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)
    last_updated = index.get_last_updated()
    click.echo(f"Index last updated at {last_updated}")


@rosetta.command()
@pass_context
def update(ctx):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)
    last_updated = index.get_last_updated()
    click.echo(f"Most recent update was at {last_updated}")
    num_of_commits, last_updated = index.update_index()
    click.echo(f"{num_of_commits} new commits indexed successfully.")


@rosetta.command()
@click.option('--query', type=click.STRING)
@pass_context
def search(ctx, query):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)
    click.echo(index.search_index(query))
