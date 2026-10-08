from pathlib import Path

import pytest

from plant_kg.adapters.araport import iter_genes
from plant_kg.adapters.dap_seq import GeneInterval, infer_targets, promoter_interval

FIXTURES = Path(__file__).parents[1] / "data" / "fixtures" / "raw"


def test_promoter_interval_is_strand_aware() -> None:
    plus = GeneInterval("AT1G00010", "Chr1", 5_000, 5_500, "+")
    minus = GeneInterval("AT1G00020", "Chr1", 8_000, 8_500, "-")

    assert promoter_interval(plus, upstream_bp=2_000, downstream_bp=500) == (3_000, 5_500)
    assert promoter_interval(minus, upstream_bp=2_000, downstream_bp=500) == (8_000, 10_500)


def test_dap_peaks_are_aggregated_into_putative_targets() -> None:
    genes = list(iter_genes(FIXTURES / "araport11.gff3"))
    peaks = FIXTURES / "DAPSeq-bHLH_tnt-bHLH34_col-chr1-5_GEM_events.narrowPeak"

    rows = list(infer_targets([peaks], genes))

    assert [(row["tf_gene_id"], row["target_gene_id"]) for row in rows] == [
        ("AT3G23210", "AT1G01580"),
        ("AT3G23210", "AT4G19690"),
    ]
    assert rows[0]["evidence"] == "promoter_overlap"
    assert rows[0]["assay"] == "DAP-seq"
    assert rows[0]["peak_count"] == 1


def test_ampdap_files_are_excluded(tmp_path: Path) -> None:
    genes = list(iter_genes(FIXTURES / "araport11.gff3"))
    ampdap = tmp_path / "DAPSeq-bHLH_tnt-bHLH34_colamp-chr1-5_GEM_events.narrowPeak"
    ampdap.write_text("Chr1\t49\t150\tpeak_1\t900\t.\t12.5\t8.0\t7.0\t50\n", encoding="utf-8")

    assert list(infer_targets([ampdap], genes)) == []


@pytest.mark.parametrize("sample", ["col", "col_a", "col_b"])
def test_geo_filename_variants_resolve_native_dap_tf(tmp_path: Path, sample: str) -> None:
    genes = list(iter_genes(FIXTURES / "araport11.gff3"))
    peak = tmp_path / f"GSM1925012_DAPSeq-bHLH_tnt-bHLH34_{sample}-chr1-5_GEM_events.narrowPeak"
    peak.write_text("Chr1\t49\t150\tpeak_1\t900\t.\t12.5\t8.0\t7.0\t50\n", encoding="utf-8")

    rows = list(infer_targets([peak], genes))

    assert len(rows) == 1
    assert rows[0]["tf_gene_id"] == "AT3G23210"
    assert rows[0]["source_file"] == peak.name
