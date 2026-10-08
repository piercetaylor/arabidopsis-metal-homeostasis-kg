"""Batched, idempotent loading of normalized CSV tables into Neo4j."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LoadStats:
    table: str
    rows: int


QUERIES = {
    "datasets": """
        UNWIND $rows AS row
        MERGE (d:Dataset {dataset_id: row.dataset_id})
        SET d.name = row.name, d.version = row.version, d.source_url = row.source_url,
            d.license = row.license, d.citation = row.citation
    """,
    "genes": """
        UNWIND $rows AS row
        MERGE (g:Gene {gene_id: row.gene_id})
        SET g.symbol = row.symbol, g.name = row.name, g.chromosome = row.chromosome,
            g.start = toInteger(row.start), g.end = toInteger(row.end), g.strand = row.strand,
            g.biotype = row.biotype, g.description = row.description, g.source = row.source,
            g.dataset_id = row.dataset_id
        WITH g, row MATCH (d:Dataset {dataset_id: row.dataset_id})
        MERGE (g)-[:FROM_DATASET]->(d)
    """,
    "motifs": """
        UNWIND $rows AS row
        MERGE (m:Motif {motif_id: row.motif_id})
        SET m.name = row.name, m.collection = row.collection, m.tax_group = row.tax_group,
            m.species_tax_id = toInteger(row.species_tax_id), m.consensus = row.consensus,
            m.data_type = row.data_type, m.matrix_url = row.matrix_url, m.source = row.source,
            m.dataset_id = row.dataset_id
        WITH m, row MATCH (d:Dataset {dataset_id: row.dataset_id})
        MERGE (m)-[:FROM_DATASET]->(d)
    """,
    "metal_focus": """
        UNWIND $rows AS row
        MATCH (g:Gene {gene_id: row.gene_id})
        MERGE (metal:Metal {name: row.metal})
        MERGE (g)-[r:ASSOCIATED_WITH_HOMEOSTASIS]->(metal)
        SET r.evidence_url = row.evidence_url, r.scope_note = row.scope_note
    """,
    "tf_motifs": """
        UNWIND $rows AS row
        MATCH (g:Gene {gene_id: row.gene_id}), (m:Motif {motif_id: row.motif_id})
        MERGE (g)-[r:HAS_MOTIF {dataset_id: row.dataset_id}]->(m)
        SET r.mapping_method = row.mapping_method
    """,
    "dap_targets": """
        UNWIND $rows AS row
        MATCH (tf:Gene {gene_id: row.tf_gene_id}),
              (target:Gene {gene_id: row.target_gene_id})
        MERGE (tf)-[r:PUTATIVE_DAP_TARGET {
            dataset_id: row.dataset_id, source_file: row.source_file
        }]->(target)
        SET r.assay = row.assay, r.evidence = row.evidence,
            r.peak_count = toInteger(row.peak_count), r.max_signal = toFloat(row.max_signal),
            r.max_q_value = toFloat(row.max_q_value),
            r.promoter_upstream_bp = toInteger(row.promoter_upstream_bp),
            r.promoter_downstream_bp = toInteger(row.promoter_downstream_bp),
            r.source_file = row.source_file
    """,
    "y2h_interactions": """
        UNWIND $rows AS row
        MATCH (a:Gene {gene_id: row.gene_a_id}), (b:Gene {gene_id: row.gene_b_id})
        MERGE (a)-[r:Y2H_INTERACTS_WITH {
            dataset_id: row.dataset_id, evidence: row.evidence
        }]->(b)
        SET r.assay = row.assay, r.publication_id = row.publication_id, r.source = row.source
    """,
}

LOAD_ORDER = (
    "datasets",
    "genes",
    "motifs",
    "metal_focus",
    "tf_motifs",
    "dap_targets",
    "y2h_interactions",
)


def _read_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def _batches(rows: Iterable[dict[str, str]], size: int) -> Iterator[list[dict[str, str]]]:
    batch: list[dict[str, str]] = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def load_graph(
    driver: Any, data_dir: Path, *, database: str = "neo4j", batch_size: int = 1_000
) -> tuple[LoadStats, ...]:
    """Load all graph tables; repeated calls preserve graph cardinality."""

    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    stats: list[LoadStats] = []
    with driver.session(database=database) as session:
        for table in LOAD_ORDER:
            path = data_dir / f"{table}.csv"
            if not path.is_file():
                raise FileNotFoundError(f"Missing normalized table: {path}")
            row_count = 0
            for batch in _batches(_read_rows(path), batch_size):
                session.run(QUERIES[table], rows=batch).consume()
                row_count += len(batch)
            stats.append(LoadStats(table, row_count))
    return tuple(stats)
