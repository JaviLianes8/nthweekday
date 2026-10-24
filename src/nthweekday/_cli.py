"""Command line tool: print the dates an RFC 5545 BYDAY value selects."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence

from ._byday import byday_dates
from ._weekday import quote

_PERIOD = re.compile(r"([0-9]{4})(?:-([0-9]{2}))?")
_SIGNED = re.compile(r"[+-][0-9]")


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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool. Exit 0 when dates were printed, 1 when none matched, 2 on bad input."""
    args = list(sys.argv[1:] if argv is None else argv)
    # argparse reads "-1FR" as an option; a signed BYDAY is always a positional.
    if "--" not in args and any(_SIGNED.match(a) for a in args):
        flags = [a for a in args if a.startswith("-") and not _SIGNED.match(a)]
        args = [*flags, "--", *(a for a in args if a not in flags)]
    parser = _parser()
    opts = parser.parse_args(args)
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
