"""What a type checker accepts: any integer type where an integer is asked for."""

from __future__ import annotations

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
"""


def test_any_integer_type_type_checks_where_an_integer_is_asked_for(tmp_path: Path) -> None:
    api = pytest.importorskip("mypy.api")
    # From a source tree the package is found through mypy_path; installed, through py.typed.
    root = Path(nthweekday.__file__).resolve().parent.parent
    search = "" if root.name == "site-packages" else f"mypy_path = {root.as_posix()}\n"
    (tmp_path / "mypy.ini").write_text(f"[mypy]\n{search}", encoding="utf-8")
    (tmp_path / "caller.py").write_text(CALLER, encoding="utf-8")
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
    assert status == 0, out + err
