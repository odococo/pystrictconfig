# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

from sample.simple import add_one


def test_add_one():
    assert add_one(5) == 6


def test_add_two():
    assert not add_one(5) == 7
