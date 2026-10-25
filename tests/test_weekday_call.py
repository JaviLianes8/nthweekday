"""``Weekday(n)`` as tools and type checkers see it: one value, typed Weekday."""

from __future__ import annotations

import ast
import inspect
import pydoc
import typing

import pytest

import nthweekday._weekday
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


def test_the_call_types_its_value_as_supports_index() -> None:
    # The run-time annotations say what the checker-only signature says: an integer value.
    hints = typing.get_type_hints(type(Weekday).__call__)
    assert hints["value"] is typing.SupportsIndex


def test_the_call_types_extra_arguments_as_never_given() -> None:
    # Extra arguments always raise TypeError, so at run time they are typed never given.
    hints = typing.get_type_hints(type(Weekday).__call__)
    assert hints["args"] is typing.NoReturn
    assert hints["kwargs"] is typing.NoReturn


def test_type_checkers_see_a_call_of_one_value_and_nothing_else() -> None:
    # pyright reads Weekday(n) through the metaclass __call__ (mypy through the __new__
    # stub). A signature with extras typed NoReturn would make pyright refuse an unpacked
    # call such as Weekday(*[3]), which runs, so checkers see one value and no extras.
    tree = ast.parse(inspect.getsource(nthweekday._weekday))
    meta = next(
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "_CheckedEnumType"
    )
    guard = next(n for n in meta.body if isinstance(n, ast.If))
    assert ast.unparse(guard.test) == "TYPE_CHECKING"
    (stub,) = (n for n in guard.body if isinstance(n, ast.FunctionDef) and n.name == "__call__")
    params = stub.args
    assert [a.arg for a in params.args] == ["cls", "value"]
    assert [ast.unparse(a.annotation) for a in params.args if a.annotation] == [
        "type[_E]",
        "SupportsIndex",
    ]
    assert (params.vararg, params.kwarg, params.kwonlyargs, params.posonlyargs) == (
        None,
        None,
        [],
        [],
    )
    assert stub.returns is not None and ast.unparse(stub.returns) == "_E"
