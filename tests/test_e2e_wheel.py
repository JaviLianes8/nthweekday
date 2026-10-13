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
    done = _run([str(script), "2026-09", "5MO"])
    assert (done.returncode, done.stdout) == (1, "")
    done = _run([str(script), "2026-13", "MO"])
    assert done.returncode == 2 and "month must be in 1..12" in done.stderr
    version = _run([str(script), "--version"])
    assert version.stdout.strip() == f"nthweekday {nthweekday.__version__}"

    probe = (
        "import nthweekday as n; "
        "print(n.nth_weekday(2026, 11, n.THURSDAY, 4), n.parse_byday('-1FR'), n.__file__)"
    )
    shown = _run([str(python), "-c", probe]).stdout
    assert shown.startswith("2026-11-26 (ByDay(Weekday.FRIDAY, -1),) ") and str(env_dir) in shown


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
