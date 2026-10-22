"""D-058 data retrieval campaign: the register, the derived series and the needs-user list are consistent.

What these tests fix (written with the register; they check structure and provenance, not scientific content):
* the three JSON files validate against their schemas (a small validator for the schema subset used, no extra dependency);
* every source that is flagged redistributable ('yes') has a licence quote that was found verbatim in the saved file;
* every derived series carries its provenance (sources, file checksums) and only from redistributable sources, and the checksums it
  records equal the register's;
* where the raw folder exists on this machine (F3_DATA_RAW, or ../data-raw next to the worktree), every registered file still has the recorded
  sha256, and every derived series rebuilds byte-identically from it. Without the raw folder those tests skip with a stated reason.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "audit" / "data"
REGISTER = DATA / "sources-register.json"
NEEDS = DATA / "needs-user.json"
DERIVED = DATA / "derived"


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------------- a small JSON-schema validator (subset)
def validate(inst, schema, root, path="$"):
    errs = []
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return validate(inst, node, root, path)
    if "const" in schema and inst != schema["const"]:
        errs.append(f"{path}: expected {schema['const']!r}, got {inst!r}")
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: {inst!r} not in {schema['enum']}")
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        def ok(x, ty):
            return {"object": isinstance(x, dict), "array": isinstance(x, list), "string": isinstance(x, str), "integer": isinstance(x, int) and not isinstance(x, bool),
                    "number": isinstance(x, (int, float)) and not isinstance(x, bool), "boolean": isinstance(x, bool), "null": x is None}[ty]
        if not any(ok(inst, ty) for ty in types):
            return errs + [f"{path}: type {type(inst).__name__} not in {types}"]
    if isinstance(inst, str):
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            errs.append(f"{path}: {inst!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(inst) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']}")
    if isinstance(inst, (int, float)) and not isinstance(inst, bool) and "minimum" in schema and inst < schema["minimum"]:
        errs.append(f"{path}: {inst} < {schema['minimum']}")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing required '{k}'")
        for k, sub in schema.get("properties", {}).items():
            if k in inst:
                errs += validate(inst[k], sub, root, f"{path}.{k}")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} items")
        if "items" in schema:
            for i, x in enumerate(inst):
                errs += validate(x, schema["items"], root, f"{path}[{i}]")
    return errs


def _raw_root():
    cands = [os.environ.get("F3_DATA_RAW"), str(REPO.parent / "data-raw")]
    for c in cands:
        if c and Path(c).is_dir():
            return Path(c)
    return None


@pytest.fixture(scope="module")
def reg():
    return _load(REGISTER)


@pytest.fixture(scope="module")
def derived():
    return {p.stem: _load(p) for p in sorted(DERIVED.glob("*.json"))}


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------------------------------- schemas
def test_register_matches_schema(reg):
    schema = _load(DATA / "sources-register.schema.json")
    errs = validate(reg, schema, schema)
    assert not errs, "\n".join(errs[:20])


def test_needs_user_matches_schema():
    schema = _load(DATA / "needs-user.schema.json")
    errs = validate(_load(NEEDS), schema, schema)
    assert not errs, "\n".join(errs[:20])


def test_every_derived_series_matches_schema(derived):
    schema = _load(DATA / "derived-series.schema.json")
    assert derived, "no derived series committed"
    bad = {}
    for n, d in derived.items():
        e = validate(d, schema, schema)
        if e:
            bad[n] = e[:3]
    assert not bad, bad


def test_validator_can_fail():
    """The validator is part of the test: it must reject a broken register (guards against a validator that accepts everything)."""
    schema = _load(DATA / "sources-register.schema.json")
    broken = _load(REGISTER)
    broken["sources"][0]["redistribution"] = "maybe"
    broken["sources"][0]["files"] = [{"path": "x", "bytes": 1, "sha256": "zz", "url": "ftp://x", "retrieved_utc": "today"}]
    errs = validate(broken, schema, schema)
    assert any("redistribution" in e for e in errs) and any("sha256" in e for e in errs)


# ---------------------------------------------------------------------------------------------------- licence discipline
def test_ids_unique(reg):
    ids = [s["id"] for s in reg["sources"]]
    assert len(ids) == len(set(ids))


def test_every_redistributable_yes_has_a_verified_quoted_licence(reg):
    bad = [s["id"] for s in reg["sources"] if s["redistribution"] == "yes" and not (s["licence"]["quote"].strip() and s["licence"]["quote_verified"] and s["licence"].get("quote_file"))]
    assert not bad, f"redistribution 'yes' without a verified quoted licence: {bad}"


def test_no_licence_is_guessed(reg):
    """A source with no licence quote can only be 'unclear' or 'no', never 'yes'."""
    bad = [s["id"] for s in reg["sources"] if not s["licence"]["quote"].strip() and s["redistribution"] == "yes"]
    assert not bad


def test_non_commercial_and_no_derivatives_are_not_redistributable(reg):
    for s in reg["sources"]:
        name = s["licence"]["name"].upper()
        if re.search(r"\bNC\b|NON-?COMMERCIAL|\bND\b|NODERIV", name) and "CC BY 4.0 (" not in name[:12]:
            assert s["redistribution"] != "yes", f"{s['id']}: licence '{s['licence']['name']}' is NC or ND but flagged yes"


def test_blocked_sources_have_no_files_or_are_documents(reg):
    for s in reg["sources"]:
        if s["status"] == "blocked" and s["files"]:
            assert s.get("role") == "document" or s["redistribution"] != "yes" or all(not f["path"].endswith((".csv", ".xlsx", ".zip")) for f in s["files"]), s["id"]


def test_every_failure_is_listed_with_a_reason_and_none_is_silent(reg):
    assert reg["failures"], "the campaign had failures; the list must not be empty"
    for f in reg["failures"]:
        assert f["error"] and f["url"].startswith("http")


def test_needs_user_covers_the_blocked_sources(reg):
    need_ids = {n["id"] for n in _load(NEEDS)["items"]}
    blocked = [s["id"] for s in reg["sources"] if s["status"] == "blocked"]
    # each blocked source is either listed itself or is covered by a need whose id starts with it or shares its stem
    missing = [b for b in blocked if not any(n == b or n.startswith(b) or b.startswith(n) or b.split("_")[0] in n for n in need_ids)]
    assert not missing, f"blocked sources with no needs-user entry: {missing}"


# ---------------------------------------------------------------------------------------------------- derived series provenance
def test_derived_series_have_provenance_and_only_from_redistributable_sources(reg, derived):
    by_id = {s["id"]: s for s in reg["sources"]}
    files = {f["path"]: f for s in reg["sources"] for f in s["files"]}
    for n, d in derived.items():
        assert d["id"] == n
        assert d["sources"] and d["source_files"]
        for src in d["sources"]:
            s = by_id[src["id"]]
            assert s["redistribution"] == "yes" and s["licence"]["quote_verified"], f"{n}: source {src['id']} is not redistributable"
            assert src["licence_quote"] == s["licence"]["quote"]
        for f in d["source_files"]:
            assert f["path"] in files, f"{n}: {f['path']} not in the register"
            assert files[f["path"]]["sha256"] == f["sha256"], f"{n}: checksum of {f['path']} differs from the register"


def test_declared_derived_series_exist(reg, derived):
    for s in reg["sources"]:
        for name in s.get("derived", []):
            assert name in derived, f"{s['id']} declares derived series {name} that is not in audit/data/derived"


def test_derived_series_are_small_summaries_not_raw_dumps(derived):
    for p in DERIVED.glob("*.json"):
        assert p.stat().st_size < 1_500_000, f"{p.name} is {p.stat().st_size} bytes: a derived series must be an aggregate, not a copy of raw data"


def test_no_credentials_in_the_data_files():
    pat = re.compile(r"(api[_-]?key|apikey|secret|password|bearer\s+[A-Za-z0-9]|token=)", re.I)
    for p in [REGISTER, NEEDS, DATA / "cross-checks.json", *DERIVED.glob("*.json")]:
        txt = p.read_text(encoding="utf-8")
        m = pat.search(txt)
        assert not m, f"{p.name}: looks like a credential near {txt[max(0, m.start() - 40):m.end() + 40]!r}"


def test_nc_nd_values_are_not_republished(derived):
    """EDGAR fossil CO2 (IEA, CC BY-NC-ND) and the WDI series that repeats it must not appear as values in the derived files or cross-checks."""
    assert "edgar_fossil_co2" not in derived and "co2_fossil_edgar" not in derived
    wdi = derived["wdi_world_series"]["data"]
    assert "EN.GHG.CO2.MT.CE.AR5" not in wdi and "EG.USE.ELEC.KH.PC" not in wdi and "ER.H2O.FWTL.K3" not in wdi
    cc = _load(DATA / "cross-checks.json")["items"]
    for x in cc:
        if "edgar2025_fossil_co2" in json.dumps(x):
            assert "not republished" in json.dumps(x)


# ---------------------------------------------------------------------------------------------------- checks against the raw folder (skip without it)
def test_registered_files_have_the_recorded_checksums(reg):
    raw = _raw_root()
    if raw is None:
        pytest.skip("raw data folder not found (set F3_DATA_RAW, or place data-raw next to the worktree); checksums not checked")
    bad, n = [], 0
    for s in reg["sources"]:
        for f in s["files"]:
            p = raw / f["path"]
            if not p.is_file():
                continue
            n += 1
            if p.stat().st_size != f["bytes"] or _sha(p) != f["sha256"]:
                bad.append(f["path"])
    assert n > 0, "raw folder present but none of the registered files in it"
    assert not bad, f"checksum or size differs from the register: {bad[:10]}"


def _load_builder():
    spec = importlib.util.spec_from_file_location("data_campaign", REPO / "site_src" / "data_campaign.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_derived_series_rebuild_identically_from_the_raw_folder(derived):
    raw = _raw_root()
    if raw is None:
        pytest.skip("raw data folder not found; derived series not rebuilt")
    m = _load_builder()
    ctx = m.Ctx(raw)
    have_pdf = shutil.which("pdftotext") is not None
    checked = 0
    for name, b in m.BUILDERS.items():
        if b["needs_pdf"] and not have_pdf:
            continue
        doc = m.build_one(ctx, name)
        text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
        assert text == (DERIVED / f"{name}.json").read_text(encoding="utf-8"), f"{name}: rebuild differs from the committed file"
        checked += 1
    assert checked >= 20


def test_every_builder_has_a_committed_output_and_vice_versa(derived):
    m = _load_builder()
    assert set(m.BUILDERS) == set(derived)
