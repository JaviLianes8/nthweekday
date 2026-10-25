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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool. Exit 0 when dates were printed, 1 when none matched, 2 on bad input."""
    flags, values = _split(list(sys.argv[1:] if argv is None else argv))
    parser = _parser()
    # argparse repeats an option it cannot read in full; no option is longer than 40.
    for arg in flags:
        if len(arg) > _QUOTE_LIMIT:
            parser.error(f"unrecognized option {quote(arg)}")
    # Before 3.12 argparse takes time quadratic in the number of options, so each distinct
    # one is read on its own, in order, so -h still prints the help next to an unknown one.
    known: list[str] = []
    extra: list[str] = []
    for flag in dict.fromkeys(flags):
        (extra if parser.parse_known_args([flag, *_STAND_INS])[1] else known).append(flag)
    # The values never reach argparse, whose handling of "--" changed in 3.12: it sees
    # stand-ins, so it still reports a missing value, and the values are read here.
    opts = parser.parse_known_args([*known, *_STAND_INS[: len(values)]])[0]
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
