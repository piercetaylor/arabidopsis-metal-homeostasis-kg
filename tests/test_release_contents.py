import runpy
import tomllib
from pathlib import Path

import pytest

from plant_kg import __version__

check_paths = runpy.run_path(str(Path(__file__).parents[1] / "scripts/check_release.py"))[
    "check_paths"
]


def test_release_versions_agree() -> None:
    root = Path(__file__).parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == __version__
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    assert f'version: "{__version__}"' in citation.splitlines()


def test_release_requires_declared_resources() -> None:
    with pytest.raises(ValueError, match="Missing release resources"):
        check_paths({"config/sources.toml"}, {"config/metal_focus.tsv"})


@pytest.mark.parametrize(
    "name",
    [
        ".env",
        ".env.production",
        "data/raw/upstream.tar",
        "data/processed/genes.csv",
        ".venv/secret.txt",
        "out/local.txt",
        "../escape",
        "/absolute",
        "C:/absolute",
        "data\\raw\\upstream.tar",
    ],
)
def test_release_rejects_local_state_and_unsafe_paths(name: str) -> None:
    with pytest.raises(ValueError, match="Local state or unsafe path"):
        check_paths({name}, set())


def test_release_allows_example_environment_and_fixture() -> None:
    allowed = {".env.example", "data/fixtures/raw/araport11.gff3"}
    check_paths(allowed, allowed)
