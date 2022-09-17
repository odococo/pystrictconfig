import sys

import click

from pystrictconfig.schema import schema
from pystrictconfig.utils import validate_yaml


@click.command()
@click.option('--file', prompt='Path to yaml file', help='Path to yaml file')
def main(file: str):
    click.secho(f'Hello {file}', fg='blue')
    validate_yaml(file, schema)


if __name__ == '__main__':
    print('args', sys.argv)
    main()
