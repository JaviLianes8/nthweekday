"""Edges of the 1.0.0 promise: the Weekday constructor and format(), ByDay's signature,
look-alike bools and strings, and messages that never repeat a huge argument."""

from __future__ import annotations

import inspect
import re
import sys
from collections.abc import Callable
from datetime import date

import pytest

import nthweekday
from nthweekday import (
    FRIDAY,
    MONDAY,
    ByDay,
    Weekday,
    byday_dates,
    next_weekday,
    nth_weekday,
    parse_byday,
)
from nthweekday._cli import main
from nthweekday._weekday import quote


def test_format_gives_the_name_without_a_spec_and_formats_the_number_with_one() -> None:
    assert (format(FRIDAY), f"{FRIDAY}", f"{MONDAY!s:>8}") == ("FRIDAY", "FRIDAY", "  MONDAY")
    assert (f"{FRIDAY:02}", f"{FRIDAY:d}", f"{MONDAY:>8}") == ("04", "4", "       0")
    assert (f"{Weekday.SUNDAY:x}", f"{Weekday.SUNDAY:+}") == ("6", "+6")


def test_the_constructor_checks_its_argument_like_every_function() -> None:
    assert Weekday(6) is Weekday.SUNDAY and Weekday(Weekday.MONDAY) is MONDAY
    for bad in (True, False, 4.0, "4", None, b"4"):
        with pytest.raises(TypeError, match="weekday must be an int"):
            Weekday(bad)  # type: ignore[arg-type]
    for out in (7, -1):
        with pytest.raises(ValueError, match=r"weekday must be in 0\.\.6"):
            Weekday(out)
    with pytest.raises(ValueError) as caught:
        Weekday(10**5000)
    assert len(str(caught.value)) < 80
    # Extra arguments are refused before any lookup, so they cannot skip the check.
    extras: list[Callable[[], object]] = [
        lambda: Weekday(True, module=None),  # type: ignore[call-arg]
        lambda: Weekday(4.0, qualname="x"),  # type: ignore[call-arg, arg-type]
        lambda: Weekday("x" * 10**6, "y"),  # type: ignore[call-arg, arg-type]
    ]
    for call in extras:
        with pytest.raises(TypeError) as refused:
            call()
        assert str(refused.value) == "Weekday() takes one argument, the weekday number"


def test_byday_takes_an_int_weekday_and_stores_a_weekday() -> None:
    day: int = date(2026, 10, 23).weekday()
    entry = ByDay(day, -1)
    assert entry.weekday is FRIDAY and type(entry.weekday) is Weekday
    assert ByDay(4) == ByDay(FRIDAY) and hash(ByDay(4, 1)) == hash(ByDay(FRIDAY, 1))


def _numpy_like_bool(name: str) -> object:
    # numpy 1.x bool scalars have __index__, so only their type tells them apart; the type
    # is named bool_ before numpy 2.0 and bool after.
    fake = type(name, (), {"__module__": "numpy", "__index__": lambda self: 1})
    return fake()


@pytest.mark.parametrize("name", ["bool_", "bool"])
def test_numpy_bool_scalars_are_refused_like_bool(name: str) -> None:
    flag = _numpy_like_bool(name)
    calls: list[Callable[[], object]] = [
        lambda: nth_weekday(2026, flag, 0, 1),  # type: ignore[arg-type]
        lambda: nth_weekday(2026, 1, flag, 1),  # type: ignore[arg-type]
        lambda: ByDay(flag, flag),  # type: ignore[arg-type]
        lambda: Weekday(flag),  # type: ignore[arg-type]
    ]
    for call in calls:
        with pytest.raises(TypeError, match=f"must be an int, got {name}$"):
            call()


def test_real_numpy_bools_are_refused() -> None:
    numpy = pytest.importorskip("numpy")
    with pytest.raises(TypeError):
        nth_weekday(2026, numpy.bool_(True), 0, 1)
    assert nth_weekday(numpy.int64(2026), numpy.int8(11), numpy.uint8(3), 4) == date(2026, 11, 26)


class _Hostile(str):
    def __repr__(self) -> str:
        return "R" * 10_000_000

    def upper(self) -> str:
        raise RuntimeError("upper called")

    def split(self, *args: object, **kwargs: object) -> list[str]:
        raise RuntimeError("split called")

    def isascii(self) -> bool:
        raise RuntimeError("isascii called")


