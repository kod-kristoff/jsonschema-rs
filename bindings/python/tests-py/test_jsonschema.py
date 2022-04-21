from collections import namedtuple
from contextlib import suppress
from enum import Enum
from functools import partial

import pytest
from hypothesis import given
from hypothesis import strategies as st

from jsonschema_rs import JSONSchema, ValidationError, is_valid, iter_errors, validate

json = st.recursive(
    st.none() | st.booleans() | st.floats() | st.integers() | st.text(),
    lambda children: st.lists(children, min_size=1) | st.dictionaries(st.text(), children, min_size=1),
)


@pytest.mark.parametrize("func", (is_valid, validate))
@given(instance=json)
def test_instance_processing(func, instance):
    with suppress(Exception):
        func(True, instance)


@pytest.mark.parametrize("func", (is_valid, validate))
@given(instance=json)
def test_schema_processing(func, instance):
    with suppress(Exception):
        func(instance, True)


@pytest.mark.parametrize("func", (is_valid, validate))
def test_invalid_schema(func):
    with pytest.raises(ValueError):
        func(2**64, True)


@pytest.mark.parametrize("func", (is_valid, validate))
def test_invalid_type(func):
    with pytest.raises(ValueError, match="Unsupported type: 'set'"):
        func(set(), True)


def test_module():
    assert JSONSchema.__module__ == "jsonschema_rs"


def test_repr():
    assert repr(JSONSchema({"minimum": 5})) == '<JSONSchema: {"minimum":5}>'


@pytest.mark.parametrize(
    "func",
    (
        JSONSchema({"minimum": 5}).validate,
        JSONSchema.from_str('{"minimum": 5}').validate,
        partial(validate, {"minimum": 5}),
    ),
)
def test_validate(func):
    with pytest.raises(ValidationError, match="2 is less than the minimum of 5"):
        func(2)


def test_from_str_error():
    with pytest.raises(ValueError, match="Expected string, got int"):
        JSONSchema.from_str(42)


@pytest.mark.parametrize(
    "val",
    (
        ("A", "B", "C"),
        ["A", "B", "C"],
    ),
)
def test_array_tuple(val):
    schema = {"type": "array", "items": {"type": "string"}}
    validate(schema, val)


@pytest.mark.parametrize(
    "val",
    ((1, 2, 3), [1, 2, 3], {"foo": 1}),
)
def test_array_tuple_invalid(val):
    schema = {"type": "array", "items": {"type": "string"}}
    with pytest.raises(ValueError):
        validate(schema, val)


def test_named_tuple():
    Person = namedtuple("Person", "first_name last_name")
    person_a = Person("Joe", "Smith")
    schema = {"type": "array", "items": {"type": "string"}}
    with pytest.raises(ValueError):
        validate(schema, person_a)


def test_recursive_dict():
    instance = {}
    instance["foo"] = instance
    with pytest.raises(ValueError):
        is_valid(True, instance)


def test_recursive_list():
    instance = []
    instance.append(instance)
    with pytest.raises(ValueError):
        is_valid(True, instance)


def test_paths():
    with pytest.raises(ValidationError) as exc:
        validate({"items": [{"type": "string"}]}, [1])
    assert exc.value.schema_path == ["items", 0, "type"]
    assert exc.value.instance_path == [0]
    assert exc.value.message == '1 is not of type "string"'


@pytest.mark.parametrize(
    "schema, draft, error",
    (
        ([], None, r'\[\] is not of types "boolean", "object"'),
        ({}, 5, "Unknown draft: 5"),
    ),
)
def test_initialization_errors(schema, draft, error):
    with pytest.raises(ValueError, match=error):
        JSONSchema(schema, draft)


@given(minimum=st.integers().map(abs))
def test_minimum(minimum):
    with suppress(SystemError):
        assert is_valid({"minimum": minimum}, minimum)
        assert is_valid({"minimum": minimum}, minimum - 1) is False


@given(maximum=st.integers().map(abs))
def test_maximum(maximum):
    with suppress(SystemError):
        assert is_valid({"maximum": maximum}, maximum)
        assert is_valid({"maximum": maximum}, maximum + 1) is False


@pytest.mark.parametrize("method", ("is_valid", "validate"))
def test_invalid_value(method):
    schema = JSONSchema({"minimum": 42})
    with pytest.raises(ValueError, match="Unsupported type: 'object'"):
        getattr(schema, method)(object())


def test_error_message():
    schema = {"properties": {"foo": {"type": "integer"}}}
    instance = {"foo": None}
    try:
        validate(schema, instance)
        pytest.fail("Validation error should happen")
    except ValidationError as exc:
        assert (
            str(exc)
            == """null is not of type "integer"

Failed validating "type" in schema["properties"]["foo"]

On instance["foo"]:
    null"""
        )


@pytest.mark.parametrize(
    "func",
    (
        JSONSchema({"properties": {"foo": {"type": "integer"}, "bar": {"type": "string"}}}).iter_errors,
        partial(iter_errors, {"properties": {"foo": {"type": "integer"}, "bar": {"type": "string"}}}),
    ),
)
def test_iter_err_message(func):
    instance = {"foo": None, "bar": None}
    errs = func(instance)

    err_a = next(errs)
    assert err_a.message == 'null is not of type "string"'

    err_b = next(errs)
    assert err_b.message == 'null is not of type "integer"'

    with suppress(StopIteration):
        next(errs)
        pytest.fail("Validation error should happen")


@pytest.mark.parametrize(
    "func",
    (
        JSONSchema({"properties": {"foo": {"type": "integer"}}}).iter_errors,
        partial(iter_errors, {"properties": {"foo": {"type": "integer"}}}),
    ),
)
def test_iter_err_empty(func):
    schema = {"properties": {"foo": {"type": "integer"}}}
    instance = {"foo": 1}
    errs = func(instance)
    with suppress(StopIteration):
        next(errs)
        pytest.fail("Validation error should happen")


class StrEnum(Enum):
    bar = "bar"
    foo = "foo"


class IntEnum(Enum):
    bar = 1
    foo = 2


def test_enum_str():
    schema = {"properties": {"foo": {"type": "string"}}}
    instance = {"foo": StrEnum.bar}
    assert is_valid(schema, instance) == True

    instance["foo"] = IntEnum.bar
    assert is_valid(schema, instance) == False


def test_enum_int():
    schema = {"properties": {"foo": {"type": "number"}}}
    instance = {"foo": IntEnum.bar}
    assert is_valid(schema, instance) == True
    instance["foo"] = StrEnum.bar
    assert is_valid(schema, instance) == False
