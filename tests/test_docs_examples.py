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


def test_every_public_name_has_a_docstring_example_that_passes() -> None:
    tests = [t for t in doctest.DocTestFinder().find(nthweekday) if t.examples]
    named = {t.name.removeprefix("nthweekday.").split(".")[0] for t in tests}
    constants = {name for name in nthweekday.__all__ if name.isupper()}
    # The day constants are Weekday members: their examples are those of Weekday.
    assert named == set(nthweekday.__all__) - constants
    runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS)
    for test in tests:
        runner.run(test)
    assert runner.summarize(verbose=False).failed == 0
    assert runner.summarize(verbose=False).attempted >= 40
