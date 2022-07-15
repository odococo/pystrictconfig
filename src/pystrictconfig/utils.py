from pathlib import Path
import yaml

from definitions import JsonLike


def read_yaml(path: str | Path) -> JsonLike:
    with open(path, 'r') as f:
        return yaml.safe_load(f)
