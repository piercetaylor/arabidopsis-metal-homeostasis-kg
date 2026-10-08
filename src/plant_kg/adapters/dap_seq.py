"""Convert DAP-seq narrowPeak files into putative TF-to-gene edges."""

from __future__ import annotations

import gzip
import re
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class GeneInterval:
    gene_id: str
    chromosome: str
    start: int
    end: int
    strand: str


def promoter_interval(
    gene: GeneInterval, *, upstream_bp: int = 2_000, downstream_bp: int = 500
) -> tuple[int, int]:
    """Return a one-based, closed, strand-aware promoter interval."""

    if gene.strand == "+":
        return max(1, gene.start - upstream_bp), gene.start + downstream_bp
    if gene.strand == "-":
        return max(1, gene.end - downstream_bp), gene.end + upstream_bp
    raise ValueError(f"Unsupported strand for {gene.gene_id}: {gene.strand!r}")


@contextmanager
def _open_text(path: Path) -> Iterator[TextIO]:
    if path.suffix == ".gz":
        with gzip.open(path, mode="rt", encoding="utf-8") as handle:
            yield handle
    else:
        with path.open(encoding="utf-8") as handle:
            yield handle


def _tf_token(path: Path) -> str | None:
    name = path.name.removesuffix(".gz")
    if re.search(r"_colamp-", name, flags=re.IGNORECASE):
        return None
    match = re.search(r"_(?:tnt|ecoli)-(.+?)_col(?:_[a-z0-9]+)?-", name, flags=re.IGNORECASE)
    if match is None:
        return None
    return match.group(1)


def _gene_indexes(
    genes: Iterable[Mapping[str, object]],
) -> tuple[list[tuple[GeneInterval, tuple[int, int]]], dict[str, str]]:
    intervals: list[tuple[GeneInterval, tuple[int, int]]] = []
    aliases: dict[str, str] = {}
    for row in genes:
        gene = GeneInterval(
            gene_id=str(row["gene_id"]),
            chromosome=str(row["chromosome"]),
            start=int(row["start"]),
            end=int(row["end"]),
            strand=str(row["strand"]),
        )
        intervals.append((gene, promoter_interval(gene)))
        for value in (row.get("gene_id"), row.get("symbol"), row.get("name")):
            if value:
                aliases[str(value).casefold()] = gene.gene_id
    return intervals, aliases


def infer_targets(
    peak_paths: Iterable[Path], genes: Iterable[Mapping[str, object]]
) -> Iterator[dict[str, object]]:
    """Aggregate promoter-overlapping DAP peaks into putative target edges."""

    intervals, aliases = _gene_indexes(genes)
    bin_size = 10_000
    interval_bins: dict[str, dict[int, list[tuple[GeneInterval, tuple[int, int]]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for item in intervals:
        chromosome = item[0].chromosome.casefold()
        promoter_start, promoter_end = item[1]
        for bin_number in range(promoter_start // bin_size, promoter_end // bin_size + 1):
            interval_bins[chromosome][bin_number].append(item)

    for path in sorted(peak_paths):
        tf_name = _tf_token(path)
        if tf_name is None:
            continue
        tf_gene_id = aliases.get(tf_name.casefold())
        if tf_gene_id is None:
            continue
        aggregates: dict[tuple[str, str], dict[str, object]] = {}
        with _open_text(path) as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip() or line.startswith(("#", "track", "browser")):
                    continue
                fields = line.rstrip("\n").split("\t")
                if len(fields) < 10:
                    raise ValueError(f"{path}:{line_number}: narrowPeak needs 10 columns")
                chromosome = fields[0]
                peak_start = int(fields[1]) + 1  # BED is zero-based, half-open.
                peak_end = int(fields[2])
                signal = float(fields[6])
                q_value = float(fields[8])
                candidates: dict[str, tuple[GeneInterval, tuple[int, int]]] = {}
                chromosome_bins = interval_bins.get(chromosome.casefold(), {})
                for bin_number in range(peak_start // bin_size, peak_end // bin_size + 1):
                    for candidate in chromosome_bins.get(bin_number, []):
                        candidates[candidate[0].gene_id] = candidate
                for target, (promoter_start, promoter_end) in candidates.values():
                    if peak_start > promoter_end or peak_end < promoter_start:
                        continue
                    key = (tf_gene_id, target.gene_id)
                    row = aggregates.setdefault(
                        key,
                        {
                            "tf_gene_id": tf_gene_id,
                            "target_gene_id": target.gene_id,
                            "assay": "DAP-seq",
                            "evidence": "promoter_overlap",
                            "peak_count": 0,
                            "max_signal": signal,
                            "max_q_value": q_value,
                            "promoter_upstream_bp": 2_000,
                            "promoter_downstream_bp": 500,
                            "source_file": path.name,
                        },
                    )
                    row["peak_count"] = int(row["peak_count"]) + 1
                    row["max_signal"] = max(float(row["max_signal"]), signal)
                    row["max_q_value"] = max(float(row["max_q_value"]), q_value)

        yield from (aggregates[key] for key in sorted(aggregates))
