"""D-058 data retrieval: download listed files, one directory per source, record sha256 and HTTP status.

Usage:  python -I audit/t0/data_campaign_fetch.py <raw root> <spec.json>

spec.json: a list of {"id": "epoch_notable", "url": "...", "file": "notable_ai_models.csv"}.
Each source id gets its own directory <raw root>/<id>/; the file is saved there with a sidecar <file>.fetch.json
(url, final url, http status, bytes, sha256, retrieved UTC, attempts, error). A download that fails twice is recorded
as a failure and the run goes on. Nothing downloaded is executed or imported. No credentials are sent.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "Mozilla/5.0 (compatible; F3-data-campaign/1.0; research; +https://github.com/stefbeau/F3)"


def curl_fetch(item: dict, out: Path) -> dict:
    """Fallback when Python's TLS store lacks an intermediate certificate: curl.exe (Windows Schannel) with full verification."""
    exe = shutil.which("curl.exe") or shutil.which("curl")
    if not exe:
        return {"ok": False, "error": "curl not found"}
    base = [exe, "-L", "-sS", "--max-time", "300", "-A", UA, "-o", str(out), "-w", "%{http_code} %{url_effective}", item["url"]]
    p = subprocess.run(base, capture_output=True, text=True)
    if p.returncode == 35 and "REVOCATION" in (p.stderr or ""):
        # Windows Schannel could not reach the revocation server; the certificate chain is still verified, only the CRL/OCSP check is skipped.
        p = subprocess.run(base[:1] + ["--ssl-no-revoke"] + base[1:], capture_output=True, text=True)
    code, _, final = (p.stdout or "").partition(" ")
    if p.returncode != 0 or not code.startswith("2"):
        return {"ok": False, "error": f"curl rc={p.returncode} http={code} {p.stderr.strip()[:200]}", "http_status": int(code) if code.isdigit() else None}
    data = out.read_bytes()
    return {"ok": True, "http_status": int(code), "final_url": final, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "error": None, "via": "curl"}


def fetch_one(root: Path, item: dict) -> dict:
    d = root / item["id"]
    d.mkdir(parents=True, exist_ok=True)
    out = d / item["file"]
    rec = {"id": item["id"], "url": item["url"], "file": item["file"], "ok": False, "attempts": 0}
    for attempt in (1, 2):
        rec["attempts"] = attempt
        try:
            req = urllib.request.Request(item["url"], headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
                rec["http_status"] = r.status
                rec["final_url"] = r.geturl()
                rec["content_type"] = r.headers.get("Content-Type")
            out.write_bytes(data)
            if len(data) == 0:
                rec.update(error=f"empty response body (HTTP {rec.get('http_status')}, final url {rec.get('final_url')})", http_status=rec.get("http_status"))
                continue
            rec.update(ok=True, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), error=None)
            break
        except urllib.error.HTTPError as e:
            rec.update(http_status=e.code, error=f"HTTP {e.code} {e.reason}")
        except Exception as e:  # noqa: BLE001
            rec.update(error=f"{type(e).__name__}: {e}")
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                c = curl_fetch(item, out)
                rec.update(c)
                if c["ok"]:
                    break
        time.sleep(2)
    rec["retrieved_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (d / (item["file"] + ".fetch.json")).write_text(json.dumps(rec, indent=1), encoding="utf-8", newline="\n")
    return rec


def main(argv):
    root = Path(argv[1])
    spec = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    for it in spec:
        r = fetch_one(root, it)
        print(("OK  " if r["ok"] else "FAIL"), it["id"], it["file"], r.get("bytes", ""), r.get("error") or "", flush=True)


if __name__ == "__main__":
    main(sys.argv)
