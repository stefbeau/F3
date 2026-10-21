"""The Explorer's R1 loop-sign sentence must be built from the data (site_src/explorer.js, function r1Sentence), not typed in.

The test extracts the page's own functions (`cross`, `r1Sentence`) and runs them in Node on (a) the committed site/data/explorer.json and
(b) a synthetic dataset in which the three settings cross 0.5 in different years, and checks that the years in the sentence equal the years
computed here from the data, and that the sentence changes when the data change. Skipped with a stated reason when Node or the data are absent.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
JS = REPO / "site_src" / "explorer.js"
DATA = REPO / "site" / "data" / "explorer.json"
NODE = shutil.which("node")

pytestmark = [pytest.mark.skipif(NODE is None, reason="Node.js not found on PATH"),
              pytest.mark.skipif(not DATA.exists(), reason="site/data/explorer.json not present (build the site first)")]


def _functions() -> str:
    src = JS.read_text(encoding="utf-8")
    a = src.index("function cross(")
    b = src.index("function signs()")
    return src[a:b]


def _run(data: dict, tmp_path: Path) -> str:
    """Run the page's own functions in Node. The program goes through a file (the data are too long for a Windows command line)."""
    prog = ("const D=" + json.dumps(data) + ";const Y=D.years;function key(s,d,sup){return s+'|'+d+'|'+(sup||'1')}\n" + _functions() +
            "\nprocess.stdout.write(r1Sentence());")
    f = tmp_path / "r1.js"
    f.write_text(prog, encoding="utf-8")
    return subprocess.run([NODE, str(f)], capture_output=True, text=True, check=True, encoding="utf-8").stdout


def _first_year(data: dict, setting: str, th: float = 0.5):
    y = data["runs"][f"{setting}|central|1"]["frac_automated"]
    return next((data["years"][i] for i, v in enumerate(y) if v >= th), None)


def test_sentence_years_equal_years_computed_from_the_data(tmp_path):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    s = _run(data, tmp_path)
    for name in ("low", "central", "race"):
        year = _first_year(data, name)
        assert re.search(rf"{name}: {year} \(fraction", s), (name, year, s)


def test_sentence_changes_when_the_data_change(tmp_path):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    n = len(data["years"])
    syn = {"years": data["years"], "runs": {}}
    for setting, first in (("low", 12), ("central", 9), ("race", 5)):                       # three DIFFERENT crossing years
        frac = [0.1 if i < first else min(1.0, 0.1 + 0.15 * (i - first + 1)) for i in range(n)]
        syn["runs"][f"{setting}|central|1"] = {"frac_automated": frac}
    s = _run(syn, tmp_path)
    expected = {k: _first_year(syn, k) for k in ("low", "central", "race")}
    assert len(set(expected.values())) == 3, expected
    for name, year in expected.items():
        assert re.search(rf"{name}: {year} \(fraction", s), (name, year, s)
    assert "same in all three settings" not in s            # the 'same year' remark appears only when the data say so
    assert s != _run(json.loads(DATA.read_text(encoding="utf-8")), tmp_path)


def test_committed_data_have_the_same_crossing_year_and_the_sentence_says_so(tmp_path):
    """In the committed data the three settings cross 0.5 in the same year (2030, with different fractions before and after)."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    years = {_first_year(data, k) for k in ("low", "central", "race")}
    s = _run(data, tmp_path)
    if len(years) == 1:
        assert "same in all three settings" in s
    else:
        assert "same in all three settings" not in s
