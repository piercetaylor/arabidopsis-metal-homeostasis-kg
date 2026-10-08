"""Arabidopsis ORFeome/AI-1 Y2H interaction adapter."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping
from pathlib import Path


def normalize_interactions(
    path: Path, genes: Iterable[Mapping[str, object]]
) -> list[dict[str, str]]:
    """Return unique, undirected AI-1 Y2H interactions with valid gene endpoints."""

    known_genes = {str(row["gene_id"]).upper() for row in genes}
    pairs: set[tuple[str, str]] = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"ida", "idb", "edge"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{path}: expected columns {sorted(required)}")
        for row in reader:
            if row["edge"].strip().upper() != "AI1":
                continue
            left = row["ida"].strip().upper().split(".", 1)[0]
            right = row["idb"].strip().upper().split(".", 1)[0]
            if left not in known_genes or right not in known_genes:
                continue
            pairs.add(tuple(sorted((left, right))))

    return [
        {
            "gene_a_id": left,
            "gene_b_id": right,
            "assay": "Y2H",
            "evidence": "AI1",
            "publication_id": "PMID:21798944",
            "source": "InterATOME",
        }
        for left, right in sorted(pairs)
    ]
