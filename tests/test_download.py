import hashlib
import json
from pathlib import Path

import pytest

from plant_kg import download
from plant_kg.sources import load_sources


class _Response:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int) -> list[bytes]:
        assert chunk_size > 0
        return [self.payload]


def test_download_is_verified_before_replacing_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "source.tsv"
    destination.write_bytes(b"known-good")
    monkeypatch.setattr(download.requests, "get", lambda *_args, **_kwargs: _Response(b"bad"))
    monkeypatch.setattr(download.time, "sleep", lambda _seconds: None)

    with pytest.raises(RuntimeError, match="Failed to download"):
        download.download_file(
            "https://example.test/source.tsv",
            destination,
            expected_md5=hashlib.md5(b"expected").hexdigest(),
        )

    assert destination.read_bytes() == b"known-good"
    assert not destination.with_suffix(".tsv.part").exists()


def test_successful_download_records_size_and_sha256(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"public-data\n"
    monkeypatch.setattr(download.requests, "get", lambda *_args, **_kwargs: _Response(payload))
    destination = tmp_path / "source.tsv"

    result = download.download_file("https://example.test/source.tsv", destination)

    assert destination.read_bytes() == payload
    assert result == {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def test_jaspar_download_follows_pages_and_checks_species(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).parents[1]
    spec = next(
        source for source in load_sources(root / "config/sources.toml") if source.key == "jaspar"
    )
    pages = {
        spec.url: {"results": [{"matrix_id": "MA0001.1"}], "next": "https://example.test/page2"},
        "https://example.test/page2": {"results": [{"matrix_id": "MA0002.1"}], "next": None},
        "https://jaspar.elixir.no/api/v1/matrix/MA0001.1/": {
            "matrix_id": "MA0001.1",
            "species": [{"tax_id": 3702}],
        },
        "https://jaspar.elixir.no/api/v1/matrix/MA0002.1/": {
            "matrix_id": "MA0002.1",
            "species": [{"tax_id": 9606}],
        },
    }
    monkeypatch.setattr(download, "_request_json", lambda url, **_kwargs: pages[url])
    destination = tmp_path / "matrices.json"

    artifact = download.download_jaspar(spec, destination)

    records = json.loads(destination.read_text(encoding="utf-8"))["results"]
    assert [record["matrix_id"] for record in records] == ["MA0001.1"]
    assert artifact["sha256"] == download.file_digest(destination)
    assert not destination.with_suffix(".json.part").exists()
