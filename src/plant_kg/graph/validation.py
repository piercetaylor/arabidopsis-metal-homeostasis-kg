"""Execute machine-readable Cypher integrity checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    check: str
    violations: int
    query_file: str

    @property
    def passed(self) -> bool:
        return self.violations == 0


def run_validations(
    driver: Any, validation_dir: Path, *, database: str = "neo4j"
) -> tuple[ValidationResult, ...]:
    results: list[ValidationResult] = []
    with driver.session(database=database) as session:
        for path in sorted(validation_dir.glob("*.cypher")):
            records = session.run(path.read_text(encoding="utf-8")).data()
            for record in records:
                results.append(
                    ValidationResult(
                        check=str(record["check"]),
                        violations=int(record["violations"]),
                        query_file=path.name,
                    )
                )
    if not results:
        raise ValueError(f"No validation queries found in {validation_dir}")
    return tuple(results)
