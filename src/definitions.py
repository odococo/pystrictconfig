import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s')

# folders location

FOLDER_SOURCE = Path(__file__).parent
FOLDER_ROOT = FOLDER_SOURCE.parent
FOLDER_DATA = Path(FOLDER_ROOT, 'data')

# custom type hints
JsonLike = Dict[str, Any]
