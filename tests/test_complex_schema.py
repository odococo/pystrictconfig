from pystrictconfig.yamlschema import List, Integer, Map


def test_list1():
    schema = List()

    assert schema.validate([])


def test_list2():
    schema = List()

    assert schema.validate([1, 2, 3], strict=False)


def test_list3():
    schema = List()

    assert schema.validate([1, 2, 3], data_type=Integer())


def test_list4():
    schema = List()

    assert not schema.validate([1.0, 2.0, 3.0], data_type=Integer())


def test_list5():
    schema = List()

    assert schema.validate([1.0, 2.0, 3.0], data_type=Integer(strict=False))


def test_list6():
    schema = List()

    assert schema.get([1.0, 2.0, 3.0], data_type=Integer()) == [1, 2, 3]


def test_map1():
    schema = Map()

    assert schema.validate({})


def test_map2():
    schema = Map()

    assert schema.validate({1: 2}, strict=False)


def test_map3():
    schema = Map()

    assert not schema.validate({1: 2})


def test_map4():
    schema = Map()

    assert not schema.validate({'nest1': 1.0}, schema={'nest1': Integer()})


def test_map5():
    schema = Map()

    assert schema.validate({'nest1': 1.0}, schema={'nest1': Integer(strict=False)})


def test_map6():
    schema = Map()

    assert not schema.validate({'nest1': 1.0}, schema={'nest1': Integer()})


def test_map7():
    schema = Map()

    assert not schema.validate({}, schema={'nest1': Integer()})


def test_map8():
    schema = Map()

    assert schema.validate({}, schema={'nest1': Integer()}, strict=False)
