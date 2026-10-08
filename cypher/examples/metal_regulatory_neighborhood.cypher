MATCH (tf:Gene)-[binding:PUTATIVE_DAP_TARGET]->(target:Gene)
      -[:ASSOCIATED_WITH_HOMEOSTASIS]->(metal:Metal)
OPTIONAL MATCH (tf)-[:HAS_MOTIF]->(motif:Motif)
OPTIONAL MATCH (tf)-[:Y2H_INTERACTS_WITH]-(partner:Gene)
RETURN metal.name AS metal,
       tf.gene_id AS regulator,
       tf.symbol AS regulator_symbol,
       target.gene_id AS putative_target,
       target.symbol AS target_symbol,
       collect(DISTINCT motif.motif_id) AS jaspar_motifs,
       collect(DISTINCT partner.gene_id) AS y2h_partners,
       binding.peak_count AS promoter_peaks
ORDER BY metal, regulator, putative_target;
