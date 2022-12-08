from typing import Callable, Any as AnyValue

from yaml import SafeLoader


class CustomLoader(SafeLoader):

    @staticmethod
    def construct(schema, constructor: Callable) -> Callable:
        def wrapper(self, node) -> AnyValue:
            instance = schema
            if isinstance(instance, type):
                instance = schema()
            value = constructor(self, node)
            print(value)
            if instance.validate(value):
                return instance.get(value)

            raise ValueError(f'{value} is not compliant to schema {instance}')

        return wrapper
