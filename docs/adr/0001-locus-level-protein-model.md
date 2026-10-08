# ADR 0001: Represent proteins with locus-level gene proxies

- **Status:** Accepted
- **Date:** 2026-09-30

## Context

Araport11 gene annotation and the regulatory layers are keyed naturally by AGI locus.
The public InterATOME table can include transcript-style identifiers, but the current
pipeline does not have a complete, versioned isoform crosswalk shared by all four
sources. Creating isoform-specific `Protein` nodes would imply precision that the
integrated inputs do not consistently support.

## Decision

Use one `Gene` node per canonical AGI locus as the endpoint for motif, DAP-seq, and
Y2H relationships. Strip transcript suffixes during Y2H normalization and treat a
Y2H `Gene` endpoint as a locus-level protein proxy. Do not create a separate
`Protein` label in this version of the graph.

## Consequences

- Cross-source joins are deterministic and require no guessed isoform mappings.
- Graph queries remain compact and use one stable identifier scheme.
- Isoform-specific interactions cannot be represented.
- Y2H relationships must not be interpreted as evidence for every protein isoform
  encoded by a locus.
- A future isoform-resolved model requires a versioned transcript/protein source and
  an explicit migration ADR.
