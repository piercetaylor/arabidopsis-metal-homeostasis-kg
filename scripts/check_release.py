"""Inspect distribution contents and write SHA-256 checksums for release assets."""

from __future__ import annotations

import argparse
import hashlib
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath

REQUIRED = {
    "config/sources.toml",
    "config/metal_focus.tsv",
    "cypher/constraints.cypher",
    "cypher/indexes.cypher",
    "cypher/validation/01_required_entities.cypher",
    "cypher/validation/02_identifier_integrity.cypher",
    "cypher/validation/03_provenance_integrity.cypher",
    "cypher/validation/04_relationship_integrity.cypher",
    "data/fixtures/raw/araport11.gff3",
    "data/fixtures/raw/jaspar_arabidopsis.json",
    "data/fixtures/raw/interatome.tsv",
    "data/fixtures/raw/DAPSeq-bHLH_tnt-bHLH34_col-chr1-5_GEM_events.narrowPeak",
    "data/README.md",
    "docs/data-provenance.md",
}
FORBIDDEN = {".git", ".venv", "out", "neo4j_data", "neo4j_logs", "__pycache__"}


def check_paths(names: set[str], required: set[str]) -> None:
    missing = required - names
    if missing:
        raise ValueError(f"Missing release resources: {sorted(missing)}")
    for name in names:
        parts = PurePosixPath(name).parts
        if (
            PurePosixPath(name).is_absolute()
            or "\\" in name
            or ":" in name
            or ".." in parts
            or FORBIDDEN.intersection(parts)
            or any(part.startswith(".pytest") for part in parts)
            or any(
                part == ".env" or part.startswith(".env.")
                for part in parts
                if part != ".env.example"
            )
            or "data/raw/" in name
            or "data/processed/" in name
        ):
            raise ValueError(f"Local state or unsafe path in distribution: {name}")


def check_wheel(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        check_paths(names, {f"plant_kg/resources/{name}" for name in REQUIRED})
        metadata_paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_paths) != 1:
            raise ValueError("Wheel must contain one metadata record.")
        metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        if metadata["Name"] != "arabidopsis-metal-homeostasis-kg":
            raise ValueError("Unexpected distribution name.")
        if metadata["License-Expression"] != "MIT":
            raise ValueError("Missing MIT license expression.")
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in names):
            raise ValueError("Missing code license.")
        return str(metadata["Version"])


def check_sdist(path: Path, version: str) -> None:
    prefix = f"arabidopsis_metal_homeostasis_kg-{version}/"
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        if any(not member.name.startswith(prefix) for member in members):
            raise ValueError("Unexpected source distribution root.")
        if any(member.issym() or member.islnk() for member in members):
            raise ValueError("Links are not permitted in the source distribution.")
        names = {member.name.removeprefix(prefix) for member in members if member.isfile()}
        check_paths(names, REQUIRED | {"pyproject.toml", "LICENSE", "CHANGELOG.md"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", type=Path, nargs="?", default=Path("dist"))
    args = parser.parse_args()
    wheels = list(args.dist.glob("*.whl"))
    sdists = list(args.dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("Use a clean directory containing exactly one wheel and one sdist.")
    version = check_wheel(wheels[0])
    check_sdist(sdists[0], version)
    lines = []
    for artifact in sorted([*wheels, *sdists]):
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        lines.append(f"{digest}  {artifact.name}")
    (args.dist / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Release {version}: resource, license and distribution checks passed.")


if __name__ == "__main__":
    main()
