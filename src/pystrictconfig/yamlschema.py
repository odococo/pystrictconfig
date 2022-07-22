import logging
from collections import defaultdict
from typing import Any as AnyValue, Tuple, Dict

from definitions import JsonLike


class Any:

    def __init__(self, strict: bool = True, as_type: type = object, **config: AnyValue):
        config['strict'] = config.get('strict', strict)
        config['as_type'] = config.get('as_type', as_type)
        self._config = config

    def validate(self, value: AnyValue) -> bool:
        if not self.strict:
            value = self.get(value)

        logging.debug(f'Validating {value} for {self.as_type or type(value)}')

        return isinstance(value, self.as_type or type(value))

    def get(self, value: AnyValue, as_type: type = None) -> AnyValue:
        if value is None:
            return None

        data_type = as_type or self.as_type or type(value)

        return data_type(value)

    @property
    def config(self) -> JsonLike:
        return self._config

    @property
    def as_type(self) -> type:
        return self.config['as_type']

    @property
    def strict(self) -> bool:
        return self.config['strict']


class Invalid(Any):
    def validate(self, value: AnyValue) -> bool:
        return False


class Integer(Any):

    def __init__(self, strict: bool = True, as_type: type = int, **config: AnyValue):
        super().__init__(strict=strict, as_type=as_type, **config)


class Float(Any):

    def __init__(self, strict: bool = True, as_type: type = float, **config: AnyValue):
        super().__init__(strict=strict, as_type=as_type, **config)


class String(Any):

    def __init__(self, strict: bool = True, as_type: type = str, **config: AnyValue):
        super().__init__(strict=strict, as_type=as_type, **config)


class Bool(Any):

    def __init__(self, strict: bool = True, as_type: type = bool,
                 yes_values: Tuple[str] = ('YES', 'Y', 'SI', '1', 'TRUE'),
                 no_values: Tuple[str] = ('NO', 'N', '0', 'FALSE'),
                 **config: AnyValue):
        config['yes_values'] = config.get('yes_values', yes_values)
        config['no_values'] = config.get('no_values', no_values)
        super().__init__(strict=strict, as_type=as_type, **config)

    def get(self, value: AnyValue, as_type: type = None) -> AnyValue:
        value = str(value).upper()
        if value in self.yes_values:
            value = True
        elif value in self.no_values:
            value = False

        return super().get(value, as_type=as_type)

    @property
    def yes_values(self) -> Tuple[str]:
        return self.config['yes_values']

    @property
    def no_values(self) -> Tuple[str]:
        return self.config['no_values']


class List(Any):

    def __init__(self, strict: bool = True, as_type: type = list, data_type: Any = Any(), **config: AnyValue):
        config['data_type'] = config.get('data_type', data_type)
        super().__init__(strict=strict, as_type=as_type, **config)

    def validate(self, value: AnyValue) -> bool:
        if not super().validate(value):
            return False

        return all([self.data_type.validate(el)
                    for el in super().get(value)])

    def get(self, value: AnyValue, as_type: type = None) -> AnyValue:
        return super().get([self.data_type.get(el) for el in value])

    @property
    def data_type(self) -> Any:
        return self.config['data_type']


class Map(Any):

    def __init__(self, strict: bool = True, as_type: type = dict, missing_key_ok: bool = False, **config: AnyValue):
        config['missing_key_ok'] = config.get('missing_key_ok', missing_key_ok)
        super().__init__(strict=strict, as_type=as_type, **config)

    def validate(self, value: AnyValue) -> bool:
        if not super().validate(value):
            return False

        return all([self.schema[key].validate(value)
                    for key, value in super().get(value).items()])

    def get(self, value: AnyValue, as_type: type = None) -> AnyValue:
        return super().get([key.get(value) for key, value in value.items()])

    @property
    def schema(self) -> Dict[str, Any]:
        default_schema = Any() if self.missing_key_ok else Invalid()
        schema = {key: value for key, value in self.config.items() if isinstance(value, Any)}

        return defaultdict(lambda: default_schema, schema)

    @property
    def missing_key_ok(self) -> bool:
        return self.config['missing_key_ok']
