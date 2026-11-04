#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -B - <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "assets")
from los import X, Z, compare_profile_los

path = Path("assets/examples.json")
examples = json.loads(path.read_text())
examples.update(x=X.tolist(), z=Z.tolist())
for preset in examples["presets"]:
    comparisons = {step: compare_profile_los(*preset["inputs"], step=step)
                   for step in range(5, 51)}
    preset["result"] = comparisons[25]["exact"]
    preset["samples"] = {step: {"sampled": result["sampled"], "samples": result["samples"]}
                         for step, result in comparisons.items()}
path.write_text(json.dumps(examples, ensure_ascii=False, separators=(",", ":")) + "\n")
PY
python -B build-cover.py
if command -v quarto >/dev/null; then
  quarto render
else
  python - <<'PY'
import re
import subprocess
from pathlib import Path

Path("dist").mkdir(exist_ok=True)
for name in ("index", "los", "laboratory"):
    source = Path(f"{name}.qmd").read_text()
    source = re.sub(r"\{\{< include (includes/_[\w-]+\.md) >\}\}", lambda m: Path(m[1]).read_text(), source)
    subprocess.run(
        ["pandoc", "--from=markdown", "--to=html5", "--standalone", "--mathml",
         "--citeproc", "--metadata-file=_quarto.yml",
         "--lua-filter=filters/pseudocode.lua",
         "--template=article.html", "-o", f"dist/{name}.html"],
        input=source, text=True, check=True,
    )
PY
fi
cp -R assets dist/
python - <<'PY'
from html import escape
from pathlib import Path

source = escape(Path("assets/los.py").read_text())
for name in ("los", "laboratory"):
    page = Path(f"dist/{name}.html")
    html = page.read_text()
    assert 'id="comparison"' in html and "<!-- los-source -->" in html, name
    page.write_text(html.replace("<!-- los-source -->", source))
assert "<math" in Path("dist/los.html").read_text()
PY
