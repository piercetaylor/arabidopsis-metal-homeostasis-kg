CALL () {
  MATCH (a)-[r:HAS_MOTIF]->(b)
  WHERE NOT a:Gene OR NOT b:Motif OR r.dataset_id IS NULL OR r.mapping_method IS NULL
  RETURN count(r) AS invalid_motif_edges
}
CALL () {
  MATCH (a)-[r:PUTATIVE_DAP_TARGET]->(b)
  WHERE NOT a:Gene OR NOT b:Gene OR r.dataset_id IS NULL OR r.source_file IS NULL
     OR r.peak_count IS NULL OR r.peak_count < 1
     OR r.assay IS NULL OR r.assay <> 'DAP-seq'
     OR r.evidence IS NULL OR r.evidence <> 'promoter_overlap'
     OR r.max_signal IS NULL OR r.max_q_value IS NULL
     OR r.promoter_upstream_bp IS NULL OR r.promoter_downstream_bp IS NULL
  RETURN count(r) AS invalid_dap_edges
}
CALL () {
  MATCH (a)-[r:Y2H_INTERACTS_WITH]->(b)
  WHERE NOT a:Gene OR NOT b:Gene OR r.dataset_id IS NULL OR r.evidence IS NULL
     OR a.gene_id > b.gene_id
     OR r.assay IS NULL OR r.assay <> 'Y2H'
     OR r.publication_id IS NULL OR r.source IS NULL
  RETURN count(r) AS invalid_y2h_edges
}
RETURN "relationship endpoint and property integrity" AS check,
       invalid_motif_edges + invalid_dap_edges + invalid_y2h_edges AS violations;
