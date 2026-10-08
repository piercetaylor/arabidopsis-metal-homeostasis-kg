"""JASPAR CORE motif adapter."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

MOTIF_ID = re.compile(r"^MA\d{4}\.\d+$")
BASES = ("A", "C", "G", "T")


def consensus_from_pfm(pfm: Mapping[str, Sequence[int]]) -> str:
    """Return a deterministic maximum-frequency consensus sequence."""

    lengths = {len(pfm[base]) for base in BASES}
    if len(lengths) != 1:
        raise ValueError("PFM rows must have equal lengths")
    length = lengths.pop()
    return "".join(
        max(BASES, key=lambda base: (int(pfm[base][index]), -BASES.index(base)))
        for index in range(length)
    )


def normalize_motifs(
    path: Path, genes: Iterable[Mapping[str, object]]
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Normalize Arabidopsis motifs and exact Araport symbol crosswalks."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    source = str(payload.get("source", "JASPAR CORE"))
    symbol_to_gene = {
        str(row["symbol"]).casefold(): str(row["gene_id"]) for row in genes if row.get("symbol")
    }
    motifs: list[dict[str, object]] = []
    mappings: list[dict[str, str]] = []
    for record in payload.get("results", []):
        motif_id = str(record["matrix_id"])
        if not MOTIF_ID.fullmatch(motif_id):
            raise ValueError(f"Invalid JASPAR matrix identifier: {motif_id}")
        species = record.get("species", [])
        tax_ids = {int(item["tax_id"]) for item in species}
        if 3702 not in tax_ids:
            continue
        name = str(record["name"])
        motifs.append(
            {
                "motif_id": motif_id,
                "name": name,
                "collection": str(record["collection"]),
                "tax_group": str(record["tax_group"]),
                "species_tax_id": 3702,
                "consensus": consensus_from_pfm(record["pfm"]),
                "data_type": str(record.get("data_type", "")),
                "matrix_url": f"https://jaspar.elixir.no/matrix/{motif_id}/",
                "source": source,
            }
        )
        gene_id = symbol_to_gene.get(name.casefold())
        if gene_id:
            mappings.append(
                {
                    "gene_id": gene_id,
                    "motif_id": motif_id,
                    "mapping_method": "exact_araport_symbol",
                }
            )
    motifs.sort(key=lambda row: str(row["motif_id"]))
    mappings.sort(key=lambda row: (row["gene_id"], row["motif_id"]))
    return motifs, mappings
