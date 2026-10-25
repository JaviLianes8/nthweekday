"""Build the real wheel, install it into a throwaway venv and drive the installed script.

Nothing is mocked: this needs network access for pip to fetch the build backend.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

import nthweekday

ROOT = Path(__file__).resolve().parent.parent
CONSUMER = """\
from datetime import date

from nthweekday import THURSDAY, ByDay, Weekday, byday_dates, nth_weekday, parse_byday


class Index:
    def __index__(self) -> int:
        return 4


assert Weekday(Index()) is ByDay(Index(), Index()).weekday is Weekday.FRIDAY
day: date = nth_weekday(2026, 11, THURSDAY, 4)
days: list[date] = byday_dates(2026, 3, "1SU,-1SU")
entries: tuple[ByDay, ...] = parse_byday("-1FR")
weekday: Weekday = entries[0].weekday
last_friday: ByDay = ByDay(date(2026, 10, 23).weekday(), -1)
assert last_friday == entries[0]
print(day, [d.day for d in days], entries[0])
"""


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600, check=False)


@pytest.mark.e2e
def test_wheel_installs_and_the_script_works(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", "-w", str(dist), str(ROOT)]
    )
    assert built.returncode == 0, built.stderr
    wheels = list(dist.glob("nthweekday-*.whl"))
    assert [w.name for w in wheels] == [f"nthweekday-{nthweekday.__version__}-py3-none-any.whl"]
    names = zipfile.ZipFile(wheels[0]).namelist()
    for module in ("__init__", "__main__", "_weekday", "_month", "_byday", "_cli"):
        assert f"nthweekday/{module}.py" in names
    assert "nthweekday/py.typed" in names
    assert not [n for n in names if n.startswith(("data/", "tests/", "scripts/"))]
    metadata = next(n for n in names if n.endswith(".dist-info/METADATA"))
    requires = [
        line
        for line in zipfile.ZipFile(wheels[0]).read(metadata).decode().splitlines()
        if line.startswith("Requires-Dist:")
    ]
    # Zero runtime dependencies: every requirement belongs to the dev extra.
    assert requires and all("extra == 'dev'" in line for line in requires), requires
    assert any(n.endswith("entry_points.txt") for n in names)
    assert any(n.endswith(".dist-info/licenses/LICENSE") for n in names)
    meta = zipfile.ZipFile(wheels[0]).read(metadata).decode()
    assert "Classifier: Development Status :: 5 - Production/Stable" in meta
    assert "Requires-Python: >=3.10" in meta and "Project-URL: Source," in meta

    env_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
    bindir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bindir / ("python.exe" if os.name == "nt" else "python")
    script = bindir / ("nthweekday.exe" if os.name == "nt" else "nthweekday")
    installed = _run([str(python), "-m", "pip", "install", "-q", "--no-index", str(wheels[0])])
    assert installed.returncode == 0, installed.stderr
    assert script.is_file()

    done = _run([str(script), "2026-11", "4TH"])
    assert (done.returncode, done.stdout) == (0, "2026-11-26\n")
    done = _run([str(script), "2026", "-1FR"])
    assert done.returncode == 0 and done.stdout.splitlines()[-1] == "2026-12-25"
    done = _run([str(python), "-m", "nthweekday", "--yearly", "1998", "20MO"])
    assert (done.returncode, done.stdout) == (0, "1998-05-18\n")
    for command in ([str(script)], [str(python), "-m", "nthweekday"]):
        done = _run([*command, "2026-09", "5MO"])
        assert (done.returncode, done.stdout) == (1, ""), command
        done = _run([*command, "2026-13", "MO"])
        assert done.returncode == 2 and "month must be in 1..12" in done.stderr, command
    version = _run([str(script), "--version"])
    assert version.stdout.strip() == f"nthweekday {nthweekday.__version__}"

    probe = (
        "import nthweekday as n; "
        "print(n.nth_weekday(2026, 11, n.THURSDAY, 4), n.parse_byday('-1FR'), n.__file__)"
    )
    shown = _run([str(python), "-c", probe]).stdout
    assert shown.startswith("2026-11-26 (ByDay(Weekday.FRIDAY, -1),) ") and str(env_dir) in shown

    # A consumer type-checks against the installed package alone, from an empty folder.
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    (consumer / "use.py").write_text(CONSUMER, encoding="utf-8")
    checked = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--no-incremental",
            "--python-executable",
            str(python),
            "use.py",
        ],
        capture_output=True,
        text=True,
        cwd=consumer,
        timeout=600,
        check=False,
        env={k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "MYPYPATH")},
    )
    assert checked.returncode == 0, checked.stdout
    ran = _run([str(python), "-I", str(consumer / "use.py")])
    assert (ran.returncode, ran.stdout) == (0, "2026-11-26 [1, 29] -1FR\n"), ran.stderr


@pytest.mark.e2e
def test_sdist_ships_the_manifest_but_no_upstream_copies(tmp_path: Path) -> None:
    built = _run([sys.executable, "-m", "build", "--sdist", "--outdir", str(tmp_path), str(ROOT)])
    assert built.returncode == 0, built.stderr
    (sdist,) = tmp_path.glob("nthweekday-*.tar.gz")
    with tarfile.open(sdist) as archive:
        names = [name.split("/", 1)[1] for name in archive.getnames() if "/" in name]
    assert "data/upstream/MANIFEST.json" in names
    assert "scripts/fetch_upstream.py" in names and "tests/conftest.py" in names
    assert [n for n in names if n.startswith("data/")] == ["data/upstream/MANIFEST.json"]
    # CONTRIBUTING tells readers to install requirements-dev.txt, so it ships too.
    shipped = ("README.md", "GUIDE.md", "CHANGELOG.md", "CONTRIBUTING.md", "requirements-dev.txt")
    for doc in (*shipped, "LICENSE", "src/nthweekday/py.typed"):
        assert doc in names
    assert not [n for n in names if n.startswith(("IMPROVEMENTS", "CERT-", ".git/", ".github"))]
    assert not [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
