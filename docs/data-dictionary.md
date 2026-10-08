# Data dictionary

All normalized files are UTF-8 CSV with a header row and LF line endings. Empty
strings represent missing optional values. Coordinates in normalized gene records are
one-based and closed. AGI identifiers are uppercase locus IDs without transcript
suffixes.

## Normalized tables

### `datasets.csv`

| Column | Type | Meaning |
|---|---|---|
| `dataset_id` | string | Stable project identifier; primary key |
| `name` | string | Human-readable source name |
| `version` | string | Upstream release or accession |
| `source_url` | URL | Exact public download or API endpoint used by the build |
| `license` | string | Source terms or documented reuse status |
| `citation` | DOI string | Primary citation or dataset DOI |

### `genes.csv`

| Column | Type | Meaning |
|---|---|---|
| `gene_id` | AGI locus ID | Primary key, for example `AT2G28160` |
| `symbol` | string | Araport gene symbol when supplied |
| `name` | string | GFF3 `Name`, falling back to `gene_id` |
| `chromosome` | string | Araport11 sequence identifier |
| `start` | integer | One-based closed gene start |
| `end` | integer | One-based closed gene end |
| `strand` | enum | `+` or `-` |
| `biotype` | string | Araport `biotype` or `locus_type` |
| `description` | string | Decoded GFF3 `Note` |
| `source` | string | GFF3 source column |
| `dataset_id` | string | `araport11-20241001` |

### `motifs.csv`

| Column | Type | Meaning |
|---|---|---|
| `motif_id` | JASPAR matrix ID | Versioned primary key, for example `MA0021.1` |
| `name` | string | JASPAR TF profile name |
| `collection` | string | JASPAR collection, expected `CORE` |
| `tax_group` | string | JASPAR taxonomic group |
| `species_tax_id` | integer | NCBI taxonomy identifier, fixed to `3702` |
| `consensus` | DNA string | Deterministic maximum-frequency base at each PFM position; ties resolve A, C, G, T |
| `data_type` | string | JASPAR evidence/data-type metadata when supplied |
| `matrix_url` | URL | JASPAR matrix landing page |
| `source` | string | Source label stored in the downloaded JSON |
| `dataset_id` | string | `jaspar-2026-core-arabidopsis` |

The normalized table stores a consensus and source link, not the complete PFM. The
downloaded JSON remains the authoritative matrix artifact for a run.

### `tf_motifs.csv`

| Column | Type | Meaning |
|---|---|---|
| `gene_id` | AGI locus ID | Gene endpoint |
| `motif_id` | JASPAR matrix ID | Motif endpoint |
| `mapping_method` | enum | `exact_araport_symbol` |
| `dataset_id` | string | JASPAR dataset provenance |

The logical key is (`gene_id`, `motif_id`, `dataset_id`). Mappings are emitted only
when the JASPAR profile name exactly matches an Araport symbol after case folding.

### `dap_targets.csv`

| Column | Type | Meaning |
|---|---|---|
| `tf_gene_id` | AGI locus ID | Transcription-factor endpoint |
| `target_gene_id` | AGI locus ID | Promoter-overlapping gene endpoint |
| `assay` | enum | `DAP-seq` |
| `evidence` | enum | `promoter_overlap` |
| `peak_count` | integer | Qualifying peaks aggregated into the edge |
| `max_signal` | float | Maximum narrowPeak signal value in the aggregate |
| `max_q_value` | float | Maximum narrowPeak q-value field in the aggregate |
| `promoter_upstream_bp` | integer | Upstream extent, currently `2000` |
| `promoter_downstream_bp` | integer | Downstream extent, currently `500` |
| `source_file` | string | Peak filename retained for traceability |
| `dataset_id` | string | `geo-gse60141` |

The logical key is (`tf_gene_id`, `target_gene_id`, `dataset_id`, `source_file`).
Separate peak files remain separate evidence relationships. These rows are
computational inferences from binding peaks, not validated regulatory effects.

### `y2h_interactions.csv`

| Column | Type | Meaning |
|---|---|---|
| `gene_a_id` | AGI locus ID | Lexicographically first locus endpoint |
| `gene_b_id` | AGI locus ID | Lexicographically second locus endpoint |
| `assay` | enum | `Y2H` |
| `evidence` | enum | `AI1` |
| `publication_id` | CURIE | `PMID:21798944` |
| `source` | string | `InterATOME` |
| `dataset_id` | string | `interatome-1.1` |

Endpoint order is canonical storage for an undirected analytical relationship.
Repeated reciprocal rows collapse; reported homodimer observations remain valid rows
with identical endpoints.

### `metal_focus.csv`

| Column | Type | Meaning |
|---|---|---|
| `gene_id` | AGI locus ID | Gene used as an example query seed |
| `metal` | string | Metal category |
| `evidence_url` | URL | Supporting ontology term or publication |
| `scope_note` | string | Explicit boundary on the hand-curated example |

This table is project configuration, not an upstream experimental dataset and not a
comprehensive annotation set.

## Graph entities

### Nodes

| Label | Unique key | Main properties |
|---|---|---|
| `Dataset` | `dataset_id` | `name`, `version`, `source_url`, `license`, `citation` |
| `Gene` | `gene_id` | `symbol`, `name`, `chromosome`, `start`, `end`, `strand`, `biotype`, `description`, `source`, `dataset_id` |
| `Motif` | `motif_id` | `name`, `collection`, `tax_group`, `species_tax_id`, `consensus`, `data_type`, `matrix_url`, `source`, `dataset_id` |
| `Metal` | `name` | `name` |

### Relationships

| Type | Direction | Key/merge identity | Properties |
|---|---|---|---|
| `FROM_DATASET` | `Gene` or `Motif` → `Dataset` | Endpoint pair | none |
| `ASSOCIATED_WITH_HOMEOSTASIS` | `Gene` → `Metal` | Endpoint pair | `evidence_url`, `scope_note` |
| `HAS_MOTIF` | `Gene` → `Motif` | Endpoints plus `dataset_id` | `dataset_id`, `mapping_method` |
| `PUTATIVE_DAP_TARGET` | TF `Gene` → target `Gene` | Endpoints plus `dataset_id` and `source_file` | `dataset_id`, `assay`, `evidence`, `peak_count`, `max_signal`, `max_q_value`, `promoter_upstream_bp`, `promoter_downstream_bp`, `source_file` |
| `Y2H_INTERACTS_WITH` | canonical `Gene` → `Gene` | Endpoints plus `dataset_id` and `evidence` | `dataset_id`, `evidence`, `assay`, `publication_id`, `source` |

Y2H endpoints are locus-level protein proxies. The relationship should be traversed
without direction in scientific queries.
