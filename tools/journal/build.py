"""Build the journal and stage its deployable files in root dist/."""
from html import escape
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "apps/journal"
REFERENCE = ROOT / "packages/tuloma-reference/src"
sys.path.insert(0, str(REFERENCE))
from tuloma_reference.los import X, Z, compare_profile_los, profile_los


def main():
    shutil.copy2(REFERENCE / "tuloma_reference/los.py", SITE / "assets/los.py")
    path = SITE / "assets/examples.json"
    examples = json.loads(path.read_text())
    examples.update(x=X.tolist(), z=Z.tolist())
    for preset in examples["presets"]:
        comparisons = {step: compare_profile_los(*preset["inputs"], step=step) for step in range(5, 51)}
        preset["result"] = profile_los(*preset["inputs"], diagnostics=True)
        preset["samples"] = {step: {"sampled": r["sampled"], "samples": r["samples"]} for step, r in comparisons.items()}
    path.write_text(json.dumps(examples, ensure_ascii=False, separators=(",", ":")) + "\n")
    for script in ("build-cover.py", "build-lesson.py"):
        subprocess.run([sys.executable, "-B", str(ROOT / "tools/journal" / script)], cwd=SITE, check=True)
    output = SITE / "dist"
    if output.exists():
        shutil.rmtree(output)
    if shutil.which("quarto"):
        subprocess.run(["quarto", "render"], cwd=SITE, check=True)
    else:
        output.mkdir()
        for name in ("index", "los", "laboratory"):
            def expand(text):
                return re.sub(r"\{\{< include (includes/_[\w-]+\.md) >\}\}", lambda m: expand((SITE / m[1]).read_text()), text)
            subprocess.run(
                ["pandoc", "--from=markdown", "--to=html5", "--standalone", "--mathml", "--citeproc",
                 "--metadata-file=_quarto.yml", "--lua-filter=filters/pseudocode.lua",
                 "--lua-filter=filters/article-refs.lua", "--template=article.html", "-o", str(output / f"{name}.html")],
                cwd=SITE, input=expand((SITE / f"{name}.qmd").read_text()), text=True, check=True,
            )
    shutil.copytree(SITE / "assets", output / "assets", dirs_exist_ok=True)
    shutil.copy2(SITE / "rust-smoke.html", output / "rust-smoke.html")
    source = escape((SITE / "assets/los.py").read_text())
    for name in ("los", "laboratory"):
        path = output / f"{name}.html"
        content = path.read_text()
        assert 'id="comparison"' in content and "<!-- los-source -->" in content, name
        path.write_text(content.replace("<!-- los-source -->", source))
    assert "<math" in (output / "los.html").read_text()
    deploy = ROOT / "dist"
    if deploy.exists():
        shutil.rmtree(deploy)
    shutil.copytree(output, deploy)
    print(f"Journal ready: {deploy}")


if __name__ == "__main__":
    main()
