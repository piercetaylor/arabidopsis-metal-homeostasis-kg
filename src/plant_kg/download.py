"""Reproducible, atomic downloads for public upstream datasets."""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from plant_kg.sources import SourceSpec


def file_digest(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _request_json(url: str, *, timeout: float, retries: int) -> dict[str, Any]:
    error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            error = exc
            if attempt + 1 < retries:
                time.sleep(2**attempt)
    raise RuntimeError(f"Failed to download JSON after {retries} attempts: {url}") from error


def download_file(
    url: str,
    destination: Path,
    *,
    expected_md5: str | None = None,
    timeout: float = 120.0,
    retries: int = 3,
) -> dict[str, Any]:
    """Download to a temporary file, verify it, then atomically publish it."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    error: Exception | None = None
    for attempt in range(retries):
        try:
            with requests.get(url, timeout=timeout, stream=True) as response:
                response.raise_for_status()
                with temporary.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
            if expected_md5 and file_digest(temporary, "md5") != expected_md5.lower():
                raise ValueError(f"MD5 mismatch for {url}")
            temporary.replace(destination)
            return {
                "bytes": destination.stat().st_size,
                "sha256": file_digest(destination),
            }
        except (OSError, requests.RequestException, ValueError) as exc:
            error = exc
            temporary.unlink(missing_ok=True)
            if attempt + 1 < retries:
                time.sleep(2**attempt)
    raise RuntimeError(f"Failed to download after {retries} attempts: {url}") from error


def download_jaspar(
    spec: SourceSpec, destination: Path, *, timeout: float = 120.0, retries: int = 3
) -> dict[str, Any]:
    """Resolve JASPAR pagination and persist detailed Arabidopsis matrix records."""

    results: list[dict[str, Any]] = []
    url: str | None = spec.url

    def fetch_detail(summary: dict[str, Any]) -> dict[str, Any]:
        matrix_id = summary["matrix_id"]
        detail_url = f"https://jaspar.elixir.no/api/v1/matrix/{matrix_id}/"
        return _request_json(detail_url, timeout=timeout, retries=retries)

    # Bound concurrency so a full build is practical without flooding the public API.
    with ThreadPoolExecutor(max_workers=4) as executor:
        while url:
            page = _request_json(url, timeout=timeout, retries=retries)
            for detail in executor.map(fetch_detail, page.get("results", [])):
                species = detail.get("species", [])
                if any(int(item["tax_id"]) == 3702 for item in species):
                    results.append(detail)
            url = page.get("next")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_text(
        json.dumps({"source": spec.name, "results": results}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)
    return {"bytes": destination.stat().st_size, "sha256": file_digest(destination)}


def download_sources(specs: tuple[SourceSpec, ...], raw_dir: Path) -> dict[str, Any]:
    """Download every declared input and write a machine-readable artifact manifest."""

    artifacts: dict[str, Any] = {}
    for spec in specs:
        destination = raw_dir / spec.filename
        if spec.key == "jaspar":
            result = download_jaspar(spec, destination)
        else:
            result = download_file(spec.url, destination, expected_md5=spec.md5)
        artifacts[spec.dataset_id] = {
            "url": spec.url,
            "filename": spec.filename,
            **result,
        }
    manifest = {
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "artifacts": artifacts,
    }
    (raw_dir / "download-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest
