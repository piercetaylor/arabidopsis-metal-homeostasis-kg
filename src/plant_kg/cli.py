"""Command-line interface for the reproducible graph workflow."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from pathlib import Path

from neo4j import GraphDatabase

from plant_kg.download import download_sources
from plant_kg.graph.loader import load_graph
from plant_kg.graph.schema import apply_schema
from plant_kg.graph.validation import run_validations
from plant_kg.pipeline import PROJECT_ROOT, build_fixture, build_full
from plant_kg.sources import load_sources


def _connection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", "plantgraph-local"))
    parser.add_argument("--database", default=os.getenv("NEO4J_DATABASE", "neo4j"))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plant-kg",
        description="Build and validate an Arabidopsis metal-homeostasis knowledge graph.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    download = commands.add_parser("download", help="Download full public source datasets")
    download.add_argument("--sources", type=Path, default=PROJECT_ROOT / "config/sources.toml")
    download.add_argument("--raw-dir", type=Path, default=PROJECT_ROOT / "data/raw")

    prepare = commands.add_parser("prepare", help="Normalize source data into graph tables")
    prepare.add_argument("--profile", choices=("fixture", "full"), required=True)
    prepare.add_argument("--raw-dir", type=Path)
    prepare.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data/processed")
    prepare.add_argument("--sources", type=Path, default=PROJECT_ROOT / "config/sources.toml")

    schema = commands.add_parser("schema", help="Apply Neo4j constraints and indexes")
    _connection_arguments(schema)

    load = commands.add_parser("load", help="Load normalized graph tables")
    load.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data/processed")
    load.add_argument("--batch-size", type=int, default=1_000)
    _connection_arguments(load)

    validate = commands.add_parser("validate", help="Run Cypher integrity checks")
    _connection_arguments(validate)

    pipeline = commands.add_parser(
        "pipeline", help="Run the end-to-end fixture or full graph workflow"
    )
    pipeline.add_argument("--profile", choices=("fixture", "full"), required=True)
    pipeline.add_argument("--raw-dir", type=Path)
    pipeline.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data/processed")
    pipeline.add_argument("--sources", type=Path, default=PROJECT_ROOT / "config/sources.toml")
    pipeline.add_argument("--batch-size", type=int, default=1_000)
    _connection_arguments(pipeline)
    return parser


def _prepare(args: argparse.Namespace) -> dict[str, int]:
    if args.profile == "fixture":
        raw_dir = args.raw_dir or PROJECT_ROOT / "data/fixtures/raw"
        return build_fixture(raw_dir, args.output_dir, args.sources)
    raw_dir = args.raw_dir or PROJECT_ROOT / "data/raw"
    return build_full(raw_dir, args.output_dir, args.sources)


def _driver(args: argparse.Namespace):
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    driver.verify_connectivity()
    return driver


def _print_validations(results) -> bool:
    passed = True
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.check} (violations={result.violations})")
        passed = passed and result.passed
    return passed


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "download":
        manifest = download_sources(load_sources(args.sources), args.raw_dir)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    if args.command == "prepare":
        print(json.dumps(_prepare(args), indent=2, sort_keys=True))
        return 0

    if args.command == "schema":
        with _driver(args) as driver:
            apply_schema(driver, PROJECT_ROOT / "cypher", database=args.database)
        print("Neo4j schema is ready.")
        return 0
    if args.command == "load":
        with _driver(args) as driver:
            stats = load_graph(
                driver, args.data_dir, database=args.database, batch_size=args.batch_size
            )
        print(json.dumps({item.table: item.rows for item in stats}, indent=2, sort_keys=True))
        return 0
    if args.command == "validate":
        with _driver(args) as driver:
            results = run_validations(
                driver, PROJECT_ROOT / "cypher/validation", database=args.database
            )
        return 0 if _print_validations(results) else 1
    if args.command == "pipeline":
        if args.profile == "full":
            raw_dir = args.raw_dir or PROJECT_ROOT / "data/raw"
            manifest = download_sources(load_sources(args.sources), raw_dir)
            print(json.dumps(manifest, indent=2, sort_keys=True))
        counts = _prepare(args)
        print(json.dumps(counts, indent=2, sort_keys=True))
        with _driver(args) as driver:
            apply_schema(driver, PROJECT_ROOT / "cypher", database=args.database)
            load_graph(driver, args.output_dir, database=args.database, batch_size=args.batch_size)
            results = run_validations(
                driver, PROJECT_ROOT / "cypher/validation", database=args.database
            )
        return 0 if _print_validations(results) else 1
    raise AssertionError(f"Unhandled command: {args.command}")
