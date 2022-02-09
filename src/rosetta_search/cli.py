import click

from rosetta_search.rosetta_index import RosettaIndex
from rosetta_search.utils import check_repo_path, normalise_paths, check_index_path, json_echo


class Context:
    def __init__(self):
        self.repo_path = None
        self.index_path = None
        self.json_mode = False

    def set_paths(self, repo_path, index_path=None):
        repo_path, index_path = normalise_paths(repo_path, index_path)
        check_repo_path(repo_path)
        index_path = check_index_path(repo_path, index_path)
        self.repo_path = repo_path
        self.index_path = index_path


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option('--json-mode', is_flag=True)
@click.option('--repo-path', type=click.Path())
@click.option('--index-path', type=click.Path())
@pass_context
def rosetta(ctx, json_mode, repo_path, index_path):
    ctx.json_mode = json_mode
    ctx.set_paths(repo_path, index_path)


@rosetta.command()
@click.option('--update/--noupdate', default=False)
@pass_context
def load(ctx, update):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)
    last_updated = index.get_last_updated()
    if last_updated is None:
        last_updated = "never"
    if ctx.json_mode:
        json_echo({"status": "success", "last_update_time": f"{last_updated}"})
    else:
        click.echo(f"Index last updated at {last_updated}")


@rosetta.command()
@pass_context
def update(ctx):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)
    last_updated = index.get_last_updated()
    if last_updated is None:
        last_updated = "never"
    click.echo(f"Most recent update was at {last_updated}")
    num_of_commits, last_updated = index.update_index()
    click.echo(f"{num_of_commits} new commits indexed successfully.")


@rosetta.command()
@click.option('--basic-search', type=click.STRING)
@pass_context
def basic_search(ctx, query):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)
    results = index.basic_search(query)
    if ctx.json_mode:
        json_echo({"status": "success", "results": results})
    else:
        click.echo(results)


@rosetta.command()
@click.option('--query', type=click.STRING)
@click.option('--top-n', type=click.INT)
@pass_context
def search(ctx, query, top_n):
    index = RosettaIndex(ctx.repo_path, ctx.index_path)

    if top_n is None:
        results = index.similarity_search_index(query)
    else:
        results = index.similarity_search_index(query, top_n)

    if ctx.json_mode:
        json_echo({"status": "success", "results": results})
    else:
        click.echo(list(results.keys()))


@rosetta.command()
@click.option('--overwrite', is_flag=True)
@pass_context
def create(ctx, overwrite):
    if not ctx.json_mode:
        click.echo(f"Building index...")

    index, num_commits, build_time, vocab_size = RosettaIndex.create_new_index(ctx.repo_path, ctx.index_path,
                                                                               tqdm_disable=ctx.json_mode)
    if ctx.json_mode:
        json_echo(
            {"status": "success", "number_of_commits": num_commits, "build_time": build_time, "vocab_size": vocab_size})


if __name__ == '__main__':
    rosetta()
