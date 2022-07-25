import logging
from collections import defaultdict
from typing import Any as AnyValue, Tuple, Dict, Callable, Mapping, Sequence

from definitions import JsonLike, TypeLike


class Any:
    _as_type: TypeLike = None
    _strict: bool = True
    _required: bool = False

    def __init__(self, **config: AnyValue):
        self._config = config

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        if value is None and self.required(required):
            logging.warning(f'{value} is None but it is required')

            return False
        # strict as config overrides value
        as_type = self.as_type or type(value)
        if self.strict(strict) and not isinstance(value, as_type):
            logging.warning(f'{value} is not of type {as_type}')

            return False

        return isinstance(self.get(value), as_type)

    def get(self, value: AnyValue, as_type: TypeLike = None, **config) -> AnyValue:
        if value is None:
            return None

        data_type = as_type or self.as_type or type(value)

        try:
            return data_type(value)
        except ValueError as e:
            logging.error(e)

            raise e

    @property
    def config(self) -> JsonLike:
        return self._config

    @property
    def as_type(self) -> TypeLike:
        return self._as_type

    def strict(self, value: bool) -> bool:
        return value if value is not None else self.config.get('strict', self._strict)

    def required(self, value: bool) -> bool:
        return value if value is not None else self.config.get('required', self._required)


class Invalid(Any):
    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        return False


class Integer(Any):
    _as_type: TypeLike = int


class Float(Any):
    _as_type: TypeLike = float


class String(Any):
    _as_type: TypeLike = str


class Bool(Any):
    _as_type: TypeLike = bool

    def __init__(self,
                 yes_values: Tuple[str] = ('YES', 'Y', 'SI', '1', 'TRUE'),
                 no_values: Tuple[str] = ('NO', 'N', '0', 'FALSE'),
                 **config: AnyValue):
        super().__init__(yes_values=yes_values, no_values=no_values, **config)

    def get(self, value: AnyValue, as_type: TypeLike = None, **config) -> AnyValue:
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
    _as_type: TypeLike = list

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None,
                 data_type: TypeLike = None, **config) -> bool:
        if not super().validate(value, strict=strict, required=required):
            return False

        data_type = data_type or (Invalid() if self.strict(strict) else Any())
        for el in value:
            if not data_type.validate(el):
                return False

        return True

    def get(self, value: Sequence, as_type: TypeLike = None,
            data_type: TypeLike = Any(), expand: bool = False, **config) -> AnyValue:
        value = self.as_type(value)
        if expand:
            as_type = self._builder(as_type)

        return super().get([data_type.get(el) for el in value], as_type=as_type)

    @staticmethod
    def _builder(as_type: TypeLike) -> Callable[[list], AnyValue]:
        def wrapper(values: list):
            return as_type(*values)
        return wrapper


class Map(Any):
    _as_type: type = dict

    def validate(self, value: Mapping, strict: bool = True, required: bool = True,
                 schema: Dict[str, Any] = None, **config) -> bool:
        default_schema = Invalid() if self.strict(strict) else Any()
        schema = defaultdict(lambda: default_schema, schema or {})
        if self.strict(strict) and value.keys() != schema.keys():
            logging.warning(f'{value.keys()} has different ')

            return False

        for key, value in value.items():
            if key not in schema:
                logging.warning(f'{key} is missing from {schema.keys()}')
            if not schema[key].validate(value):
                return False

        return True

    def get(self, value: AnyValue, as_type: TypeLike = None,
            schema: Dict[str, Any] = None, expand: bool = False, **config) -> AnyValue:
        value = self.as_type(value)
        schema = schema or {key: Any() for key, value in value.items()}
        if expand:
            as_type = self._builder(as_type)

        return super().get({k: schema[k].get(value[k]) for k, v in schema.items()}, as_type=as_type)

    @staticmethod
    def _builder(as_type: TypeLike) -> Callable[[dict], AnyValue]:
        def wrapper(values: dict):
            return as_type(**values)
        return wrapper
