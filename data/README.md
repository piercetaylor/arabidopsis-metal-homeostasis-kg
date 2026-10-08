# Data directories

This repository separates upstream downloads, generated tables, and test fixtures.

| Path | Contents | Tracked by Git |
|---|---|---|
| `data/raw/` | Full files retrieved by `plant-kg download`, plus `download-manifest.json` | No |
| `data/processed/` | Normalized full-profile CSV tables | No |
| `data/fixtures/raw/` | Small hand-authored, source-shaped inputs | Yes |
| `data/fixtures/generated/` | Optional generated fixture tables | No |

The test fixtures use plausible formats and real-style AGI identifiers so that parser,
coordinate, and graph behavior can be exercised. Their relationships, values, and
scores are synthetic. They are not excerpts of the source datasets, are not evidence
for biological claims, and must not be used for scientific analysis.

Run the fixture workflow without network access:

```bash
plant-kg prepare --profile fixture
```

For full data, read [data provenance](../docs/data-provenance.md), review the source
terms, and then run:

```bash
plant-kg download
plant-kg prepare --profile full
```

Do not force-add ignored upstream or generated files. Preserve the generated download
manifest with analysis outputs when exact input provenance matters.
