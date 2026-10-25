"""Seeded property and hostile-input tests: only the documented errors, bounded messages,
linear time. The expected dates are found by walking the calendar one day at a time."""

from __future__ import annotations

import contextlib
import random
import time
from collections.abc import Callable
from datetime import date, timedelta

import pytest

from nthweekday import (
    ByDay,
    Weekday,
    byday_dates,
    nth_weekday,
    nth_weekday_in_year,
    parse_byday,
)
from nthweekday._cli import main

PIECES = [
    "SU",
    "mo",
    "TU",
    "we",
    "TH",
    "fr",
    "SA",
    "+",
    "-",
    "0",
    "1",
    "2",
    "5",
    "9",
    "53",
    ",",
    " ",
    "\x00",
    chr(0x17F),
    chr(0x212A),
    chr(0xFF11),
    "\ud800",
    "=",
    ";",
    "MO" * 50,
]


def _walk(year: int, month: int | None, entry: ByDay) -> set[date]:
    day = date(year, month or 1, 1)
    days = []
    while day.year == year and (month is None or day.month == month):
        if day.weekday() == entry.weekday:
            days.append(day)
        if day == date(9999, 12, 31):
            break
        day += timedelta(days=1)
    if entry.ordinal is None:
        return set(days)
    n = entry.ordinal
    index = n - 1 if n > 0 else len(days) + n
    return {days[index]} if 0 <= index < len(days) else set()


@pytest.mark.parametrize("seed", range(3))
def test_parse_raises_only_value_error_with_a_short_message(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(20000):
        value = "".join(rng.choice(PIECES) for _ in range(rng.randint(0, 30)))
        try:
            entries = parse_byday(value)
        except ValueError as error:
            assert len(str(error)) < 300, value
        else:
            assert parse_byday(",".join(map(str, entries))) == entries
            assert all(type(e.weekday) is Weekday for e in entries)


@pytest.mark.parametrize("seed", range(3))
def test_byday_dates_match_a_day_by_day_walk(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(300):
        year = rng.choice([1, 2, 1582, 1900, 2000, 2024, 2026, 2100, 9999])
        month = rng.choice([None, *range(1, 13)])
        entries = [
            ByDay(Weekday(rng.randrange(7)), rng.choice([None, *range(-53, 0), *range(1, 54)]))
            for _ in range(rng.randint(1, 5))
        ]
        expected = set().union(*(_walk(year, month, e) for e in entries))
        got = byday_dates(year, month, entries)
        assert got == sorted(expected), (year, month, entries)
        assert byday_dates(year, month, ",".join(map(str, entries))) == got


@pytest.mark.parametrize("seed", range(3))
def test_nth_queries_match_a_day_by_day_walk(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(300):
        year, weekday = rng.randint(1, 9999), Weekday(rng.randrange(7))
        month, n = rng.randint(1, 12), rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        expected = _walk(year, month, ByDay(weekday, n))
        try:
            got = {nth_weekday(year, month, weekday, n)}
        except ValueError:
            got = set()
        assert got == expected
        n = rng.choice([*range(-53, 0), *range(1, 54)])
        try:
            got = {nth_weekday_in_year(year, weekday, n)}
        except ValueError:
            got = set()
        assert got == _walk(year, None, ByDay(weekday, n))


@pytest.mark.parametrize("seed", range(2))
def test_the_command_line_exits_0_1_or_2(seed: int, capsys: pytest.CaptureFixture[str]) -> None:
    rng = random.Random(seed)
    periods = ["2026", "2026-02", "0001", "9999-12", "2026-13", "26", "", "-1", "2026-1x"]
    for _ in range(400):
        args = [rng.choice(periods), "".join(rng.choice(PIECES[:16]) for _ in range(4))]
        args += rng.sample(["--yearly", "--", "-1FR"], rng.randint(0, 2))
        rng.shuffle(args)
        try:
            code = main(args)
        except SystemExit as stop:
            code = stop.code  # type: ignore[assignment]
        assert code in (0, 1, 2), args
        assert len(capsys.readouterr().err) < 2000


def _time(call: Callable[[], object]) -> float:
    start = time.perf_counter()
    with contextlib.suppress(ValueError):
        call()
    return time.perf_counter() - start


@pytest.mark.parametrize(
    "build",
    [
        lambda k: ",".join(["-1FR"] * k),
        lambda k: "MO" * k,
        lambda k: "1" * k + "MO",
        lambda k: ",".join(["5MO", "53SU"] * k) + ",bad",
        lambda k: chr(0x17F) * k,
    ],
)
def test_parse_time_is_linear(build: Callable[[int], str]) -> None:
    small, large = build(20000), build(160000)
    best_small = min(_time(lambda: parse_byday(small)) for _ in range(3))
    best_large = min(_time(lambda: parse_byday(large)) for _ in range(3))
    assert best_large < 8 * 4 * best_small + 0.05


def test_huge_arguments_give_short_messages() -> None:
    calls: list[Callable[[], object]] = [
        lambda: parse_byday("x" * 1_000_000),
        lambda: parse_byday("MO," * 100_000 + "x" * 100_000),
        lambda: Weekday.parse("M" * 1_000_000),
        lambda: nth_weekday(10**5000, 1, 0, 1),
        lambda: nth_weekday(2026, 1, 0, -(10**5000)),
        lambda: ByDay(Weekday.MONDAY, 10**100),
        lambda: byday_dates(2026, 10**30, "MO"),
    ]
    for call in calls:
        with pytest.raises(ValueError) as caught:
            call()
        assert len(str(caught.value)) < 300


def test_a_huge_valid_list_is_answered() -> None:
    assert byday_dates(2026, 10, ",".join(["5FR", "-1FR", "FR"] * 50000)) == [
        date(2026, 10, d) for d in (2, 9, 16, 23, 30)
    ]


def test_command_line_messages_are_short(capsys: pytest.CaptureFixture[str]) -> None:
    for args in (["2026", "x" * 100_000], ["9" * 100_000, "MO"], ["2026-09", "5MO," * 50_000]):
        with contextlib.suppress(SystemExit):
            main([*args[:-1], args[-1].rstrip(",")])
        assert len(capsys.readouterr().err) < 1000
