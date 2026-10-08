import os
from pathlib import Path

import pytest
from neo4j import GraphDatabase

from plant_kg.graph.loader import load_graph
from plant_kg.graph.schema import apply_schema
from plant_kg.graph.validation import run_validations
from plant_kg.pipeline import build_fixture

pytestmark = pytest.mark.integration
PROJECT_ROOT = Path(__file__).parents[2]


@pytest.fixture
def driver():
    uri = os.getenv("NEO4J_URI")
    if not uri:
        pytest.skip("NEO4J_URI is not configured")
    if os.getenv("NEO4J_TEST_ALLOW_RESET") != "1":
        pytest.fail(
            "Integration tests clear the database; "
            "set NEO4J_TEST_ALLOW_RESET=1 for a disposable instance"
        )
    instance = GraphDatabase.driver(
        uri,
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "plantgraph-ci")),
    )
    instance.verify_connectivity()
    with instance.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
        session.run("MATCH (n) DETACH DELETE n").consume()
    yield instance
    instance.close()


def test_fixture_load_is_idempotent_and_passes_validations(driver, tmp_path: Path) -> None:
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    build_fixture(PROJECT_ROOT / "data/fixtures/raw", tmp_path)
    apply_schema(driver, PROJECT_ROOT / "cypher", database=database)

    first = load_graph(driver, tmp_path, database=database, batch_size=2)
    with driver.session(database=database) as session:
        before = session.run(
            "MATCH (n) WITH count(n) AS nodes MATCH ()-[r]->() "
            "RETURN nodes, count(r) AS relationships"
        ).single()
    second = load_graph(driver, tmp_path, database=database, batch_size=2)
    with driver.session(database=database) as session:
        after = session.run(
            "MATCH (n) WITH count(n) AS nodes MATCH ()-[r]->() "
            "RETURN nodes, count(r) AS relationships"
        ).single()

    assert first == second
    assert dict(before) == dict(after)
    assert before["nodes"] == 10
    assert before["relationships"] == 14

    validations = run_validations(driver, PROJECT_ROOT / "cypher/validation", database=database)
    assert len(validations) >= 4
    assert all(result.passed for result in validations), validations

    with driver.session(database=database) as session:
        constraints = {
            record["name"] for record in session.run("SHOW CONSTRAINTS YIELD name RETURN name")
        }
    assert constraints == {
        "dataset_id_unique",
        "gene_id_unique",
        "metal_name_unique",
        "motif_id_unique",
    }

    with driver.session(database=database) as session:
        # A combined scientific path is optional; the homodimer still supplies Y2H evidence.
        session.run(
            "MATCH (g:Gene {gene_id: 'AT3G23210'})-[r:Y2H_INTERACTS_WITH]-() DELETE r"
        ).consume()
    no_combined_path = run_validations(
        driver, PROJECT_ROOT / "cypher/validation", database=database
    )
    assert all(result.passed for result in no_combined_path)

    with driver.session(database=database) as session:
        session.run("MATCH ()-[r:HAS_MOTIF]->() REMOVE r.mapping_method").consume()
        session.run("MATCH ()-[r:PUTATIVE_DAP_TARGET]->() REMOVE r.assay").consume()
        session.run("MATCH ()-[r:Y2H_INTERACTS_WITH]->() REMOVE r.publication_id").consume()
    broken = run_validations(driver, PROJECT_ROOT / "cypher/validation", database=database)
    relationships = next(result for result in broken if "relationship" in result.check)
    assert relationships.violations == 4  # one motif, two DAP, and one Y2H edge


def test_validation_rejects_missing_gene_coordinates(driver, tmp_path: Path) -> None:
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    build_fixture(PROJECT_ROOT / "data/fixtures/raw", tmp_path)
    apply_schema(driver, PROJECT_ROOT / "cypher", database=database)
    load_graph(driver, tmp_path, database=database)
    with driver.session(database=database) as session:
        session.run("MATCH (g:Gene {gene_id: 'AT1G01580'}) REMOVE g.start").consume()

    results = run_validations(driver, PROJECT_ROOT / "cypher/validation", database=database)

    identifiers = next(result for result in results if "identifier" in result.check)
    assert identifiers.violations == 1
