from pathlib import Path

from plant_kg.graph.schema import read_statements, split_statements

PROJECT_ROOT = Path(__file__).parents[1]


def test_schema_defines_unique_keys_for_each_node_type() -> None:
    statements = read_statements(PROJECT_ROOT / "cypher" / "constraints.cypher")

    assert len(statements) == 4
    assert all("IF NOT EXISTS" in statement for statement in statements)
    assert {
        label
        for statement in statements
        for label in ("Dataset", "Gene", "Motif", "Metal")
        if f":{label}" in statement
    } == {
        "Dataset",
        "Gene",
        "Motif",
        "Metal",
    }


def test_cypher_splitter_ignores_comments_and_empty_statements() -> None:
    assert split_statements("// comment\nRETURN 1;\n\nRETURN 2;;") == ("RETURN 1", "RETURN 2")
