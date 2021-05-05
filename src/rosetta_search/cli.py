import click

from .rosetta_index import RosettaIndex
from .utils import check_repo_path, normalise_paths, check_index_path, json_echo


class Context:
    def __init__(self):
        self.repo_path = None
        self.index_path = None
        self.json_mode = False


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option('--json-mode', is_flag=True)
@click.argument('repo-path', type=click.Path())
@click.option('--index-path', type=click.Path())
@pass_context
def rosetta(ctx, json_mode, repo_path, index_path):
    ctx.json_mode = json_mode
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
    if ctx.json_mode:
        json_echo({"status": "success", "last_update_time": f"{last_updated}"})
    else:
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
    results = index.search_index(query)
    if ctx.json_mode:
        json_echo({"status": "success", "results": results})
    else:
        click.echo(results)


if __name__ == '__main__':
    rosetta()
