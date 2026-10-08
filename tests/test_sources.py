from pathlib import Path

from plant_kg.sources import load_sources

PROJECT_ROOT = Path(__file__).parents[1]


def test_public_source_manifest_is_complete_and_citable() -> None:
    sources = load_sources(PROJECT_ROOT / "config/sources.toml")

    assert {source.key for source in sources} == {"araport11", "dap_seq", "jaspar", "y2h"}
    assert all(source.url.startswith("https://") for source in sources)
    assert all(source.license and source.citation for source in sources)
    assert next(source for source in sources if source.key == "jaspar").license == "CC BY 4.0"
    assert "Ouverte 2.0" in next(source for source in sources if source.key == "y2h").license
