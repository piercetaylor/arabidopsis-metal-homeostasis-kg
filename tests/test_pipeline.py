import csv
import shutil
import tarfile
from pathlib import Path

from plant_kg.pipeline import build_fixture, build_full
from plant_kg.sources import load_sources

FIXTURES = Path(__file__).parents[1] / "data" / "fixtures" / "raw"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_fixture_pipeline_writes_deterministic_graph_tables(tmp_path: Path) -> None:
    counts = build_fixture(FIXTURES, tmp_path)

    assert counts == {
        "datasets": 4,
        "genes": 4,
        "motifs": 1,
        "tf_motifs": 1,
        "dap_targets": 2,
        "y2h_interactions": 2,
        "metal_focus": 4,
    }
    assert [row["gene_id"] for row in _read(tmp_path / "genes.csv")] == [
        "AT1G01580",
        "AT2G28160",
        "AT3G23210",
        "AT4G19690",
    ]
    assert _read(tmp_path / "dap_targets.csv")[0]["dataset_id"] == "geo-gse60141"
    assert _read(tmp_path / "y2h_interactions.csv")[0]["dataset_id"] == "interatome-1.1"


def test_full_build_preserves_custom_source_provenance(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    manifest = tmp_path / "sources.toml"
    original = (FIXTURES.parents[2] / "config/sources.toml").read_text(encoding="utf-8")
    manifest.write_text(
        original.replace("araport11-20241001", "araport11-local")
        .replace("geo-gse60141", "geo-local")
        .replace("jaspar-2026-core-arabidopsis", "jaspar-local")
        .replace("interatome-1.1", "y2h-local")
        .replace(
            "https://zenodo.org/records/17371665/files/",
            "https://example.org/mirror/",
        ),
        encoding="utf-8",
    )
    sources = {source.key: source for source in load_sources(manifest)}
    # Plain fixtures retain their own filenames; the manifest controls every input path.
    content = manifest.read_text(encoding="utf-8").replace(
        sources["araport11"].filename, "araport11.gff3"
    )
    manifest.write_text(content, encoding="utf-8")
    sources = {source.key: source for source in load_sources(manifest)}
    for key, name in (
        ("araport11", "araport11.gff3"),
        ("jaspar", "jaspar_arabidopsis.json"),
        ("y2h", "interatome.tsv"),
    ):
        shutil.copyfile(FIXTURES / name, raw / sources[key].filename)
    with tarfile.open(raw / sources["dap_seq"].filename, "w") as archive:
        peak = next(FIXTURES.glob("*.narrowPeak"))
        archive.add(peak, arcname=peak.name)

    output = tmp_path / "processed"
    counts = build_full(raw, output, manifest)

    assert counts["dap_targets"] == 2
    assert {row["dataset_id"] for row in _read(output / "genes.csv")} == {"araport11-local"}
    annotation = next(row for row in _read(output / "datasets.csv") if "Araport" in row["name"])
    assert annotation["dataset_id"] == "araport11-local"
    assert annotation["source_url"].startswith("https://example.org/mirror/")
    for table, expected in (
        ("dap_targets", "geo-local"),
        ("motifs", "jaspar-local"),
        ("tf_motifs", "jaspar-local"),
        ("y2h_interactions", "y2h-local"),
    ):
        assert {row["dataset_id"] for row in _read(output / f"{table}.csv")} == {expected}
