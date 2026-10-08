CREATE CONSTRAINT dataset_id_unique IF NOT EXISTS
FOR (n:Dataset) REQUIRE n.dataset_id IS UNIQUE;

CREATE CONSTRAINT gene_id_unique IF NOT EXISTS
FOR (n:Gene) REQUIRE n.gene_id IS UNIQUE;

CREATE CONSTRAINT motif_id_unique IF NOT EXISTS
FOR (n:Motif) REQUIRE n.motif_id IS UNIQUE;

CREATE CONSTRAINT metal_name_unique IF NOT EXISTS
FOR (n:Metal) REQUIRE n.name IS UNIQUE;
