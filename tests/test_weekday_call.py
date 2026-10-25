"""``Weekday(n)`` as tools and type checkers see it: one value, typed Weekday."""

from __future__ import annotations

import inspect
import pydoc
import typing

import pytest

from nthweekday import Weekday


def test_the_signature_is_one_value_on_every_version() -> None:
    assert str(inspect.signature(Weekday)) == "(value)"
    assert "Weekday(value)" in pydoc.plain(pydoc.render_doc(Weekday))
    assert Weekday(value=3) is Weekday.THURSDAY
    with pytest.raises(TypeError, match="takes one argument"):
        Weekday(3, 4)  # type: ignore[call-arg]


def test_the_call_is_typed_to_return_the_class_it_is_called_on() -> None:
    hints = typing.get_type_hints(type(Weekday).__call__)
    returned = hints["return"]
    assert isinstance(returned, typing.TypeVar)
    assert hints["cls"] == type[returned]
    assert typing.Any not in hints.values()
