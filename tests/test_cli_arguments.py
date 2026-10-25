"""How the command line splits its arguments: options, values, and the first ``--``."""

from __future__ import annotations

import pytest

from nthweekday._cli import main


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code or 0)
    out, err = capsys.readouterr()
    return code, out, err


def test_a_signed_byday_before_a_double_dash_is_still_a_value(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run(capsys, "2026-11", "-1FR", "--") == (0, "2026-11-27\n", "")
    assert _run(capsys, "2026", "-1FR", "--yearly", "--") == (0, "2026-12-25\n", "")
    assert _run(capsys, "2026-11", "--", "-1FR") == (0, "2026-11-27\n", "")


@pytest.mark.parametrize(
    "args",
    [
        ("2026", "--", "--"),
        ("--", "2026", "--"),
        ("--", "2026-02", "--"),
        ("--yearly", "2026", "--", "--"),
    ],
)
def test_a_second_double_dash_is_a_value(
    capsys: pytest.CaptureFixture[str], args: tuple[str, ...]
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, out) == (2, "")
    assert "invalid BYDAY entry '--'" in err and "Traceback" not in err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("--", "--", "MO"), "period must be YYYY or YYYY-MM, got '--'"),
        (("--", "2026", "--yearly"), "invalid BYDAY entry '--yearly'"),
        (("-", "MO"), "period must be YYYY or YYYY-MM, got '-'"),
        (("2026", "--", "--", "--"), "unrecognized arguments: '--'"),
        (("2026", "-q", "MO", "x"), "unrecognized arguments: '-q x'"),
        (("-q", "2026", "-q", "MO", "-q"), "unrecognized arguments: '-q'\n"),
    ],
)
def test_values_are_read_in_order_and_the_rest_is_refused(
    capsys: pytest.CaptureFixture[str], args: tuple[str, ...], message: str
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, out) == (2, "")
    assert message in err
