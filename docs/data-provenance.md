# Data provenance

Source metadata and access conditions were checked on 2026-09-30. Exact machine
inputs are declared in `config/sources.toml`; this document explains why each source
is used and what the project does to it.

## Provenance policy

- Upstream biological files are downloaded into `data/raw/`, which is ignored by Git.
- The downloader writes a local `download-manifest.json` with the retrieval time,
  source URL, byte size, and SHA-256 digest of each artifact.
- Normalized full-data outputs under `data/processed/` are also ignored.
- Repository fixtures are hand-authored and source-shaped. They test contracts but
  are not samples copied from the full datasets.
- Publications and source accessions must be cited in downstream analyses. The
  repository MIT license does not relicense source data.

## Araport11 gene annotation

- **Owner/distributor:** TAIR/Phoenix Bioinformatics through its official Zenodo
  community
- **Input:** `Araport11_GFF3_genes_transposons.20241001.gff.gz`
- **Release:** pinned quarterly snapshot dated 2024-10-01
- **Source URL:** <https://zenodo.org/records/17371665/files/Araport11_GFF3_genes_transposons.20241001.gff.gz?download=1>
- **Record DOI:** <https://doi.org/10.5281/zenodo.17371665>
- **Published MD5:** `c72c998d26ef28180409370d74229a92`
- **Citation:** Cheng C-Y et al. (2017), *The Plant Journal*.
  <https://doi.org/10.1111/tpj.13415>
- **Reuse status:** the Zenodo record is public but does not state a reuse license.
  Public access is not treated as permission to relicense the file. It is fetched for
  local processing and is not redistributed.

The adapter loads exact GFF3 `gene` features, decodes attributes, retains genomic
coordinates and strand, and keys records by AGI locus. Transcript and child features
are excluded. Araport coordinates are one-based and closed.

The pinned snapshot contains occasional legacy bytes in annotation text. Undecodable
UTF-8 bytes are retained as explicit `\xNN` escapes in normalized text fields.

## Arabidopsis DAP-seq cistrome

- **Owner/distributor:** O'Malley et al.; NCBI Gene Expression Omnibus
- **Input:** `GSE60141_RAW.tar`, containing processed narrowPeak files
- **Accession:** [GSE60141](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE60141),
  the DAP-seq subseries within superseries GSE60143
- **Source URL:** <https://ftp.ncbi.nlm.nih.gov/geo/series/GSE60nnn/GSE60141/suppl/GSE60141_RAW.tar>
- **Citation:** O'Malley RC et al. (2016), *Cell*.
  <https://doi.org/10.1016/j.cell.2016.04.038>
- **Reuse status:** publicly archived by NCBI GEO. NCBI/GEO policies and any submitter
  rights apply. The archive is downloaded for local processing and is not
  redistributed.

The full pipeline selects native-genome DAP-seq peak files and excludes `_colamp-`
ampDAP-seq files. NarrowPeak intervals are zero-based and half-open; the adapter
converts the start to a one-based interval before overlap comparison. A peak supports
a `PUTATIVE_DAP_TARGET` edge when it overlaps the target gene's strand-aware window
from 2,000 bp upstream through 500 bp downstream of the transcription start site.
Qualifying peaks are aggregated by TF and target gene.

This transformation is a project inference. DAP-seq is an *in vitro* binding assay;
neither a peak nor promoter proximity proves transcriptional regulation in vivo.

## JASPAR CORE motifs

- **Owner/distributor:** JASPAR consortium
- **Input:** detailed REST API records for CORE plant matrices filtered to NCBI
  taxonomy ID 3702
- **Release:** JASPAR 2026
- **Source URL:** <https://jaspar.elixir.no/api/v1/matrix/?collection=CORE&tax_group=plants&tax_id=3702&version=latest&page_size=1000>
- **Release site:** <https://jaspar.elixir.no/>
- **Citation:** Ovek Baydar D et al. (2026), *Nucleic Acids Research*.
  <https://doi.org/10.1093/nar/gkaf1209>
- **License:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- **Redistribution policy:** downloaded API output is not committed; attribution and
  license metadata are retained in the project documentation.

The downloader follows API pagination and fetches matrix detail records using at most
four simultaneous requests. `tax_id=3702` selects Arabidopsis and `version=latest`
selects the non-redundant profiles. The live API serves the current JASPAR release;
the recorded SHA-256 and retrieval date identify the exact local snapshot. The adapter
keeps versioned matrix IDs, retains Arabidopsis records, derives a deterministic
consensus from each PFM, and emits a gene-to-motif link only when the JASPAR name
exactly matches an Araport symbol after case folding. It does not use fuzzy matching,
so valid aliases may remain unlinked.

## InterATOME / Arabidopsis Interactome-1

- **Owner/distributor:** Dario Monachello and Claire Lurin; Recherche Data Gouv
- **Dataset:** *InterATOME protein-protein interactions, Public*, version 1.1
- **Dataset DOI:** <https://doi.org/10.15454/5I2RO1>
- **Input file:** `Public_raw_data` through data-file API identifier `100278`
- **Source URL:** <https://entrepot.recherche.data.gouv.fr/api/access/datafile/100278>
- **Published MD5:** `8748bc11b954531f1516fccd4835fde8`
- **Related publication:** Arabidopsis Interactome Mapping Consortium (2011),
  *Science*. <https://doi.org/10.1126/science.1203877>
- **License:** Etalab Open Licence 2.0, identified by the repository as compatible
  with CC BY 2.0
- **Redistribution policy:** fetched on demand rather than vendored; dataset authors,
  DOI, version, and license are attributed.

The public InterATOME collection includes systematic large-scale Arabidopsis Y2H
maps. This project keeps rows marked `AI1`, strips transcript suffixes, requires both
endpoints to resolve to Araport loci, canonicalizes endpoint order, and collapses
reciprocal duplicates. Reported homodimer evidence is retained as a self-loop. The
graph stores publication `PMID:21798944` and assay `Y2H` on each relationship.

## Metal-homeostasis query lens

`config/metal_focus.tsv` is a small, hand-curated set of example query seeds. Each
row includes an evidence URL and the explicit note that it is not a comprehensive
annotation set. It is not presented as a fifth public dataset and should not be used
for enrichment statistics or completeness claims.

## Reproducing an input set

Run `plant-kg download`, then archive the generated download manifest alongside the
analysis outputs. Compare its SHA-256 values before reusing an existing raw-data
directory. A changed digest can reflect a changed upstream response even when the URL
is unchanged and should trigger review before graph regeneration.
