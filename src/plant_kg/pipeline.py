"""Normalize public-source-shaped inputs into graph-ready CSV tables."""

from __future__ import annotations

import csv
import tarfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from plant_kg.adapters.araport import iter_genes
from plant_kg.adapters.dap_seq import infer_targets
from plant_kg.adapters.jaspar import normalize_motifs
from plant_kg.adapters.y2h import normalize_interactions
from plant_kg.sources import SourceSpec, load_sources

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _build_tables(
    *,
    araport_path: Path,
    dap_paths: Sequence[Path],
    jaspar_path: Path,
    y2h_path: Path,
    output_dir: Path,
    sources: Sequence[SourceSpec],
) -> dict[str, int]:
    source_by_key = {source.key: source for source in sources}
    genes = list(iter_genes(araport_path))
    for row in genes:
        row["dataset_id"] = source_by_key["araport11"].dataset_id

    dap_rows = (
        {**row, "dataset_id": source_by_key["dap_seq"].dataset_id}
        for row in infer_targets(sorted(dap_paths), genes)
    )

    motifs, tf_motifs = normalize_motifs(jaspar_path, genes)
    for row in motifs:
        row["dataset_id"] = source_by_key["jaspar"].dataset_id
    for row in tf_motifs:
        row["dataset_id"] = source_by_key["jaspar"].dataset_id

    y2h_rows = normalize_interactions(y2h_path, genes)
    for row in y2h_rows:
        row["dataset_id"] = source_by_key["y2h"].dataset_id

    focus = _read_tsv(PROJECT_ROOT / "config" / "metal_focus.tsv")
    known_ids = {str(row["gene_id"]) for row in genes}
    focus = [row for row in focus if row["gene_id"] in known_ids]

    datasets = [
        {
            "dataset_id": spec.dataset_id,
            "name": spec.name,
            "version": spec.version,
            "source_url": spec.url,
            "license": spec.license,
            "citation": spec.citation,
        }
        for spec in sources
    ]

    counts = {
        "datasets": _write_csv(
            output_dir / "datasets.csv",
            ["dataset_id", "name", "version", "source_url", "license", "citation"],
            datasets,
        ),
        "genes": _write_csv(
            output_dir / "genes.csv",
            [
                "gene_id",
                "symbol",
                "name",
                "chromosome",
                "start",
                "end",
                "strand",
                "biotype",
                "description",
                "source",
                "dataset_id",
            ],
            genes,
        ),
        "motifs": _write_csv(
            output_dir / "motifs.csv",
            [
                "motif_id",
                "name",
                "collection",
                "tax_group",
                "species_tax_id",
                "consensus",
                "data_type",
                "matrix_url",
                "source",
                "dataset_id",
            ],
            motifs,
        ),
        "tf_motifs": _write_csv(
            output_dir / "tf_motifs.csv",
            ["gene_id", "motif_id", "mapping_method", "dataset_id"],
            tf_motifs,
        ),
        "dap_targets": _write_csv(
            output_dir / "dap_targets.csv",
            [
                "tf_gene_id",
                "target_gene_id",
                "assay",
                "evidence",
                "peak_count",
                "max_signal",
                "max_q_value",
                "promoter_upstream_bp",
                "promoter_downstream_bp",
                "source_file",
                "dataset_id",
            ],
            dap_rows,
        ),
        "y2h_interactions": _write_csv(
            output_dir / "y2h_interactions.csv",
            [
                "gene_a_id",
                "gene_b_id",
                "assay",
                "evidence",
                "publication_id",
                "source",
                "dataset_id",
            ],
            y2h_rows,
        ),
        "metal_focus": _write_csv(
            output_dir / "metal_focus.csv",
            ["gene_id", "metal", "evidence_url", "scope_note"],
            focus,
        ),
    }
    return counts


def build_fixture(
    raw_dir: Path,
    output_dir: Path,
    sources_path: Path = PROJECT_ROOT / "config" / "sources.toml",
) -> dict[str, int]:
    """Build deterministic normalized tables from small source-shaped fixtures."""

    return _build_tables(
        araport_path=raw_dir / "araport11.gff3",
        dap_paths=sorted(raw_dir.glob("*.narrowPeak*")),
        jaspar_path=raw_dir / "jaspar_arabidopsis.json",
        y2h_path=raw_dir / "interatome.tsv",
        output_dir=output_dir,
        sources=load_sources(sources_path),
    )


def _extract_dap_peaks(archive: Path, destination: Path) -> tuple[Path, ...]:
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            member_name = Path(member.name).name
            if not member.isfile() or not member_name.endswith((".narrowPeak", ".narrowPeak.gz")):
                continue
            target = destination / member_name
            source = tar.extractfile(member)
            if source is None:
                continue
            with source, target.open("wb") as handle:
                while chunk := source.read(1024 * 1024):
                    handle.write(chunk)
            extracted.append(target)
    if not extracted:
        raise ValueError(f"No narrowPeak files found in {archive}")
    return tuple(sorted(extracted))


def build_full(raw_dir: Path, output_dir: Path, sources_path: Path) -> dict[str, int]:
    """Normalize all previously downloaded public datasets."""

    sources = load_sources(sources_path)
    specs = {spec.key: spec for spec in sources}
    peaks = _extract_dap_peaks(raw_dir / specs["dap_seq"].filename, raw_dir / "dap_peaks")
    return _build_tables(
        araport_path=raw_dir / specs["araport11"].filename,
        dap_paths=peaks,
        jaspar_path=raw_dir / specs["jaspar"].filename,
        y2h_path=raw_dir / specs["y2h"].filename,
        output_dir=output_dir,
        sources=sources,
    )
