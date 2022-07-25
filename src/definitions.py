import logging
from pathlib import Path
from typing import Dict, Any, Callable, Type

logging.basicConfig(format='%(asctime)d-%(levelname)s-%(message)s')

# folders location

FOLDER_SOURCE = Path(__file__).parent
FOLDER_ROOT = FOLDER_SOURCE.parent
FOLDER_DATA = Path(FOLDER_ROOT, 'data')

# custom type hints
JsonLike = Dict[str, Any]
TypeLike = Type | Callable
