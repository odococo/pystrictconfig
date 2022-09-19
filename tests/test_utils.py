from pathlib import Path

import pytest

from pystrictconfig import FOLDER_DATA
from pystrictconfig import utils
from pystrictconfig.core import Integer


def test_read_yaml1():
    data = utils.validate_yaml(Path(FOLDER_DATA, 'simple_yaml_config.yaml'))
    file = {
        'rest': {
            'url': 'https://example.org/primenumbers/v1',
            'port': 8443
        },
        'prime_numbers': [
            2, 3, 5, 7, 11, 13, 17, 19
        ],
        'prime_numbers2': [
            2, 3, 5, 7, 11, 13, 17, 19
        ]
    }

    assert data == file


def test_read_yaml2():
    schema = Integer()

    with pytest.raises(ValueError):
        utils.validate_yaml(Path(FOLDER_DATA, 'basic_yaml_config.yaml'), schema)


def test_read_json1():
    data = utils.validate_json(Path(FOLDER_DATA, 'simple_json_config.json'))
    file = {
        'rest': {
            'url': 'https://example.org/primenumbers/v1',
            'port': 8443
        },
        'prime_numbers': [
            2, 3, 5, 7, 11, 13, 17, 19
        ],
        'prime_numbers2': [
            2, 3, 5, 7, 11, 13, 17, 19
        ]
    }

    assert data == file


def test_read_json2():
    schema = Integer()

    with pytest.raises(ValueError):
        utils.validate_json(Path(FOLDER_DATA, 'basic_json_config.json'), schema)
