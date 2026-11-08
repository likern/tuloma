"""Download pinned upstream release archives, verify SHA-256, then cache."""
import hashlib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CACHE = Path(__file__).resolve().parents[2] / ".cache/upstream"


def download(request):
    for attempt in range(2):
        try:
            with urlopen(request, timeout=45) as source:
                return source.read()
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt or isinstance(error, HTTPError) and error.code < 500:
                raise


def release_archive(repository, tag, name, asset_id, sha256):
    archive = CACHE / name
    if archive.exists():
        payload = archive.read_bytes()
    else:
        # The asset API avoids failures of the release download frontend.
        sources = [
            Request(f"https://api.github.com/repos/{repository}/releases/assets/{asset_id}",
                    headers={"Accept": "application/octet-stream", "User-Agent": "Tuloma-build/0.1"}),
            Request(f"https://github.com/{repository}/releases/download/{tag}/{name}",
                    headers={"User-Agent": "Tuloma-build/0.1"}),
        ]
        for i, request in enumerate(sources):
            try:
                payload = download(request)
                break
            except (HTTPError, URLError, TimeoutError):
                if i == len(sources) - 1:
                    raise
    digest = hashlib.sha256(payload).hexdigest()
    if digest != sha256:
        raise SystemExit(f"Unexpected {name} SHA-256: {digest}; remove {archive} if corrupted")
    CACHE.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(payload)
    print(f"Verified {name} SHA-256: {digest}", flush=True)
    return archive
