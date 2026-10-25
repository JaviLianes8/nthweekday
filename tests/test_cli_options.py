"""How the command line reads its options: one rule on every Python version."""

from __future__ import annotations

import argparse
import contextlib
import io
import time
from collections.abc import Callable

import pytest

from nthweekday import __version__
from nthweekday._cli import main


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code or 0)
    out, err = capsys.readouterr()
    return code, out, err


@pytest.mark.parametrize(
    "option",
    ["--=\x1b[2J", "-=\x07", "-=‮​", "--=\x1b]0;owned\x07", "-=\x1b]52;c;aGk=\x07", "-\x00"],
)
def test_errors_never_write_an_unprintable_character(
    capsys: pytest.CaptureFixture[str], option: str
) -> None:
    for args in ([option, "2026", "MO"], ["2026", "MO", option]):
        code, out, err = _run(capsys, *args)
        assert (code, out) == (2, "")
        assert all(c.isprintable() for c in err.replace("\n", "")), repr(err)
        assert "unrecognized arguments: " + repr(option) in err


@pytest.mark.parametrize(
    "option",
    ["-help", "-hx", "-hh", "--=x", "-=", "--yearly=1", "--help=x", "-yearly", "---yearly"],
)
def test_malformed_options_are_unrecognized_on_every_version(
    capsys: pytest.CaptureFixture[str], option: str
) -> None:
    code, out, err = _run(capsys, option, "2026", "MO")
    assert (code, out) == (2, "")
    assert err.endswith(f"error: unrecognized arguments: {option!r}\n")
    code, out, err = _run(capsys, option)
    assert (code, out) == (2, "")
    assert "the following arguments are required: period, byday" in err


@pytest.mark.parametrize(
    ("args", "shown"),
    [
        (("-=", "2026", "MO", "--version"), "version"),
        (("-q", "-h"), "help"),
        (("-q", "--version"), "version"),
        (("-h", "--version"), "help"),
        (("--version", "-h"), "version"),
        (("--vers", "--he"), "version"),
        (("2026", "-1FR", "--h"), "help"),
    ],
)
def test_the_first_of_help_and_version_wins_over_anything_else(
    capsys: pytest.CaptureFixture[str], args: tuple[str, ...], shown: str
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, err) == (0, "")
    if shown == "version":
        assert out == f"nthweekday {__version__}\n"
    else:
        assert out.startswith("usage: nthweekday ")


def test_the_long_option_guard_starts_past_40_characters(
    capsys: pytest.CaptureFixture[str],
) -> None:
    forty = "-" + "q" * 39
    code, _, err = _run(capsys, forty, "2026", "MO")
    assert code == 2 and err.endswith(f"error: unrecognized arguments: '{forty}'\n")
    code, _, err = _run(capsys, forty + "q", "2026", "MO")
    assert code == 2 and err.endswith(f"error: unrecognized option '{forty}'... (41 characters)\n")


def test_argparse_reads_at_most_the_three_options_and_two_values(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: list[int] = []
    parse = argparse.ArgumentParser.parse_known_args

    def counted(self: argparse.ArgumentParser, args: list[str]) -> object:
        seen.append(len(args))
        return parse(self, args)

    monkeypatch.setattr(argparse.ArgumentParser, "parse_known_args", counted)
    many = [f"-q{i}" for i in range(5000)] + ["--yearly", "--y", "--ye"] * 5000
    assert _run(capsys, *many, "2026", "-53TH")[0] == 2
    assert seen == [3]
    assert _run(capsys, *["--yearly"] * 5000, "2026", "-53TH") == (0, "2026-01-01\n", "")
    assert seen == [3, 3]


def _time_main(args: list[str]) -> float:
    start = time.perf_counter()
    out, err = io.StringIO(), io.StringIO()
    with (
        contextlib.redirect_stdout(out),
        contextlib.redirect_stderr(err),
        contextlib.suppress(SystemExit),
    ):
        main(args)
    return time.perf_counter() - start


@pytest.mark.parametrize(
    "build",
    [
        lambda n: ["-q"] * n + ["-1FR"] * n,
        lambda n: [f"-q{i}" for i in range(n)] + ["2026"] * n,
        lambda n: ["--yearly"] * n + ["2026", "-1FR"],
    ],
    ids=["repeated", "distinct", "known"],
)
def test_reading_the_arguments_takes_linear_time(build: Callable[[int], list[str]]) -> None:
    # 64 times the arguments may take at most 256 times as long: linear growth passes with
    # room for noise, quadratic growth (4096 times) cannot.
    small, large = build(1000), build(64000)
    best_small = min(_time_main(small) for _ in range(5))
    best_large = min(_time_main(large) for _ in range(2))
    assert best_large < 256 * best_small + 0.05
