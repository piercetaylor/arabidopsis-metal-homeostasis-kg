CALL () { MATCH (n:Dataset) RETURN count(n) AS datasets }
CALL () { MATCH (n:Gene) RETURN count(n) AS genes }
CALL () { MATCH (n:Motif) RETURN count(n) AS motifs }
CALL () { MATCH (n:Metal) RETURN count(n) AS metals }
CALL () { MATCH ()-[r:PUTATIVE_DAP_TARGET]->() RETURN count(r) AS dap_edges }
CALL () { MATCH ()-[r:HAS_MOTIF]->() RETURN count(r) AS motif_edges }
CALL () { MATCH ()-[r:Y2H_INTERACTS_WITH]->() RETURN count(r) AS y2h_edges }
RETURN "required graph entities" AS check,
       CASE WHEN datasets > 0 THEN 0 ELSE 1 END +
       CASE WHEN genes > 0 THEN 0 ELSE 1 END +
       CASE WHEN motifs > 0 THEN 0 ELSE 1 END +
       CASE WHEN metals > 0 THEN 0 ELSE 1 END +
       CASE WHEN dap_edges > 0 THEN 0 ELSE 1 END +
       CASE WHEN motif_edges > 0 THEN 0 ELSE 1 END +
       CASE WHEN y2h_edges > 0 THEN 0 ELSE 1 END AS violations;
