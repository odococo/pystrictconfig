import shutil

import click
from bumpver.cli import update
from build.__main__ import main as build
from twine.commands.check import main as check
from twine.commands.upload import main as upload


@click.command()
@click.option('-u', '--username', prompt=True, envvar='TWINE_USERNAME')
@click.option('-p', '--password', prompt=True, envvar='TWINE_PASSWORD')
@click.option('--to-pypi/--no-to-pypi', default=True)
def main(username: str, password: str, to_pypi: bool):
    shutil.rmtree('dist', ignore_errors=True)
    update(['--patch'])
    if to_pypi:
        build([])
        check(['dist/*'])
        upload(['-u', f'"{username}"', '-p', f'"{password}"', 'dist/*'])
        print('Uploaded to PyPi')
    print('what')


if __name__ == '__main__':
    main()
