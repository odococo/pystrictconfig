from pathlib import Path

from definitions import FOLDER_DATA, JsonLike
from pystrictconfig import utils
from pystrictconfig.yamlschema import Integer, Float, String, Bool


def read_data() -> JsonLike:
    return utils.read_yaml(Path(FOLDER_DATA, 'basic_config.yaml'))


def test_integer1():
    schema = Integer()

    assert schema.validate(1)


def test_integer2():
    schema = Integer()

    assert not schema.validate(1.0)


def test_integer3():
    schema = Integer()

    assert schema.get(1) == 1


def test_float1():
    schema = Float()

    assert schema.validate(1.0)


def test_float2():
    schema = Float()

    assert not schema.validate(1)


def test_float3():
    schema = Float()

    assert schema.get(1.0) == 1.0


def test_string1():
    schema = String()

    assert schema.validate('test')


def test_string2():
    schema = String()

    assert not schema.validate(1)


def test_string3():
    schema = String()

    assert schema.get(1) == '1'


def test_bool1():
    schema = Bool()

    assert schema.validate(True)


def test_bool2():
    schema = Bool()

    assert schema.validate(False)


def test_bool3():
    schema = Bool()

    assert not schema.validate('SI')


def test_bool4():
    schema = Bool()

    assert schema.get('SI')


def test_bool5():
    schema = Bool()

    assert not schema.get('FALSE')
