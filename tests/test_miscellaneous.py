from dataclasses import dataclass

import pytest

from pystrictconfig.core import Any, Map, Schema, Integer


def test_update1():
    schema = Any(required=True)

    assert schema.update_config(required=False).validate(None), 'Configuration values can be updated by update_config'


def test_update2():
    schema = Any(required=True)

    assert not schema.update_config(required=False).restore_config().validate(None), \
        'Configuration values can be updated by update_config and restored by restore_config'


def test_clone1():
    schema = Any()

    assert schema == schema.clone(), 'A schema should be equal to a copy of itself'


def test_clone2():
    schema = Any()

    assert not schema == schema.clone().update_config(required=True), 'An update of a schema does not afflict copies'


def test_clone3():
    schema = Map(schema={'test1': Any()})

    assert not schema == schema.clone().update_config(schema={'test2': Any()}), \
        'A deepcopy of the schema is executed, not a shallow copy'


def test_metaclass1():
    class X(metaclass=Schema):
        _schema: Map = Map(schema={
            'x': Integer()
        })

        def __init__(self, x: int):
            self.x = x

    assert X(1).x == 1, 'A class with a schema should not raise exception if it is valid'


def test_metaclass2():
    class X(metaclass=Schema):
        _schema: Map = Map(schema={
            'x': Integer()
        }, strict=True)

        def __init__(self, x: int, y: float):
            self.x = x
            self.y = y

    with pytest.raises(AssertionError):
        X(1, 2)


def test_metaclass3():
    class X(metaclass=Schema):
        pass

    X()


def test_metaclass4():
    @dataclass
    class X(metaclass=Schema):
        _schema = Map(schema={
            'x': Integer()
        })

        x: int = 42

    X()


def test_metaclass5():
    @dataclass
    class X(metaclass=Schema):
        _schema = Map()

    @dataclass
    class Y(X):
        _schema = Map(schema={
            'x': Integer()
        })

        x: int = 42

    Y()
