from typing import Any as AnyValue, Tuple

from definitions import JsonLike


class Schema:
    _as_type: type = None

    def __init__(self, **config: AnyValue):
        self._config = config

    def validate(self, value: AnyValue) -> bool:
        return isinstance(value, self.as_type)

    def get(self, value: AnyValue, as_type: type = None) -> AnyValue:
        data_type = as_type or self._as_type

        return data_type(value)

    @property
    def config(self) -> JsonLike:
        return self._config

    @property
    def as_type(self) -> type:
        return self.config.get('as_type', self._as_type)


class Any(Schema):
    def get(self, value: AnyValue, as_type: type = None) -> AnyValue:
        as_type = as_type or type(value)

        return super().get(value, as_type=as_type)


class Integer(Schema):
    _as_type: type = int


class Float(Schema):
    _as_type: type = float


class String(Schema):
    _as_type: type = str


class Bool(Schema):
    _as_type: type = bool
    _yes_values: Tuple[str] = ('YES', 'Y', 'SI', '1', 'TRUE')
    _no_values: Tuple[str] = ('NO', 'N', '0', 'FALSE')

    def get(self, value: AnyValue, as_type: type = None) -> bool:
        value = str(value).upper()
        if value in self.yes_values:
            value = True
        elif value in self.no_values:
            value = False

        return super().get(value, as_type=as_type)

    @property
    def yes_values(self) -> Tuple[str]:
        return self.config.get('yes_values', self._yes_values)

    @property
    def no_values(self) -> Tuple[str]:
        return self.config.get('no_values', self._no_values)


class Map(Schema):
    _as_type: type = dict

    def validate(self, value: AnyValue) -> bool:
        super().validate(value)

        return all([self.config[key].validate(value)
                    for key, value in super().get(value).items()])
