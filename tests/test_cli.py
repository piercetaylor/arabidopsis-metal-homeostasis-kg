import csv
from pathlib import Path

from plant_kg.cli import main

FIXTURES = Path(__file__).parents[1] / "data" / "fixtures" / "raw"


def test_prepare_fixture_command_runs_the_normalization_seam(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "prepare",
            "--profile",
            "fixture",
            "--raw-dir",
            str(FIXTURES),
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert '"dap_targets": 2' in capsys.readouterr().out
    with (tmp_path / "motifs.csv").open(encoding="utf-8", newline="") as handle:
        assert next(csv.DictReader(handle))["motif_id"] == "MA0962.2"
