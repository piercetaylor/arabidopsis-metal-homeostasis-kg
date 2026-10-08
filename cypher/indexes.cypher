CREATE INDEX gene_symbol IF NOT EXISTS FOR (n:Gene) ON (n.symbol);
CREATE INDEX gene_chromosome IF NOT EXISTS FOR (n:Gene) ON (n.chromosome);
CREATE INDEX motif_name IF NOT EXISTS FOR (n:Motif) ON (n.name);
