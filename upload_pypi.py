import shutil

import click
from bumpver.cli import update
from build.__main__ import main as build
from twine.commands.check import main as check
from twine.commands.upload import main as upload


@click.command()
@click.option('--to-pypi/--no-to-pypi', default=True)
def main(to_pypi: bool):
    shutil.rmtree('dist', ignore_errors=True)
    try:
        update(['--patch'])
    except SystemExit:
        # everything ok. A completed command should exit
        pass
    if to_pypi:
        build([])
        check(['dist/*'])
        # authentication through TWINE_USERNAME and TWINE_PASSWORD env variables
        upload(['dist/*'])
        print('Uploaded to PyPi')


if __name__ == '__main__':
    main()
