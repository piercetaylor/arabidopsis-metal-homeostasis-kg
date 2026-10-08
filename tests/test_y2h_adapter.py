from pathlib import Path

from plant_kg.adapters.araport import iter_genes
from plant_kg.adapters.y2h import normalize_interactions

FIXTURES = Path(__file__).parents[1] / "data" / "fixtures" / "raw"


def test_ai1_y2h_edges_are_filtered_canonicalized_and_deduplicated() -> None:
    genes = list(iter_genes(FIXTURES / "araport11.gff3"))

    rows = normalize_interactions(FIXTURES / "interatome.tsv", genes)

    assert rows == [
        {
            "gene_a_id": "AT2G28160",
            "gene_b_id": "AT2G28160",
            "assay": "Y2H",
            "evidence": "AI1",
            "publication_id": "PMID:21798944",
            "source": "InterATOME",
        },
        {
            "gene_a_id": "AT2G28160",
            "gene_b_id": "AT3G23210",
            "assay": "Y2H",
            "evidence": "AI1",
            "publication_id": "PMID:21798944",
            "source": "InterATOME",
        },
    ]
