from pathlib import Path
from typing import Any as AnyValue, Iterable

from pystrictconfig import TypeLike
from pystrictconfig.core import Integer, OneOf, Any, String


class Port(Integer):
    yaml_tag: str = '!port'

    def validate(self, value: AnyValue) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be an integer between 0 and 65535.
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value):
            return False

        value = self.get(value)

        return 0 <= value <= 65535


class LocalPath(OneOf):
    yaml_tag: str = '!path'
    as_type: TypeLike = Path
    valid_types: Iterable[Any] = (String(), String(as_type=Path))
    exists: bool = True

    def validate(self, value: AnyValue) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be one of the valid values.
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value):
            return False

        path = self.get(value)

        if path.exists() and (self.exists is not None and not self.exists):
            return False
        if not path.exists() and self.exists:
            return False

        return True
