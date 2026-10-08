# Contributing

Thank you for helping improve this project. Contributions that strengthen
reproducibility, biological interpretation, testing, documentation, or data-source
adapters are welcome.

## Development setup

Use Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For graph integration work, start the pinned local Neo4j service:

```bash
cp .env.example .env
docker compose up -d --wait
plant-kg pipeline --profile fixture
```

## Before opening a pull request

Run the code checks before opening a pull request:

```bash
ruff format --check .
ruff check .
pytest -m "not integration"
NEO4J_TEST_ALLOW_RESET=1 pytest -m integration
```

Pull requests should explain the behavioral change, identify any altered data
contracts, and add or update tests. Keep changes focused and avoid committing raw
downloads, generated full-data tables, credentials, or local Neo4j state.

Integration tests clear the configured database. Use a disposable instance and
explicitly enable the reset. In PowerShell set `$env:NEO4J_TEST_ALLOW_RESET='1'`.

Changes to packaging or bundled resources also need the
[release checks](docs/releasing.md). CI builds the distributions, installs the wheel
outside the checkout, audits runtime dependencies and runs the fixture graph workflow.

## Scientific changes

Changes to source selection or biological inference rules require particular care:

1. Link a stable primary source and state its reuse terms.
2. Record the exact version or accession and expected file format.
3. Keep upstream files in `data/raw/`; do not vendor them.
4. Add a small, hand-authored, source-shaped fixture that does not reproduce a
   material portion of the source dataset.
5. Test coordinate systems, identifier normalization, filtering, and edge semantics.
6. Update `docs/data-provenance.md`, `docs/data-dictionary.md`, and an ADR when a
   durable design decision changes.

Do not describe DAP-seq promoter overlaps as validated regulatory relationships.
Do not resolve gene aliases or motif mappings by fuzzy matching without explicit,
reviewable evidence.

## Reporting issues

For a reproducible bug report, include the command, operating system, Python
version, exception text, and whether the fixture or full profile was used. Do not
attach licensed upstream datasets or secrets. Report security concerns according to
[SECURITY.md](SECURITY.md).

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
