"""Araport11 GFF3 adapter."""

from __future__ import annotations

import gzip
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO
from urllib.parse import unquote


@contextmanager
def _open_text(path: Path) -> Iterator[TextIO]:
    if path.suffix == ".gz":
        with gzip.open(path, mode="rt", encoding="utf-8", errors="backslashreplace") as handle:
            yield handle
    else:
        with path.open(encoding="utf-8", errors="backslashreplace") as handle:
            yield handle


def parse_attributes(raw: str) -> dict[str, str]:
    """Parse a GFF3 attribute column without discarding escaped characters."""

    attributes: dict[str, str] = {}
    for field in raw.rstrip(";").split(";"):
        if not field or "=" not in field:
            continue
        key, value = field.split("=", 1)
        attributes[unquote(key)] = unquote(value)
    return attributes


def iter_genes(path: Path) -> Iterator[dict[str, str | int]]:
    """Yield normalized locus-level gene rows from an Araport11 GFF3 file."""

    with _open_text(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip() or line.startswith("#"):
                continue
            columns = line.rstrip("\n").split("\t")
            if len(columns) != 9:
                raise ValueError(f"{path}:{line_number}: expected 9 GFF3 columns")
            chromosome, source, feature, start, end, _score, strand, _phase, raw_attrs = columns
            if feature != "gene":
                continue
            attrs = parse_attributes(raw_attrs)
            gene_id = attrs.get("ID", "").upper()
            if not gene_id:
                raise ValueError(f"{path}:{line_number}: gene feature has no ID")
            yield {
                "gene_id": gene_id,
                "symbol": attrs.get("symbol", attrs.get("Symbol", "")),
                "name": attrs.get("Name", gene_id),
                "chromosome": chromosome,
                "start": int(start),
                "end": int(end),
                "strand": strand,
                "biotype": attrs.get("biotype", attrs.get("locus_type", "")),
                "description": attrs.get("Note", ""),
                "source": source,
            }
