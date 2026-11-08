"""Install the pinned upstream Pyodide 0.29.4 Rust exception-handling sysroot."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

TOOLCHAIN = "nightly-2025-02-01"
URL = ("https://github.com/pyodide/rust-emscripten-wasm-eh-sysroot/releases/download/"
       "emcc-4.0.9_nightly-2025-02-01/emcc-4.0.9_nightly-2025-02-01.tar.bz2")
SHA256 = "572731c36ced02d84f2b825a1d91484d48aa5f935d6694d9231369010733fa5b"
CACHE = Path(__file__).resolve().parents[2] / ".cache/sysroots" / URL.rsplit("/", 1)[1]


def download(request):
    for attempt in range(2):
        try:
            with urlopen(request, timeout=45) as source:
                return source.read()
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt or isinstance(error, HTTPError) and error.code < 500:
                raise


def archive_bytes():
    if CACHE.exists():
        return CACHE.read_bytes()
    try:
        return download(Request(URL, headers={"User-Agent": "Tuloma-build/0.1"}))
    except (HTTPError, URLError, TimeoutError):
        # Official asset API is a fallback for release-CDN failures.
        api = "https://api.github.com/repos/pyodide/rust-emscripten-wasm-eh-sysroot/releases/tags/emcc-4.0.9_nightly-2025-02-01"
        release = json.loads(download(Request(api, headers={"User-Agent": "Tuloma-build/0.1"})))
        asset = next(a for a in release["assets"] if a["name"] == URL.rsplit("/", 1)[1])
        return download(Request(asset["url"], headers={"Accept": "application/octet-stream", "User-Agent": "Tuloma-build/0.1"}))


def main():
    probe = subprocess.run(["rustup", "run", TOOLCHAIN, "rustc", "--print", "sysroot"], capture_output=True, text=True)
    if probe.returncode:
        subprocess.run(["rustup", "toolchain", "install", TOOLCHAIN, "--profile", "minimal", "--no-self-update"], check=True)
    root = subprocess.check_output(["rustup", "run", TOOLCHAIN, "rustc", "--print", "sysroot"], text=True).strip()
    payload = archive_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"Unexpected upstream sysroot SHA-256: {digest}; remove {CACHE} if corrupted")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(payload)
    print(f"Verified upstream sysroot SHA-256: {digest}")
    with tarfile.open(CACHE) as source:
        source.extractall(Path(root) / "lib/rustlib", filter="data")


if __name__ == "__main__":
    main()
