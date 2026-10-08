# ADR 0003: Download upstream data instead of redistributing it

- **Status:** Accepted
- **Date:** 2026-09-30

## Context

The four upstream resources have different terms, file sizes, and update mechanisms.
JASPAR and InterATOME state open licenses; public availability of another source does
not necessarily grant permission to relicense it. Committing large upstream files
would also inflate Git history and obscure exactly how an analysis acquired them.

## Decision

Commit source declarations, adapters, provenance documentation, and small hand-authored
fixtures. Download full artifacts into ignored local storage at run time. Record URL,
retrieval time, byte size, and SHA-256 in a local download manifest. Keep normalized
full-data tables out of Git as well. Apply the repository's MIT license only to the
project code and documentation.

## Consequences

- The public repository remains small and does not redistribute third-party datasets.
- Users must have network access for a first full build and remain responsible for
  complying with source terms.
- Upstream downtime can block a new full build.
- Mutable API responses require manifest review and digest comparison for exact
  reproduction.
- Continuous integration uses only fixtures and never depends on live data hosts.
