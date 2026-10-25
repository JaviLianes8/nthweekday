"""What a type checker accepts (any integer type where an integer is asked for) and refuses."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import nthweekday

CALLER = """\
from datetime import date

from nthweekday import (
    ByDay, Weekday, byday_dates, last_weekday, next_weekday, nth_weekday,
    nth_weekday_in_year, previous_weekday, week_of_month, weekdays_in_month,
)


class Index:
    def __index__(self) -> int:
        return 4


d = date(2026, 10, 12)
w: Weekday = Weekday(Index())
w = Weekday.from_iso(Index())
b: ByDay = ByDay(Index(), Index())
dates: list[date] = byday_dates(Index(), Index(), "MO") + weekdays_in_month(Index(), 1, 0)
d = nth_weekday(Index(), Index(), Index(), Index())
d = last_weekday(Index(), Index(), Index())
d = nth_weekday_in_year(Index(), Index(), Index())
d = next_weekday(d, Index()) or previous_weekday(d, Index())
n: int = week_of_month(d, Index())
# None is meaningful here: a yearly rule, an entry without an ordinal.
dates = byday_dates(2026, None, "MO")
b = ByDay(1, None)
# Unpacked arguments run, so neither checker may refuse them.
values: list[int] = [3]
named: dict[str, int] = {"value": 3}
w = Weekday(*[3])
w = Weekday(**{"value": 3})
w = Weekday(*values)
w = Weekday(**named)
"""

# Each line must be refused with the error code after it.
REFUSED = """\
from nthweekday import Weekday

Weekday(None)  # arg-type
Weekday("MO")  # arg-type
Weekday(4.0)  # arg-type
Weekday(3, 4)  # call-arg
Weekday(3, module="x")  # call-arg
"""


# pyright's names for mypy's error codes in REFUSED.
PYRIGHT_RULES = {"arg-type": "reportArgumentType", "call-arg": "reportCallIssue"}


def _source_root() -> Path | None:
    # From a source tree the package is found through an extra path; installed, through py.typed.
    root = Path(nthweekday.__file__).resolve().parent.parent
    return None if root.name == "site-packages" else root


def _mypy(tmp_path: Path, source: str) -> tuple[str, int]:
    api = pytest.importorskip("mypy.api")
    root = _source_root()
    search = "" if root is None else f"mypy_path = {root.as_posix()}\n"
    (tmp_path / "mypy.ini").write_text(f"[mypy]\n{search}", encoding="utf-8")
    (tmp_path / "caller.py").write_text(source, encoding="utf-8")
    out, err, status = api.run(
        [
            "--strict",
            "--no-incremental",
            "--python-version=3.10",
            f"--config-file={tmp_path / 'mypy.ini'}",
            f"--cache-dir={tmp_path / 'cache'}",
            str(tmp_path / "caller.py"),
        ]
    )
    return out + err, status


def test_any_integer_type_type_checks_where_an_integer_is_asked_for(tmp_path: Path) -> None:
    out, status = _mypy(tmp_path, CALLER)
    assert status == 0, out


def test_a_weekday_call_without_one_integer_fails_type_checking(tmp_path: Path) -> None:
    out, status = _mypy(tmp_path, REFUSED)
    assert status == 1, out
    expected = {
        (number, line.rsplit("# ", 1)[1])
        for number, line in enumerate(REFUSED.splitlines(), 1)
        if "# " in line
    }
    found = {
        (int(match[1]), match[2])
        for match in re.finditer(r"caller\.py:(\d+): error: .*\[([a-z-]+)\]$", out, re.M)
    }
    assert found == expected, out


def _pyright(tmp_path: Path, source: str) -> list[tuple[int, str]]:
    # Optional: pyright reads Weekday(n) through other annotations than mypy does.
    pytest.importorskip("pyright")
    root = _source_root()
    config: dict[str, object] = {"typeCheckingMode": "strict", "pythonVersion": "3.10"}
    if root is not None:
        config["extraPaths"] = [root.as_posix()]
    (tmp_path / "pyrightconfig.json").write_text(json.dumps(config), encoding="utf-8")
    (tmp_path / "caller.py").write_text(source, encoding="utf-8")
    command = [sys.executable, "-m", "pyright", "--outputjson", "--pythonpath", sys.executable]
    run = subprocess.run(
        [*command, "-p", str(tmp_path), str(tmp_path / "caller.py")],
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    report = json.loads(run.stdout)
    return sorted(
        (item["range"]["start"]["line"] + 1, item.get("rule", item["message"]))
        for item in report["generalDiagnostics"]
        if item["severity"] == "error"
    )


def test_pyright_accepts_what_runs(tmp_path: Path) -> None:
    assert _pyright(tmp_path, CALLER) == []


def test_pyright_refuses_a_weekday_call_without_one_integer(tmp_path: Path) -> None:
    expected = [
        (number, PYRIGHT_RULES[line.rsplit("# ", 1)[1]])
        for number, line in enumerate(REFUSED.splitlines(), 1)
        if "# " in line
    ]
    assert _pyright(tmp_path, REFUSED) == expected
