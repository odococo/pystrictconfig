from pystrictconfig.yamlschema import List, Integer, Map


def test_list1():
    schema = List()

    assert schema.validate([])


def test_list2():
    schema = List()

    assert schema.validate([1, 2, 3])


def test_list3():
    schema = List(data_type=Integer())

    assert schema.validate([1, 2, 3])


def test_list4():
    schema = List(data_type=Integer())

    assert not schema.validate([1.0, 2.0, 3.0])


def test_list5():
    schema = List(data_type=Integer(strict=False))

    assert schema.validate([1.0, 2.0, 3.0])


def test_list6():
    schema = List(data_type=Integer(strict=False))

    assert schema.get([1.0, 2.0, 3.0]) == [1, 2, 3]


def test_map1():
    schema = Map()

    assert schema.validate({})


def test_map2():
    schema = Map(missing_key_ok=True)

    assert schema.validate({1: 2})


def test_map3():
    schema = Map()

    assert not schema.validate({1: 2})


def test_map4():
    schema = Map(nest1=Integer())

    assert not schema.validate({'nest1': 1.0})


def test_map5():
    schema = Map(nest1=Integer(strict=False))

    assert schema.validate({'nest1': 1.0})
