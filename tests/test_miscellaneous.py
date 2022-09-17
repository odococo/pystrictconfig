from pystrictconfig.core import Any, Map


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
