# Releasing

Version 0.1.0 is an alpha release candidate. The public-data build has been
verified, but the project is not a hosted database or a production deployment.
Release artifacts contain code, configuration, Cypher and the attributed test
fixture. They never contain full upstream datasets or a Neo4j database.

## Release checks

From a clean checkout, install the release tools and the tested runtime snapshot:

```bash
python -m pip install -c requirements-runtime.txt -e ".[dev,release]"
ruff format --check .
ruff check .
pytest -m "not integration"
python -m build
python -m twine check dist/*
python scripts/check_release.py dist
pip-audit --strict -r requirements-runtime.txt
```

Use an empty distribution directory when rebuilding. The content check requires
one wheel and one source archive, verifies required resources and licensing,
rejects local state, and writes `dist/SHA256SUMS`.

The package includes resources using Hatch's
[forced-inclusion configuration](https://hatch.pypa.io/latest/config/build/#forced-inclusion).
Wheel and source metadata explicitly use version 2.4 for compatibility with
release tooling.

CI repeats these checks on Python 3.11 and 3.13. It installs the wheel, runs the
offline fixture CLI outside the checkout, and tests graph loading and validation
against its disposable Neo4j service. The successful Python 3.11 job retains a
`release-candidate` artifact for 14 days.

Before publishing, check that:

- CI is green for the exact commit being tagged.
- The version agrees in `pyproject.toml`, `plant_kg.__version__` and `CITATION.cff`.
- The changelog and citation release date match the release.
- Source citations and fixture reuse notices remain in the archives.
- Git contains no credentials, raw downloads, generated full-data tables or local
  database state. Private vulnerability reporting is enabled on GitHub.

Publishing requires an explicit decision from the repository owner. Tag the
verified commit as `v0.1.0`, create a GitHub Release with the changelog entry, and
attach the wheel, source archive and `SHA256SUMS` from the same successful CI run.
This procedure does not publish to PyPI.

## Installing the wheel

Download and verify the wheel against `SHA256SUMS`, then install it in a virtual
environment:

```bash
python -m pip install arabidopsis_metal_homeostasis_kg-0.1.0-py3-none-any.whl
plant-kg --version
plant-kg prepare --profile fixture
```

Installed wheels read bundled inputs but write `data/raw/` and
`data/processed/` beneath the current directory. Editable installs keep those
outputs in the checkout. Use `--raw-dir` and `--output-dir` to choose other
locations. Neo4j must be running before graph commands can connect; the source
archive includes the local Compose configuration.

## If a release fails

Do not move an already published tag. Mark the faulty release as a prerelease or
withdraw its affected assets, describe the problem in the changelog, and issue a
new patch version after CI passes. Reinstall a known-good version in a fresh
environment. Keep analysis manifests and database volumes; never delete them as
part of a software rollback.

For changed graph semantics, build a separate empty database and compare the
validation and query results before switching analyses to it.
