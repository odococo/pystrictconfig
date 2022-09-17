import json
from pathlib import Path

import logging

import yaml

from pystrictconfig import JsonLike
from pystrictconfig.core import Any


def validate_yaml(path: str | Path, schema: Any = Any()) -> JsonLike:
    """
    Read a yaml file with a schema.

    @param path: path to a yaml file
    @param schema: schema of the yaml file
    @return: the content of the file with respect to the schema
    """
    logging.debug(f'Reading yaml file: {path}')
    with open(path, 'r') as f:
        value = yaml.safe_load(f)
        if schema.validate(value):
            return schema.get(value)

        raise ValueError


def validate_json(path: str | Path, schema: Any = Any()) -> JsonLike:
    """
    Read a json file with a schema.

    @param path: path to a json file
    @param schema: schema of the json file
    @return: the content of the file with respect to the schema
    """
    logging.debug(f'Reading json file: {path}')
    with open(path, 'r') as f:
        value = json.load(f)
        if schema.validate(value):
            return schema.get(value)

        raise ValueError
