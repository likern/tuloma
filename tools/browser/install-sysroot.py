"""Install the pinned upstream Pyodide 0.29.4 Rust exception-handling sysroot."""
from pathlib import Path
import subprocess
import tarfile
from upstream import release_archive

TOOLCHAIN = "nightly-2025-02-01"


def main():
    probe = subprocess.run(["rustup", "run", TOOLCHAIN, "rustc", "--print", "sysroot"], capture_output=True, text=True)
    if probe.returncode:
        subprocess.run(["rustup", "toolchain", "install", TOOLCHAIN, "--profile", "minimal", "--no-self-update"], check=True)
    root = subprocess.check_output(["rustup", "run", TOOLCHAIN, "rustc", "--print", "sysroot"], text=True).strip()
    archive = release_archive(
        "pyodide/rust-emscripten-wasm-eh-sysroot", "emcc-4.0.9_nightly-2025-02-01",
        "emcc-4.0.9_nightly-2025-02-01.tar.bz2", 256376931,
        "572731c36ced02d84f2b825a1d91484d48aa5f935d6694d9231369010733fa5b",
    )
    with tarfile.open(archive) as source:
        source.extractall(Path(root) / "lib/rustlib", filter="data")


if __name__ == "__main__":
    main()
