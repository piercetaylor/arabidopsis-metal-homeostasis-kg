"""Typed access to the public-source manifest."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceSpec:
    key: str
    dataset_id: str
    name: str
    version: str
    url: str
    filename: str
    license: str
    citation: str
    md5: str | None = None


def load_sources(path: Path) -> tuple[SourceSpec, ...]:
    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    return tuple(SourceSpec(key=key, **values) for key, values in payload.items())
