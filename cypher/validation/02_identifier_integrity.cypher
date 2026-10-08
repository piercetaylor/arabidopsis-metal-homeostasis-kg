CALL {
  MATCH (g:Gene)
  WHERE g.gene_id IS NULL
     OR NOT g.gene_id =~ '^AT[1-5CM]G[0-9]{5}$'
     OR g.start IS NULL
     OR g.end IS NULL
     OR g.start > g.end
     OR g.strand IS NULL
     OR NOT g.strand IN ['+', '-']
  RETURN count(g) AS invalid_genes
}
CALL {
  MATCH (m:Motif)
  WHERE m.motif_id IS NULL
     OR NOT m.motif_id =~ '^MA[0-9]{4}[.][0-9]+$'
  RETURN count(m) AS invalid_motifs
}
RETURN "identifier and coordinate integrity" AS check,
       invalid_genes + invalid_motifs AS violations;
