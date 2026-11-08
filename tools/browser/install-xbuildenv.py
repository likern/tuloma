"""Install the exact official Pyodide 0.29.4 archive via its supported URL API."""
import subprocess
from upstream import release_archive


def main():
    archive = release_archive(
        "pyodide/pyodide", "0.29.4", "xbuildenv-0.29.4.tar.bz2", 414312937,
        "a29fc4a076408a18fc29eb4b280f80c6dddc95c19514c874c29e590d0931c02a",
    )
    subprocess.run(["pyodide", "xbuildenv", "install", "--url", archive.as_uri()], check=True)


if __name__ == "__main__":
    main()
