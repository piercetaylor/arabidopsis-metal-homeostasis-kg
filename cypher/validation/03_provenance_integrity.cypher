CALL () {
  MATCH (n)
  WHERE (n:Gene OR n:Motif) AND NOT (n)-[:FROM_DATASET]->(:Dataset)
  RETURN count(n) AS nodes_without_provenance
}
CALL () {
  MATCH ()-[r]->()
  WHERE type(r) IN ['HAS_MOTIF', 'PUTATIVE_DAP_TARGET', 'Y2H_INTERACTS_WITH']
    AND (r.dataset_id IS NULL OR NOT EXISTS {
      MATCH (:Dataset {dataset_id: r.dataset_id})
    })
  RETURN count(r) AS edges_without_provenance
}
CALL () {
  MATCH (d:Dataset)
  WHERE d.source_url IS NULL OR d.license IS NULL OR d.citation IS NULL
  RETURN count(d) AS datasets_without_provenance
}
RETURN "dataset provenance integrity" AS check,
       nodes_without_provenance + edges_without_provenance + datasets_without_provenance
       AS violations;
