# Full-data verification

Verified on October 7, 2026 using the public input snapshot in
[source-snapshot.json](source-snapshot.json). Full source files and normalized
tables are stored locally under the ignored data directories.

The build downloaded all four sources, normalized their records, applied the
uniqueness constraints, loaded a clean Neo4j 5.26 Community instance, and ran the
version-controlled validation and example queries.

## Normalized records

| Table | Rows |
|---|---:|
| Datasets | 4 |
| Araport11 genes | 33,318 |
| JASPAR Arabidopsis motifs | 598 |
| Exact gene-to-motif mappings | 332 |
| Putative DAP-seq targets, per source file | 1,172,835 |
| InterATOME AI-1 Y2H pairs, including homodimers | 6,438 |
| Metal-homeostasis query seeds | 4 |

The loaded graph contains **33,921 nodes** and **1,213,525 relationships**.
The DAP counts describe promoter-overlap inferences; the Y2H counts describe the
InterATOME `AI1` subset and should not be interpreted as a reproduction of a
different interaction-map release.

## Validation and example queries

All four validation suites returned zero violations:

- Required graph entities
- Identifier and coordinate integrity
- Dataset provenance integrity
- Relationship endpoint and property integrity

All three example queries executed successfully:

| Query | Result rows |
|---|---:|
| `convergent_evidence.cypher` | 40 |
| `metal_regulatory_neighborhood.cypher` | 191 |
| `motif_supported_regulators.cypher` | 61 |

The four query seeds collectively have 111 distinct putative DAP-seq regulators
in this snapshot. These paths join assay evidence and a declared query lens;
they do not establish regulation or protein interaction in a living plant.

## Reproduction

Follow the full-data commands in the [README](../../README.md). Compare the
download manifest against the recorded snapshot before comparing row counts.
The JASPAR API serves the current release, so later downloads may differ.

The fixture suite is independent of upstream network availability. Local checks
passed 19 unit tests and two Neo4j integration tests, including an idempotent
second fixture load and deliberate missing-property failures. GitHub Actions
repeats those checks on each push and pull request.
