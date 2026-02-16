import click
from manager import WitManager

wit = WitManager()

@click.group()
def cli():
    pass

@cli.command()
def init():
    wit.init()

@cli.command()
@click.argument('path')
def add(path):
    wit.add(path)

@cli.command()
@click.option('-m', '--message', required=True)
def commit(message):
    wit.commit(message)

@cli.command()
def status():
    wit.status()

@cli.command()
@click.argument('commit_id')
def checkout(commit_id):
    wit.checkout(commit_id)

if __name__ == "__main__":
    cli()