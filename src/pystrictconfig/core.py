import logging
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Any as AnyValue, Tuple, Callable, Mapping, Sequence, Iterable

from pystrictconfig import JsonLike, TypeLike


@dataclass
class Any:
    as_type: TypeLike = None
    strict: bool = True
    required: bool = False

    def __post_init__(self):
        self._original_config = self.config

    def validate(self, value: AnyValue) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked
        @return: True if value is compliant to validator, False otherwise
        """
        if value is None and self.required:
            logging.warning(f'{value} is None but it is required')

            return False
        # strict as config overrides value
        as_type = self.as_type or type(value)
        if self.strict and not isinstance(value, as_type):
            logging.warning(f'{value} is not of type {as_type}')

            return False

        return isinstance(self.get(value), as_type)

    def get(self, value: AnyValue) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        if value is None:
            return None

        if not self.as_type:
            return value

        try:
            return self.as_type(value)
        except (ValueError, TypeError) as e:
            logging.error(e)

            raise e

    @property
    def config(self) -> JsonLike:
        """
        Return configuration values of the validator.

        @return: configuration values
        """
        return deepcopy({key: value for key, value in self.__dict__.items() if not key.startswith('_')})

    @config.setter
    def config(self, config: JsonLike) -> None:
        self.__dict__.update(**config)

    def update_config(self, **config) -> 'Any':
        """
        Update default configuration values with new ones.

        @param config: any configuration as:
        - as_type
        - strict
        - required
        - anything defined in subclasses
        @return: self instance
        """
        self.config = config

        return self

    def restore_config(self) -> 'Any':
        """
        Restore configuration to default values.

        @return: self instance
        """
        self.config = self._original_config

        return self

    def clone(self) -> 'Any':
        """
        Create a copy of validator with current configuration values.

        @return: a copy of the validator
        """
        return deepcopy(self)


@dataclass
class Invalid(Any):
    def validate(self, value: AnyValue) -> bool:
        """
        An Invalid validator which does not validate any value.

        @param value: value to be checked
        @return: False
        """
        return False


@dataclass
class Integer(Any):
    as_type: TypeLike = int


@dataclass
class Float(Any):
    as_type: TypeLike = float


@dataclass
class String(Any):
    as_type: TypeLike = str


@dataclass
class Bool(Any):
    as_type: TypeLike = bool
    yes_values: Tuple[str] = ('YES', 'Y', 'SI', '1', 'TRUE')
    no_values: Tuple[str] = ('NO', 'N', '0', 'FALSE')

    def get(self, value: AnyValue) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten. It is checked against true and false values.
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        value = str(value).upper()
        if value in self.yes_values:
            value = True
        elif value in self.no_values:
            value = False

        return super().get(value)


@dataclass
class List(Any):
    as_type: TypeLike = list
    data_type: TypeLike = None
    expand: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.data_type = self.data_type or (Invalid() if self.strict else Any())
        if self.expand:
            self.as_type = self._builder(self.as_type)

    def validate(self, value: AnyValue) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. Each item of the sequence is checked against the data_type.
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value):
            return False

        for el in value:
            if not self.data_type.validate(el):
                return False

        return True

    def get(self, value: Sequence) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten. Each item of the sequence is gotten with the data_type.
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        return super().get([self.data_type.get(el) for el in value])

    @staticmethod
    def _builder(as_type: TypeLike) -> Callable[[list], AnyValue]:
        """
        Wrapper to type to allow star expression of value.

        @param as_type: type which require star expression
        @return: wrapper to the type
        """
        def wrapper(values: list):
            return as_type(*values)
        return wrapper


@dataclass
class Map(Any):
    as_type: TypeLike = dict
    schema: JsonLike = None
    expand: bool = False

    def __post_init__(self):
        super().__post_init__()
        default_schema = Invalid() if self.strict else Any()
        self.schema = defaultdict(lambda: default_schema, self.schema or {})
        if self.expand:
            self.as_type = self._builder(self.as_type)

    def validate(self, value: Mapping) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. Each value of the dictionary is checked against data_type in the schema
        @return: True if value is compliant to validator, False otherwise
        """
        if self.strict and value.keys() != self.schema.keys():
            logging.warning(f'{value.keys()} has different keys with respect to {self.schema.keys()}')

            return False

        for key, value in value.items():
            if key not in self.schema:
                logging.warning(f'{key} is missing from {self.schema.keys()}')
            if not self.schema[key].validate(value):
                logging.warning(f'{key} has an invalid value')

                return False

        return True

    def get(self, value: AnyValue) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten. Each value is gotten with the data_type in the schema
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        return super().get({k: self.schema[k].get(value[k]) for k, v in value.items()})

    @staticmethod
    def _builder(as_type: TypeLike) -> Callable[[dict], AnyValue]:
        """
        Wrapper to type to allow star expression of value.

        @param as_type: type which require star expression
        @return: wrapper to the type
        """
        def wrapper(values: dict):
            return as_type(**values)
        return wrapper


@dataclass
class Enum(Any):
    valid_values: Iterable[AnyValue] = tuple()

    def __post_init__(self):
        super().__post_init__()
        if not self.valid_values:
            logging.warning('No valid value provided!')

    def validate(self, value: AnyValue) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be one of the valid values.
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value):
            return False

        # if here value is None then required = False
        if value is not None:
            data_type = type(value)
            for el in self.valid_values:
                if (value == el and (type(value) == type(el))) or (not self.strict and value == data_type(el)):
                    break
            else:
                logging.warning(f'{value} is not one of {self.valid_values}')

                return False

        return True


@dataclass
class OneOf(Any):
    valid_types: Iterable[Any] = tuple()

    def __post_init__(self):
        super().__post_init__()
        if not self.valid_types:
            logging.warning('No valid type provided!')

    def validate(self, value: AnyValue) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be one of the valid values.
        @return: True if value is compliant to validator, False otherwise
        """
        for valid_type in self.valid_types:
            if valid_type.validate(value):
                break
        else:
            logging.warning(f'{value} is not one of {self.valid_types}')

            return False

        return True
