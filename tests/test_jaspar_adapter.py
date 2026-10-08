from pathlib import Path

from plant_kg.adapters.araport import iter_genes
from plant_kg.adapters.jaspar import normalize_motifs

FIXTURES = Path(__file__).parents[1] / "data" / "fixtures" / "raw"


def test_jaspar_motifs_and_explicit_symbol_links_are_normalized() -> None:
    genes = list(iter_genes(FIXTURES / "araport11.gff3"))

    motifs, mappings = normalize_motifs(FIXTURES / "jaspar_arabidopsis.json", genes)

    assert motifs == [
        {
            "motif_id": "MA0962.2",
            "name": "bHLH34",
            "collection": "CORE",
            "tax_group": "plants",
            "species_tax_id": 3702,
            "consensus": "GCACGTG",
            "data_type": "PBM",
            "matrix_url": "https://jaspar.elixir.no/matrix/MA0962.2/",
            "source": "JASPAR 2026 CORE",
        }
    ]
    assert mappings == [
        {
            "gene_id": "AT3G23210",
            "motif_id": "MA0962.2",
            "mapping_method": "exact_araport_symbol",
        }
    ]
