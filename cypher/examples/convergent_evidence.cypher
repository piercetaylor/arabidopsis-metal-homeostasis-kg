MATCH (regulator:Gene)-[binding:PUTATIVE_DAP_TARGET]->(target:Gene),
      (regulator)-[interaction:Y2H_INTERACTS_WITH]-(target)
RETURN regulator.gene_id AS regulator,
       regulator.symbol AS regulator_symbol,
       target.gene_id AS target,
       target.symbol AS target_symbol,
       binding.peak_count AS promoter_peaks,
       interaction.publication_id AS interaction_publication
ORDER BY promoter_peaks DESC;
