# Changelog

## 0.1.0 (release candidate)

First public release candidate.

- Integrates Araport11 genes, native-genome DAP-seq promoter overlaps, JASPAR
  motifs and InterATOME AI-1 Y2H observations in Neo4j.
- Includes an offline fixture, source download manifests, uniqueness constraints,
  integrity checks and three example Cypher queries.
- Packages the fixture, configuration, Cypher files and data attribution with
  the CLI. Installed packages write analysis outputs to the working directory.
- Tests parsers, normalization, graph validation and repeated-load idempotence.
  CI also builds and exercises the installed wheel outside the checkout.

DAP-seq targets are putative binding relationships. Y2H endpoints are gene-locus
protein proxies, and the iron-homeostasis seeds are a small query lens.
Full source datasets are downloaded on demand, not distributed with the release.
