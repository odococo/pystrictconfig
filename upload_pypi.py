import shutil

import click
from bumpver.cli import update
from build.__main__ import main as build
from tox.session import main as tox
from twine.commands.check import main as check
from twine.commands.upload import main as upload


@click.command()
@click.option('--to-pypi/--no-to-pypi', default=True)
def main(to_pypi: bool):
    try:
        tox(['-r'])
    except SystemExit as ex:
        if ex.code != 0:
            raise ex
    shutil.rmtree('dist', ignore_errors=True)
    try:
        update(['--patch'])
    except SystemExit as ex:
        if ex.code != 0:
            raise ex
    if to_pypi:
        build([])
        check(['dist/*'])
        # authentication through TWINE_USERNAME and TWINE_PASSWORD env variables
        upload(['dist/*'])
        print('Uploaded to PyPi')


if __name__ == '__main__':
    main()
