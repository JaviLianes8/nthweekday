"""Every ``expression  # -> value`` line in the README and the GUIDE must hold, and every
docstring example must pass."""

from __future__ import annotations

import doctest
import re
from pathlib import Path

import pytest

import nthweekday

ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(r"```python\n(.*?)```", re.S)


@pytest.mark.parametrize(("name", "least"), [("README.md", 20), ("GUIDE.md", 34)])
def test_documented_results_are_true(name: str, least: int) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    namespace: dict[str, object] = {}
    checked = 0
    for block in BLOCK.findall(text):
        lines: list[str] = []
        for line in block.splitlines():
            if "  # -> " in line:
                exec("\n".join(lines), namespace)
                lines = []
                code, expected = line.split("  # -> ", 1)
                got = eval(code, namespace)
                assert got == eval(expected, namespace), line
                if expected.startswith(("ByDay", "Weekday", "(ByDay")):
                    # The repr is what users see in a console, so it is part of the promise.
                    assert repr(got) == expected, line
                checked += 1
            else:
                lines.append(line)
        exec("\n".join(lines), namespace)
    assert checked >= least


def test_docs_use_only_public_names() -> None:
    for name in ("README.md", "GUIDE.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert not re.search(r"nthweekday\._[a-z]|from \._", text), name


# Every docstring with an example; the classes keep their defining module (so that
# inspect.getsource finds them), so their examples are collected from the classes.
DOCTESTS = {
    "ByDay": 4,
    "NoSuchDayError": 2,
    "Weekday": 4,
    "Weekday.code": 1,
    "Weekday.from_iso": 1,
    "Weekday.iso": 1,
    "Weekday.parse": 2,
    "byday_dates": 3,
    "last_weekday": 2,
    "next_weekday": 4,
    "nth_weekday": 3,
    "nth_weekday_in_year": 3,
    "ordinal_of": 3,
    "parse_byday": 2,
    "previous_weekday": 3,
    "week_of_month": 4,
    "weekdays_in_month": 2,
}


def test_every_public_name_has_a_docstring_example_that_passes() -> None:
    finder = doctest.DocTestFinder()
    tests = finder.find(nthweekday)
    for name in ("ByDay", "NoSuchDayError", "Weekday"):
        tests += finder.find(getattr(nthweekday, name))
    found = {t.name.removeprefix("nthweekday."): len(t.examples) for t in tests if t.examples}
    assert found == DOCTESTS
    constants = {name for name in nthweekday.__all__ if name.isupper()}
    # The day constants are Weekday members: their examples are those of Weekday.
    assert {name.split(".")[0] for name in found} == set(nthweekday.__all__) - constants
    runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS)
    for test in tests:
        runner.run(test)
    assert runner.summarize(verbose=False) == (0, sum(DOCTESTS.values()))
