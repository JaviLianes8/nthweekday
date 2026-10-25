"""Command line tool: print the dates an RFC 5545 BYDAY value selects."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence

from ._byday import byday_dates
from ._weekday import _QUOTE_LIMIT, quote

_PERIOD = re.compile(r"([0-9]{4})(?:-([0-9]{2}))?")
_SIGNED = re.compile(r"[+-][0-9]")
_STAND_INS = ("period", "byday")
_OPTIONS = ("--help", "--version", "--yearly")


def _parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="nthweekday",
        description="Print the dates a BYDAY value such as 4TH or -1FR selects, one per line.",
        epilog="examples: nthweekday 2026-11 4TH | nthweekday 2026 -1FR | "
        "nthweekday --yearly 2026 20MO",
    )
    parser.add_argument("period", help="YYYY-MM for one month, or YYYY for every month")
    parser.add_argument("byday", help="BYDAY value, for example 1MO,-1FR or TU")
    parser.add_argument(
        "--yearly",
        action="store_true",
        help="with YYYY, count ordinals within the whole year (BYDAY in a YEARLY rule)",
    )
    parser.add_argument("--version", action="version", version=f"nthweekday {__version__}")
    return parser


def _split(args: Sequence[str]) -> tuple[list[str], list[str]]:
    # One pass: everything after the first "--" is a value, and so is a signed BYDAY such
    # as "-1FR", which argparse would read as an option.
    flags: list[str] = []
    values: list[str] = []
    for at, arg in enumerate(args):
        if arg == "--":
            values.extend(args[at + 1 :])
            break
        is_flag = arg.startswith("-") and arg != "-" and not _SIGNED.match(arg)
        (flags if is_flag else values).append(arg)
    return flags, values


def _option(flag: str) -> str | None:
    # One rule on every Python version: -h, or a non-empty prefix of a long option without
    # "=", as none takes a value. argparse read "-hx", "-=" and "--=x" differently before
    # 3.12, and its "ambiguous option" error repeats the text unescaped.
    if flag == "-h":
        return "--help"
    found = [o for o in _OPTIONS if o.startswith(flag)]
    return found[0] if flag[2:] and "=" not in flag and len(found) == 1 else None


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool. Exit 0 when dates were printed, 1 when none matched, 2 on bad input."""
    flags, values = _split(list(sys.argv[1:] if argv is None else argv))
    parser = _parser()
    # argparse repeats an option it cannot read in full; no option is longer than 40.
    for arg in flags:
        if len(arg) > _QUOTE_LIMIT:
            parser.error(f"unrecognized option {quote(arg)}")
    extra = [flag for flag in dict.fromkeys(flags) if _option(flag) is None]
    # argparse sees no text of the caller: the options it knows, each once and in the order
    # given (so the first of -h and --version wins over anything else), and stand-ins for
    # the values, so it still reports a missing one. Its handling of "--" changed in 3.12.
    options = dict.fromkeys(option for option in map(_option, flags) if option is not None)
    opts = parser.parse_known_args([*options, *_STAND_INS[: len(values)]])[0]
    extra += values[len(_STAND_INS) :]
    if extra:
        parser.error(f"unrecognized arguments: {quote(' '.join(extra))}")
    opts.period, opts.byday = values[: len(_STAND_INS)]
    period = _PERIOD.fullmatch(opts.period)
    if period is None:
        parser.error(f"period must be YYYY or YYYY-MM, got {quote(opts.period)}")
    year, month = int(period[1]), period[2]
    if opts.yearly and month is not None:
        parser.error("--yearly takes a bare year, not YYYY-MM")
    try:
        if opts.yearly:
            found = byday_dates(year, None, opts.byday)
        else:
            months = [int(month)] if month is not None else list(range(1, 13))
            found = [d for m in months for d in byday_dates(year, m, opts.byday)]
    except ValueError as exc:
        parser.error(str(exc))
    if not found:
        print(f"nthweekday: {quote(opts.byday)} selects no date in {opts.period}", file=sys.stderr)
        return 1
    sys.stdout.write("".join(f"{d.isoformat()}\n" for d in found))
    return 0
