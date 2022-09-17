import pytest

from pystrictconfig.core import Any, Integer, Float, String, Bool, Invalid


def test_any1():
    schema = Any()

    assert schema.validate(1), 'Any schema should validate anything, including integers'


def test_any2():
    schema = Any()

    assert schema.validate(False), 'Any schema should validate anything, including booleans'


def test_any3():
    schema = Any()

    assert schema.validate(['test']), 'Any schema should validate anything, including lists'


def test_any4():
    schema = Any()

    assert schema.validate(None), 'Any schema should validate anything, including None'


def test_any5():
    schema = Any(required=True)

    assert not schema.validate(None), 'Any schema should validate anything, but not None if a value is required'


def test_any6():
    schema = Any(as_type=object)

    with pytest.raises(TypeError):
        schema.get(1)


def test_invalid1():
    schema = Invalid()

    assert not schema.validate(1), 'Invalid should not validate anything, including integers'


def test_invalid2():
    schema = Invalid()

    assert not schema.validate('test'), 'Invalid should not validate anything, including strings'


def test_invalid3():
    schema = Invalid()

    assert schema.get('test') == 'test', 'Invalid getter does not validate value, just getting it'


def test_integer1():
    schema = Integer()

    assert schema.validate(1), 'Integer should validate integer values'


def test_integer2():
    schema = Integer()

    assert not schema.validate(1.0), 'Integer should not validate float values'


def test_integer3():
    schema = Integer(strict=False)

    assert schema.validate(1.0), 'Integer should not validate float values, unless strict is False'


def test_integer4():
    schema = Integer()

    assert schema.get(1) == 1, 'Integer getter of a integer value just returns itself'


def test_integer5():
    schema = Integer()

    assert schema.get(1.5) == 1, 'Integer getter of a float value just cast the number to an integer'


def test_float1():
    schema = Float()

    assert schema.validate(1.0), 'Float should validate float values'


def test_float2():
    schema = Float()

    assert not schema.validate(1), 'Float should not validate integer values'


def test_float3():
    schema = Float(strict=False)

    assert schema.validate(1), 'Float should not validate integer values, unless strict is False'


def test_float4():
    schema = Float()

    assert schema.get(1.5) == 1.5, 'Float getter of a float value just returns itself'


def test_float5():
    schema = Float()

    assert schema.get(1) == 1.0, 'Float getter of an integer value just cast the number to a float'


def test_string1():
    schema = String()

    assert schema.validate('test'), 'String should validate strings'


def test_string2():
    schema = String()

    assert not schema.validate(1), 'String should not validate integers'


def test_string3():
    schema = String()

    assert schema.get(1) == '1', 'String getter of a string value just returns itself'


def test_string4():
    schema = String()

    assert schema.get(1) == '1', 'String getter of an integer value just cast the number to a string'


def test_bool1():
    schema = Bool()

    assert schema.validate(True), 'Bool should validate booleans'


def test_bool2():
    schema = Bool()

    assert schema.validate(False), 'Bool should validate booleans'


def test_bool3():
    schema = Bool()

    assert not schema.validate('SI'), 'Bool should not validate strings'


def test_bool4():
    schema = Bool(strict=False)

    assert schema.validate('SI'), 'Bool should not validate strings, unless strict is False'


def test_bool5():
    schema = Bool()

    assert schema.get('SI'), 'Bool getter checks if value is one of yes_values'


def test_bool6():
    schema = Bool()

    assert not schema.get('FALSE'), 'Bool getter checks if value is one of no_values'


def test_bool7():
    schema = Bool()

    assert schema.get('123'), 'Bool getter of any value is equal to boolean value of the value itself'


def test_bool8():
    schema = Bool()

    assert not schema.get(''), 'Bool getter of any value is equal to boolean value of the value itself'
