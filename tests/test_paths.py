from pathlib import Path

import pytest

from plant_kg import paths


def test_checkout_resources(tmp_path: Path) -> None:
    package = tmp_path / "src/plant_kg"
    package.mkdir(parents=True)
    (tmp_path / "config").mkdir()
    (tmp_path / "config/sources.toml").touch()
    assert paths.resource_root(package) == tmp_path


def test_bundled_resources_take_precedence(tmp_path: Path) -> None:
    package = tmp_path / "site-packages/plant_kg"
    bundled = package / "resources"
    (bundled / "config").mkdir(parents=True)
    (bundled / "config/sources.toml").touch()
    assert paths.resource_root(package) == bundled


def test_missing_resources_fail_clearly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="reinstall"):
        paths.resource_root(tmp_path / "site-packages/plant_kg")


def test_wheel_outputs_use_working_directory(tmp_path: Path, monkeypatch) -> None:
    bundled = tmp_path / "resources"
    bundled.mkdir()
    workspace = tmp_path / "analysis"
    workspace.mkdir()
    monkeypatch.setattr(paths, "RESOURCE_ROOT", bundled)
    monkeypatch.chdir(workspace)
    assert paths.workspace_root() == workspace


def test_checkout_outputs_stay_in_checkout(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "pyproject.toml").touch()
    monkeypatch.setattr(paths, "RESOURCE_ROOT", tmp_path)
    assert paths.workspace_root() == tmp_path
