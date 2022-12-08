import logging
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Any as AnyValue, Tuple, Callable, Mapping, Sequence, Iterable, Type, Dict

from pystrictconfig import JsonLike, TypeLike
from pystrictconfig.yaml_loader import CustomLoader


class YamlType(type):
    def __new__(mcs, name: str, bases: Tuple[Type], dct: Dict):
        clazz = super().__new__(mcs, name, bases, dct)
        # noinspection PyTypeChecker
        cls = dataclass(clazz)
        if cls.yaml_constructor:
            logging.info(f'Added constructor for {cls.yaml_tag} with {cls.yaml_constructor} for {name}')
            # noinspection PyArgumentList
            CustomLoader.add_constructor(cls.yaml_tag, CustomLoader.construct(cls(), cls.yaml_constructor))

        return cls


class Any(metaclass=YamlType):
    yaml_tag: str = None
    yaml_constructor: Callable = None
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


class Invalid(Any):
    yaml_tag: str = None
    yaml_constructor: Callable = CustomLoader.construct_undefined

    def validate(self, value: AnyValue) -> bool:
        """
        An Invalid validator which does not validate any value.

        @param value: value to be checked
        @return: False
        """
        return False


class Integer(Any):
    yaml_tag: str = 'tag:yaml.org,2002:int'
    yaml_constructor: Callable = CustomLoader.construct_yaml_int
    as_type: TypeLike = int


class Float(Any):
    yaml_tag: str = 'tag:yaml.org,2002:float'
    yaml_constructor: Callable = CustomLoader.construct_yaml_float
    as_type: TypeLike = float


class String(Any):
    yaml_tag: str = 'tag:yaml.org,2002:str'
    yaml_constructor: Callable = CustomLoader.construct_yaml_str
    as_type: TypeLike = str


@dataclass
class Bool(Any):
    yaml_tag: str = 'tag:yaml.org,2002:bool'
    yaml_constructor: Callable = CustomLoader.construct_yaml_bool
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


class List(Any):
    yaml_tag: str = 'tag:yaml.org,2002:seq'
    yaml_constructor: Callable = CustomLoader.construct_sequence
    as_type: TypeLike = list
    data_type: Any = None
    strict: bool = False
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


class Map(Any):
    yaml_tag: str = 'tag:yaml.org,2002:map'
    yaml_constructor: Callable = CustomLoader.construct_mapping
    as_type: TypeLike = dict
    schema: JsonLike[Any] = None
    strict: bool = False
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


class Enum(Any):
    valid_values: Iterable[AnyValue] = (None,)

    def __post_init__(self):
        super().__post_init__()
        if not self.valid_values:
            logging.warning(f'No valid value provided for {self.__class__.__name__}!')

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


class Schema(type):
    def __call__(cls, *args, **kwargs) -> AnyValue:
        obj = super().__call__(*args, **kwargs)
        fields = {key: value for key, value in vars(obj).items() if not key.startswith('_')}
        if not fields:
            schema: Map = Map(strict=False)
        else:
            schema: Map = getattr(obj, '_schema')

            assert isinstance(schema, Map), 'Schema should be defined in a variable called _schema of type Map'
        assert schema.validate(fields), 'Instance is not compliant to its schema'

        return obj


class OneOf(Any):
    valid_types: Iterable[Any] = (Any(),)

    def __post_init__(self):
        super().__post_init__()
        if not self.valid_types:
            logging.warning(f'No valid type provided for {self.__class__.__name__}!')

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
