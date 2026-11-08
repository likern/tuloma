"""Stage one cp313 WASM wheel and its verified hash for the journal worker."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]


def main(directory):
    wheels = list(Path(directory).glob("tuloma-0.1.0-cp313-cp313-*wasm32.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"Expected exactly one Tuloma cp313 WASM wheel, got {len(wheels)}")
    wheel = wheels[0]
    assets = ROOT / "apps/journal/assets"
    target = assets / "wheels"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    shutil.copy2(wheel, target / wheel.name)
    (target / "manifest.json").write_text(json.dumps({
        "pyodide": "0.29.4", "filename": wheel.name,
        "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
    }, indent=2) + "\n")
    shutil.copy2(ROOT / "tests/browser/smoke.py", assets / "native-smoke.py")
    print(target / "manifest.json")


if __name__ == "__main__":
    main(sys.argv[1])
