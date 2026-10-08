"""Apply idempotent Neo4j schema statements."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def split_statements(text: str) -> tuple[str, ...]:
    uncommented = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("//")
    )
    return tuple(statement.strip() for statement in uncommented.split(";") if statement.strip())


def read_statements(path: Path) -> tuple[str, ...]:
    return split_statements(path.read_text(encoding="utf-8"))


def apply_schema(driver: Any, cypher_dir: Path, *, database: str = "neo4j") -> None:
    statements = read_statements(cypher_dir / "constraints.cypher") + read_statements(
        cypher_dir / "indexes.cypher"
    )
    with driver.session(database=database) as session:
        for statement in statements:
            session.run(statement).consume()
