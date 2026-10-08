# Public data sources

Research checked 2026-09-30. The repository should publish source code, configuration, checksums, attribution, and small synthetic test fixtures. Upstream biological files should be fetched on demand into a git-ignored directory; this avoids bloating Git history and respects sources whose pages provide public access without an explicit redistribution license.

## Recommended sources

| Layer | Source and scientific scope | Reproducible download | Reuse status | Implementation note |
|---|---|---|---|---|
| DAP-seq binding | O'Malley *et al.*, *Cell* 2016, “Cistrome and Epicistrome Features Shape the Regulatory DNA Landscape” ([paper](https://doi.org/10.1016/j.cell.2016.04.038); [GEO GSE60141](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE60141)). The study reports the Arabidopsis DAP-seq atlas and about 2.7 million TF binding sites. | Pin the 77.3 MB archive URL `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE60nnn/GSE60141/suppl/GSE60141_RAW.tar` and record its checksum after download. It contains processed `narrowPeak` files; the adapter excludes `_colamp-` ampDAP-seq members. | GEO is a public archive and NCBI makes its files freely downloadable. NCBI places no restrictions on molecular-data use or distribution, while warning that submitters may retain rights ([NCBI policy](https://www.ncbi.nlm.nih.gov/home/about/policies/), [GEO downloads](https://www.ncbi.nlm.nih.gov/geo/info/download.html)). Cite GSE60141 and the paper. | Prefer GEO to the paper's legacy Plant Cistrome URL. GEO supplies peaks, not a canonical experimentally validated target-gene table, so `TF -> Gene` edges are a documented project inference (see below). |
| Motifs | JASPAR 2026 CORE plant position-frequency matrices ([downloads](https://jaspar2026.elixir.no/downloads/), [documentation](https://jaspar2026.elixir.no/docs/)). CORE is curated and non-redundant. | Versioned plant MEME file: `https://jaspar2026.elixir.no/download/data/2026/CORE/JASPAR2026_CORE_plants_non-redundant_pfms_meme.txt`. Metadata: `https://mencius.uio.no/JASPAR/JASPAR_metadata/2026/ultimate_metadata_table_CORE.tsv`. The REST API is also available, but the static 2026 paths are more reproducible. | JASPAR is [CC BY 4.0](https://jaspar2026.elixir.no/) and requires attribution. Cite the release paper, DOI [`10.1093/nar/gkaf1209`](https://doi.org/10.1093/nar/gkaf1209). | Load matrix ID plus version as the stable key (for example `MA0021.1`), and retain species, TF name/family, collection, release, and matrix values. Do not silently collapse matrix versions. |
| Genes | The Araport11 Arabidopsis annotation, described by Cheng *et al.* ([DOI `10.1111/tpj.13415`](https://doi.org/10.1111/tpj.13415)). Phoenix Bioinformatics/TAIR publishes quarterly snapshots through its official Zenodo community ([record](https://doi.org/10.5281/zenodo.17371665)). | Pin `https://zenodo.org/records/17371665/files/Araport11_GFF3_genes_transposons.20241001.gff.gz?download=1`; published MD5 is `c72c998d26ef28180409370d74229a92`. The record also exposes functional descriptions if needed. | The Zenodo record is marked **Open**, but its License field is blank. Treat this as public access, not an explicit permission to relicense or redistribute. Fetch at runtime, cite TAIR/Araport11, and do not commit the GFF. | Araport11 annotates the TAIR10 reference assembly used by the DAP-seq peaks. Parse `gene` features and AGI locus IDs. GFF3 coordinates are 1-based closed; narrowPeak/BED coordinates are 0-based half-open, so normalize before overlap calculations. |
| Y2H interactions | Arabidopsis Interactome-1 from the Arabidopsis Interactome Mapping Consortium, *Science* 2011 ([paper/PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3170756/), DOI [`10.1126/science.1203877`](https://doi.org/10.1126/science.1203877)). The main ORFeome screen contains 5,664 confirmed binary Y2H interactions among 2,661 proteins. | Use the [InterATOME public deposit](https://doi.org/10.15454/5I2RO1), data file ID `100278`, which integrates the AIM 2011 network and identifies AI-1 rows in its `edge` column. The pinned file is 386,036 bytes with MD5 `8748bc11b954531f1516fccd4835fde8`. | The deposit is public under Licence Ouverte 2.0 (Etalab), which is compatible with CC BY 2.0. Cite both the dataset DOI and original AI-1 paper. | Retain only `edge=AI1`, canonicalize endpoint order for undirected analysis, preserve biologically meaningful homodimer self-loops, and identify the source as InterATOME rather than claiming an exact `AI1_M` subset. |

## Defensible expansion of the metal-homeostasis scope

The implementation deliberately uses four documented query seeds rather than claiming
complete pathway coverage. A future broad-coverage extension should derive its scope
from Gene Ontology annotations instead of expanding that list ad hoc. The current GO
Arabidopsis MOD file is `https://current.geneontology.org/annotations/gaf/ARATH-mod.gaf.gz`;
the corresponding ontology is [`go-basic.obo`](https://purl.obolibrary.org/obo/go/go-basic.obo).
GO recommends recording the release date from the GAF header and using the matching
ontology release ([download guidance](https://geneontology.org/docs/download-go-annotations/)).
GO data products are [CC BY 4.0](https://geneontology.org/docs/go-citation-policy/).

Seed the subgraph with Arabidopsis genes annotated to these terms or any `is_a`/`part_of` descendants in `go-basic.obo`:

| Metal | Homeostasis roots | Transport root |
|---|---|---|
| Iron | [`GO:0006879`](https://amigo.geneontology.org/amigo/term/GO%3A0006879), intracellular iron ion homeostasis; [`GO:0060586`](https://amigo.geneontology.org/amigo/term/GO%3A0060586), multicellular organismal-level iron ion homeostasis | [`GO:0006826`](https://amigo.geneontology.org/amigo/term/GO%3A0006826), iron ion transport |
| Zinc | [`GO:0006882`](https://amigo.geneontology.org/amigo/term/GO%3A0006882), intracellular zinc ion homeostasis | [`GO:0006829`](https://amigo.geneontology.org/amigo/term/GO%3A0006829), zinc ion transport |
| Copper | [`GO:0055070`](https://amigo.geneontology.org/amigo/term/GO%3A0055070), copper ion homeostasis | [`GO:0006825`](https://amigo.geneontology.org/amigo/term/GO%3A0006825), copper ion transport |
| Manganese | [`GO:0055071`](https://amigo.geneontology.org/amigo/term/GO%3A0055071), manganese ion homeostasis | [`GO:0006828`](https://amigo.geneontology.org/amigo/term/GO%3A0006828), manganese ion transport |

Do **not** use `GO:0055072` as the iron root: GO now marks it obsolete and recommends the two current iron-homeostasis terms above ([term history](https://amigo.geneontology.org/amigo/term/GO%3A0055072)). Preserve GAF evidence code, assigned-by group, reference, and annotation date so users can distinguish experimental from computational annotations.

## DAP-seq target-edge semantics

Binding peaks show *in vitro* TF-DNA binding, not regulation in a living plant. A transparent demo rule is:

1. Derive each gene's TSS from the strand-aware Araport11 gene bounds.
2. Convert each narrowPeak interval into the same coordinate convention.
3. Call a candidate target only when the peak interval overlaps the declared window of 2,000 bp upstream through 500 bp downstream of the TSS.
4. Aggregate qualifying peaks by TF, target, and source file while retaining peak count, maximum signal, maximum q-value, promoter-window parameters, and source filename on the edge.
5. Label the relationship `PUTATIVE_DAP_TARGET`, not `REGULATES`.

This makes the target list reproducible and prevents a genomic proximity heuristic from being presented as direct functional regulation.

## Risks to surface in the repository

- The legacy Plant Cistrome and CCSB hosts are old and may be intermittently unavailable. Use GEO, Zenodo, BioGRID release archives, checksums, retry logic, and actionable error messages.
- “Publicly downloadable” is not always “permissively licensed.” JASPAR, BioGRID, and GO have explicit licenses; Araport11's cited Zenodo record and the original CCSB/PMC AI-1 copies do not. Keep upstream downloads out of Git and document attribution.
- `latest` URLs undermine reproducibility. Pin releases for the showcase workflow and offer an explicit update command separately.
- AGI identifiers can appear with transcript suffixes or aliases. Canonicalize graph gene keys to uppercase locus-level IDs such as `AT1G01010`, while retaining the source identifier.
- The expected AI-1 count of 5,664 applies specifically to `AI1_M`. Do not assert that count for a broader BioGRID publication filter unless validation reproduces the exact subset.
