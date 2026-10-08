MATCH (regulator:Gene)-[:HAS_MOTIF]->(motif:Motif),
      (regulator)-[:PUTATIVE_DAP_TARGET]->(target:Gene)
      -[:ASSOCIATED_WITH_HOMEOSTASIS]->(metal:Metal)
RETURN regulator.gene_id AS regulator,
       regulator.symbol AS symbol,
       motif.motif_id AS motif,
       motif.consensus AS consensus,
       metal.name AS metal,
       count(DISTINCT target) AS putative_metal_targets
ORDER BY putative_metal_targets DESC, regulator;
