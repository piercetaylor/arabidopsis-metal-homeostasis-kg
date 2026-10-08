# ADR 0002: Derive putative DAP targets by promoter overlap

- **Status:** Accepted
- **Date:** 2026-09-30

## Context

GEO GSE60141 provides DAP-seq binding peaks, not a canonical table of experimentally
validated target genes. A graph edge is useful for traversal, but assigning a nearby
gene to a peak is a computational interpretation rather than a direct observation of
regulation.

## Decision

Derive a `PUTATIVE_DAP_TARGET` relationship when a native-genome DAP-seq peak overlaps
a strand-aware interval extending 2,000 bp upstream through 500 bp downstream of an
Araport11 transcription start site. Convert narrowPeak coordinates before comparison,
exclude ampDAP-seq files, and aggregate qualifying peaks by TF-target pair and source file.
Store the method, window sizes, peak count, maximum signal, maximum q-value field,
source filename, and dataset identifier on the normalized row/relationship.

## Consequences

- The inference is deterministic and reviewable.
- The edge name communicates uncertainty and avoids claiming functional regulation.
- Different promoter windows or gene annotations can produce different target sets.
- Distal enhancers and chromatin context are not modeled.
- Aggregation keeps the graph manageable but does not preserve every peak as a node.
