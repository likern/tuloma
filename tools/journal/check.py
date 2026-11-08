"""Check the relocations, packaged reference and browser entry points."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
for name in ("index.html", "los.html", "laboratory.html", "rust-smoke.html"):
    assert (DIST / name).is_file(), name
assert (DIST / "assets/los.py").read_bytes() == (ROOT / "packages/tuloma-reference/src/tuloma_reference/los.py").read_bytes()
for name in ("main.js", "worker.js", "lesson.js", "load-tuloma.js", "style.css", "brand/favicon.svg"):
    assert (DIST / "assets" / name).is_file(), name
for name in ("los.html", "laboratory.html"):
    text = (DIST / name).read_text()
    assert "<!-- los-source -->" not in text and 'id="comparison"' in text
assert "<math" in (DIST / "los.html").read_text()
manifest_path = DIST / "assets/wheels/manifest.json"
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    wheel = manifest_path.parent / manifest["filename"]
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == manifest["sha256"]
    assert (DIST / "assets/native-smoke.py").is_file()
print("Journal relocation and runtime assets verified")
