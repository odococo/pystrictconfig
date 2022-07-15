from pathlib import Path

# folders location
from typing import Dict, Any

FOLDER_SOURCE = Path(__file__).parent
FOLDER_ROOT = FOLDER_SOURCE.parent

# custom type hints
JsonLike = Dict[str, Any]
