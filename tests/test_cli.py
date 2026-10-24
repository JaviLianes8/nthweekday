from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from nthweekday._cli import main


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code or 0)
    out, err = capsys.readouterr()
    return code, out, err


def test_one_month(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "2026-11", "4TH") == (0, "2026-11-26\n", "")


def test_signed_byday_is_not_taken_for_an_option(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "2026", "-1FR")
    lines = out.splitlines()
    assert code == 0 and len(lines) == 12
    assert (lines[0], lines[-1]) == ("2026-01-30", "2026-12-25")
    assert _run(capsys, "2026-10", "+1MO")[:2] == (0, "2026-10-05\n")


def test_options_may_come_after_a_signed_byday(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "1998", "-1SU", "--yearly")[:2] == (0, "1998-12-27\n")
    code, out, _ = _run(capsys, "2026-11", "-1FR", "-h")
    assert code == 0 and out.startswith("usage: nthweekday")


def test_an_explicit_double_dash_keeps_a_signed_byday(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "--", "2026-11", "-1FR") == (0, "2026-11-27\n", "")
    assert _run(capsys, "--yearly", "--", "1998", "-1SU")[:2] == (0, "1998-12-27\n")


def test_yearly_ordinals(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "--yearly", "1998", "20MO")[:2] == (0, "1998-05-18\n")


def test_list_values_are_sorted_within_each_month(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "2026-03", "-1SU,1SU")
    assert (code, out) == (0, "2026-03-01\n2026-03-29\n")


def test_nothing_matched_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = _run(capsys, "2026-09", "5MO")
    assert (code, out) == (1, "")
    assert "selects no date in 2026-09" in err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("2026-13", "MO"), "month must be in 1..12"),
        (("0000", "MO"), "year must be in 1..9999"),
        (("2026-1", "MO"), "period must be YYYY or YYYY-MM"),
        (("26", "MO"), "period must be YYYY or YYYY-MM"),
        (("2026", "0MO"), "BYDAY ordinal must be 1..53"),
        (("2026", "-54MO"), "BYDAY ordinal must be 1..53"),
        (("2026", "1XX"), "invalid BYDAY entry"),
        (("--yearly", "2026-05", "MO"), "--yearly takes a bare year"),
        (("2026",), "the following arguments are required"),
    ],
)
def test_bad_input_exits_2(
    capsys: pytest.CaptureFixture[str], args: tuple[str, ...], message: str
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, out) == (2, "")
    assert message in err


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    from nthweekday import __version__

    code, out, _ = _run(capsys, "--version")
    assert (code, out) == (0, f"nthweekday {__version__}\n")


def test_python_m_exits_with_the_code_of_main() -> None:
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent / "src")}
    cases = [
        (["2026-11", "4TH"], 0, "2026-11-26\n"),
        (["2026-09", "5MO"], 1, ""),
        (["26", "MO"], 2, ""),
    ]
    for args, code, out in cases:
        done = subprocess.run(
            [sys.executable, "-m", "nthweekday", *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
            check=False,
        )
        assert (done.returncode, done.stdout) == (code, out), done.stderr
