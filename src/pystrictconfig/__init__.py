import importlib.metadata
import logging
from pathlib import Path
from typing import Dict, Callable, Type, Union, TypeVar

__version__ = importlib.metadata.version(__package__ or __name__)

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.DEBUG)

# folders location

FOLDER_PACKAGE = Path(__file__).parent
FOLDER_SOURCE = FOLDER_PACKAGE.parent
FOLDER_ROOT = FOLDER_SOURCE.parent
FOLDER_DATA = Path(FOLDER_ROOT, 'data')

# custom type hints
T = TypeVar('T')

JsonLike = Union[Dict[str, T], T]
TypeLike = Union[Callable, Type]