def test_str_subclasses_are_read_as_plain_strings() -> None:
    assert parse_byday(_Hostile("-1FR")) == (ByDay(FRIDAY, -1),)
    assert Weekday.parse(_Hostile("fri")) is FRIDAY
    assert byday_dates(2026, 10, _Hostile("-1FR")) == [date(2026, 10, 30)]
    for call in (lambda: parse_byday(_Hostile("XX")), lambda: Weekday.parse(_Hostile("XX"))):
        with pytest.raises(ValueError) as caught:
            call()
        assert len(str(caught.value)) < 100
    # Every message quotes through this helper, whoever calls it.
    assert quote(_Hostile("XX")) == "'XX'"


@pytest.mark.parametrize(
    "call",
    [
        lambda: nth_weekday(2026, "x" * 10**6, 0, 1),  # type: ignore[arg-type]
        lambda: nth_weekday(2026, 1, [0] * 10**6, 1),  # type: ignore[arg-type]
        lambda: nth_weekday(2026, 1, 0, b"1" * 10**6),  # type: ignore[arg-type]
        lambda: next_weekday(date(2026, 1, 1), [0] * 10**6),  # type: ignore[arg-type]
        lambda: next_weekday("2" * 10**6, 0),  # type: ignore[arg-type]
        lambda: ByDay(0, "1" * 10**6),  # type: ignore[arg-type]
        lambda: byday_dates(2026, 1, 10**5000),  # type: ignore[arg-type]
        lambda: parse_byday(b"M" * 10**6),  # type: ignore[arg-type]
        lambda: Weekday.parse(["x"] * 10**6),  # type: ignore[arg-type]
        lambda: Weekday.from_iso("1" * 10**6),  # type: ignore[arg-type]
    ],
)
def test_type_errors_name_the_type_and_never_the_value(call: Callable[[], object]) -> None:
    with pytest.raises(TypeError) as caught:
        call()
    message = str(caught.value)
    assert len(message) < 80 and "xx" not in message and "11" not in message and "00" not in message


@pytest.mark.parametrize(
    "args",
    [
        ["2026", "MO", "x" * 30_000],
        ["2026", "MO", *["x"] * 10_000],
        ["2026", "MO", "-" + "y" * 5000],
        ["--" + "z" * 5000, "2026", "MO"],
        ["--yearly=" + "q" * 5000, "2026", "MO"],
        ["-h" + "w" * 5000, "2026", "MO"],
        ["--=" + "v" * 5000, "2026", "MO"],
        ["2026", "-1FR", "-" + "u" * 5000],
        ["--", "2026", "MO", "t" * 5000],
    ],
)
def test_command_line_errors_quote_at_most_40_characters(
    capsys: pytest.CaptureFixture[str], args: list[str]
) -> None:
    with pytest.raises(SystemExit) as stop:
        main(args)
    err = capsys.readouterr().err
    assert stop.value.code == 2 and len(err) < 400, err[:200]
    assert not any(c * 41 in err for c in "xyzqwvut")


@pytest.mark.parametrize("length", [41, 42, 60, 80, 81])
def test_an_option_past_the_quote_limit_is_cut(
    capsys: pytest.CaptureFixture[str], length: int
) -> None:
    value = "q" * (length - len("--yearly="))
    with pytest.raises(SystemExit) as stop:
        main(["--yearly=" + value, "2026", "MO"])
    err = capsys.readouterr().err
    assert stop.value.code == 2 and value not in err and f"({length} characters)" in err


def test_public_classes_keep_their_source_and_functions_report_the_package() -> None:
    for name in ("ByDay", "NoSuchDayError", "Weekday"):
        source = inspect.getsource(getattr(nthweekday, name))
        assert source.startswith(("@dataclass", "class ")), name
        assert re.search(rf"^class {name}[(:]", source, re.M), name
        assert len(source.splitlines()) > 10, name
    for name in nthweekday.__all__:
        obj = getattr(nthweekday, name)
        if inspect.isfunction(obj):
            assert obj.__module__ == "nthweekday", name
            assert inspect.getsource(obj).startswith(f"def {name}("), name


def test_pickles_of_the_classes_load_from_their_defining_modules() -> None:
    import pickle

    for value in (Weekday.MONDAY, ByDay(FRIDAY, -1), nthweekday.NoSuchDayError("x")):
        module = type(value).__module__
        assert module.startswith("nthweekday.") and module in sys.modules
        dumped = pickle.dumps(value)
        assert module.encode() in dumped
        assert repr(pickle.loads(dumped)) == repr(value)
