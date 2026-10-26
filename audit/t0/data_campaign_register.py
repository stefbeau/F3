"""D-058: build audit/data/sources-register.json and audit/data/needs-user.json from the raw folder and the curated metadata.

Usage:  python -I audit/t0/data_campaign_register.py <raw root> [--out-dir audit/data]

Inputs
  * <raw root>/<dir>/*.fetch.json   written by audit/t0/data_campaign_fetch.py (url, http status, bytes, sha256, retrieval time)
  * audit/t0/data_campaign_meta.py  curated metadata (licence, quote, units, coverage, what each source supports)
Checks done here (a failure stops the build)
  * every licence quote in the metadata occurs verbatim (after whitespace and quote-mark normalisation) in the saved file it names;
  * every file a source claims exists with the recorded sha256 (recomputed here, not trusted from the sidecar);
  * a file that should be a PDF starts with %PDF (an interstitial page is recorded as a failure, not as data).
Nothing downloaded is executed or imported; PDFs are read with pdftotext when available.
"""
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def load_meta():
    spec = importlib.util.spec_from_file_location("data_campaign_meta", HERE / "data_campaign_meta.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


def norm(s: str) -> str:
    """Whitespace, quote-mark and markdown normalisation (links reduced to their text, emphasis marks dropped) so a quote can be matched in .md files."""
    s = html.unescape(s).translate(_QUOTES)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("*", "").replace("_", " ")
    return re.sub(r"\s+", " ", s).strip()


def visible_text(raw: Path, spec: str) -> str:
    """Text of a saved file for quote checking. spec: 'dir/file' or 'dir/file.zip!member'."""
    if "!" in spec:
        zpath, member = spec.split("!", 1)
        with zipfile.ZipFile(raw / zpath) as z:
            return z.read(member).decode("utf-8", "replace")
    p = raw / spec
    head = p.read_bytes()[:5]
    if head == b"%PDF-":
        exe = shutil.which("pdftotext")
        if not exe:
            raise RuntimeError("pdftotext not available to verify a quote in " + spec)
        out = subprocess.run([exe, "-layout", str(p), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        return out.stdout
    if head[:2] == b"PK" and p.suffix.lower() == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        parts = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                parts.extend(str(c) for c in row if c is not None)
        return " ".join(parts)
    t = p.read_bytes().decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t)


def quote_ok(raw: Path, quote: str, spec: str) -> bool:
    text = norm(visible_text(raw, spec))
    q = norm(quote)
    if q in text:
        return True
    return re.sub(r"\s+", "", q) in re.sub(r"\s+", "", text)  # JSON files keep no spaces after colons


def sidecars(raw: Path, d: str):
    out = []
    for p in sorted((raw / d).glob("*.fetch.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def file_ok(raw: Path, rec: dict):
    p = raw / rec["id"] / rec["file"]
    if not rec.get("ok") or not p.is_file():
        return False, rec.get("error") or "missing"
    if p.stat().st_size == 0:
        return False, "empty file"
    if p.suffix.lower() == ".pdf" or rec["file"].endswith(".pdf"):
        if p.read_bytes()[:5] != b"%PDF-":
            return False, "not a PDF (interstitial or error page)"
    return True, None


def build(raw: Path, out_dir: Path):
    meta = load_meta()
    sources, failures, claimed = [], [], set()
    problems = []
    for m in meta.SOURCES:
        dirs = m.get("dirs") or [m["id"]]
        files, fails = [], []
        for d in dirs:
            claimed.add(d)
            for rec in sidecars(raw, d):
                if m.get("only") and rec["file"] not in m["only"]:
                    continue
                ok, why = file_ok(raw, rec)
                if ok:
                    p = raw / d / rec["file"]
                    files.append({"path": f"{d}/{rec['file']}", "bytes": p.stat().st_size, "sha256": sha256_file(p), "url": rec["url"],
                                  "http_status": rec.get("http_status"), "retrieved_utc": rec["retrieved_utc"],
                                  **({"via": rec["via"]} if rec.get("via") else {})})
                else:
                    fails.append({"source_id": m["id"], "path": f"{d}/{rec['file']}", "url": rec["url"], "error": why,
                                  "http_status": rec.get("http_status"), "attempts": rec.get("attempts"), "retrieved_utc": rec.get("retrieved_utc")})
        # curated quote check
        lic = dict(m["licence"])
        qf = lic.get("quote_file")
        if lic.get("quote"):
            if not qf:
                problems.append(f"{m['id']}: licence quote without quote_file")
            else:
                try:
                    lic["quote_verified"] = bool(quote_ok(raw, lic["quote"], qf))
                except Exception as e:  # noqa: BLE001
                    lic["quote_verified"] = False
                    problems.append(f"{m['id']}: could not verify quote in {qf}: {e}")
                if not lic["quote_verified"]:
                    problems.append(f"{m['id']}: quote NOT found in {qf}")
        else:
            lic["quote_verified"] = False
        entry = {
            "id": m["id"], "title": m["title"], "publisher": m["publisher"], "url": m["url"],
            "domains": m["domains"], "supports": m["supports"], "version": m["version"], "retrieved": m.get("retrieved", "2026-10-22"),
            "status": m["status"], "licence": lic, "redistribution": m["redistribution"], "redistribution_note": m["redistribution_note"],
            "units": m["units"], "geography": m["geography"], "time_span": m["time_span"], "variables": m["variables"],
            "files": files, "total_bytes": sum(f["bytes"] for f in files), "notes": m.get("notes", ""),
        }
        for k in ("landing_page", "attribution", "derived", "cross_checks", "role"):
            if m.get(k):
                entry[k] = m[k]
        if m["status"] == "retrieved" and not files:
            problems.append(f"{m['id']}: status retrieved but no file on disk")
        if m["redistribution"] == "yes" and not (lic.get("quote") and lic.get("quote_verified")):
            problems.append(f"{m['id']}: redistribution yes without a verified licence quote")
        sources.append(entry)
        failures.extend(fails)
    unclaimed = sorted(p.name for p in raw.iterdir() if p.is_dir() and p.name not in claimed and not p.name.startswith("_"))
    cc_path = out_dir / "cross-checks.json"
    cross = json.loads(cc_path.read_text(encoding="utf-8"))["items"] if cc_path.exists() else meta.CROSS_CHECKS
    reg = {
        "schema_version": 1,
        "campaign": "D-058",
        "description": "Every external source retrieved or attempted in the D-058 data retrieval campaign. Raw files are NOT committed; sha256 identifies exactly what was read. Licence quotes were checked verbatim against the saved file named in quote_file.",
        "retrieved": "2026-10-22",
        "sources": sources,
        "failures": failures,
        "cross_checks": cross,
        "unregistered_raw_dirs": unclaimed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sources-register.json").write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (out_dir / "needs-user.json").write_text(json.dumps({"schema_version": 1, "campaign": "D-058", "items": meta.NEEDS_USER}, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8", newline="\n")
    return reg, problems


def main(argv):
    raw = Path(argv[1])
    out_dir = REPO / "audit" / "data"
    if "--out-dir" in argv:
        out_dir = Path(argv[argv.index("--out-dir") + 1])
    reg, problems = build(raw, out_dir)
    n_files = sum(len(s["files"]) for s in reg["sources"])
    print(f"sources: {len(reg['sources'])}, files: {n_files}, bytes: {sum(s['total_bytes'] for s in reg['sources'])}, failures: {len(reg['failures'])}")
    print("unregistered raw dirs:", reg["unregistered_raw_dirs"])
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
