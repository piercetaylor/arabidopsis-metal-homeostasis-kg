from pathlib import Path

from plant_kg.adapters.araport import iter_genes

FIXTURES = Path(__file__).parents[1] / "data" / "fixtures" / "raw"


def test_araport_gene_features_are_normalized() -> None:
    genes = list(iter_genes(FIXTURES / "araport11.gff3"))

    assert genes == [
        {
            "gene_id": "AT1G01580",
            "symbol": "FRO2",
            "name": "FRO2",
            "chromosome": "Chr1",
            "start": 100,
            "end": 500,
            "strand": "+",
            "biotype": "protein_coding",
            "description": "ferric reduction oxidase 2",
            "source": "Araport11",
        },
        {
            "gene_id": "AT2G28160",
            "symbol": "FIT",
            "name": "FIT",
            "chromosome": "Chr2",
            "start": 1000,
            "end": 1600,
            "strand": "-",
            "biotype": "protein_coding",
            "description": "FER-like iron deficiency-induced transcription factor",
            "source": "Araport11",
        },
        {
            "gene_id": "AT3G23210",
            "symbol": "bHLH34",
            "name": "BHLH34",
            "chromosome": "Chr3",
            "start": 3000,
            "end": 3600,
            "strand": "+",
            "biotype": "protein_coding",
            "description": "basic helix-loop-helix transcription factor 34",
            "source": "Araport11",
        },
        {
            "gene_id": "AT4G19690",
            "symbol": "IRT1",
            "name": "IRT1",
            "chromosome": "Chr4",
            "start": 2000,
            "end": 2700,
            "strand": "+",
            "biotype": "protein_coding",
            "description": "iron-regulated transporter 1",
            "source": "Araport11",
        },
    ]


def test_legacy_annotation_bytes_are_preserved_as_escapes(tmp_path: Path) -> None:
    path = tmp_path / "legacy.gff3"
    path.write_bytes(
        b"Chr1\tAraport11\tgene\t1\t10\t.\t+\t.\t"
        b"ID=AT1G01010;symbol=NAC001;Note=legacy \x91text\x92\n"
    )

    gene = next(iter_genes(path))

    assert gene["gene_id"] == "AT1G01010"
    assert gene["description"] == r"legacy \x91text\x92"
