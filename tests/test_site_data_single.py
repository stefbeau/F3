"""Explorer v0.2 (D-056): the data is loaded once per page. fetch() and XMLHttpRequest of a local .json are blocked on file:// (checked in Edge: "origin 'null' has been
blocked by CORS policy"), and the pages must open from disk, so the pages load ONE script-form file, site/data/explorer.js (`window.F3DATA=<json>;`). The strict
site/data/explorer.json ships as the data product (CSV and data users, tests) but no page loads it. Both files are written from the same string by the generator, so
this test pins them to the same bytes: the script form cannot drift from the JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
JSON_F = SITE / "data" / "explorer.json"
JS_F = SITE / "data" / "explorer.js"
PAGES = ["index.html", "explorer.html", "compare.html", "connections.html", "methods.html", "limitations.html", "sources.html", "about.html"]
DATA_PAGES = ["index.html", "explorer.html", "compare.html", "connections.html"]            # pages whose scripts draw from the data


@pytest.mark.skipif(not JSON_F.exists(), reason="site/data/explorer.json not present (build the site first)")
def test_script_form_is_the_json_text_and_nothing_else():
    text = JSON_F.read_text(encoding="utf-8")
    assert JS_F.read_text(encoding="utf-8") == "window.F3DATA=" + text + ";\n"
    assert json.loads(JS_F.read_text(encoding="utf-8")[len("window.F3DATA="):-2]) == json.loads(text)


def test_each_data_page_loads_exactly_one_data_file_and_no_page_fetches_the_json():
    for page in PAGES:
        html = (SITE / page).read_text(encoding="utf-8")
        loads = re.findall(r'<script src="(data/[^"]+)"', html)
        assert loads == (["data/explorer.js"] if page in DATA_PAGES else []), (page, loads)
        assert not re.search(r"<script[^>]*explorer\.json|<link[^>]*rel=.(preload|prefetch)[^>]*explorer\.json", html), page
    for js in (SITE / "assets").glob("*.js"):
        src = js.read_text(encoding="utf-8")
        assert "fetch(" not in src and "XMLHttpRequest" not in src and "explorer.json" not in src, js.name       # one copy loaded, no second route to the data


def test_the_data_download_is_named_on_the_methods_page():
    html = (SITE / "methods.html").read_text(encoding="utf-8")
    assert 'href="data/explorer.json"' in html and "strict JSON" in html and "no value" in html


def _strict(text):
    def refuse(token):
        raise ValueError("non-strict JSON constant: " + token)
    return json.loads(text, parse_constant=refuse)


@pytest.mark.skipif(not JSON_F.exists(), reason="site/data/explorer.json not present (build the site first)")
def test_script_and_json_copies_hold_identical_data_under_a_strict_parser():
    js = JS_F.read_text(encoding="utf-8")
    assert js.startswith("window.F3DATA=") and js.rstrip().endswith(";")
    body = js[len("window.F3DATA="):].rstrip()[:-1]
    from_js = _strict(body)                                                                     # NaN / Infinity / -Infinity raise
    from_json = _strict(JSON_F.read_text(encoding="utf-8"))
    assert from_js == from_json
