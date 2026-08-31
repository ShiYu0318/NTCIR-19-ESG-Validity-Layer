#!/usr/bin/env python3
"""Verify the release capsule and regenerate the manuscript results."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "release_manifest.json"
INPUTS_ROOT = ROOT / "inputs"
CORPUS_INDEX_PATH = INPUTS_ROOT / "aicup_zh" / "corpus_index.json.gz"

PAPER_TABLE_STEMS = (
    "table1_dataset",
    "table2_main",
    "table3_legality_cost",
    "table4_contrasts",
    "table6_regimes",
    "table7_multilingual_mechanism",
    "table8_invalid_anatomy",
    "table9_external_arms",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def load_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))


def _actual_artifact_paths(root: Path) -> set[str]:
    inputs_root = root / "inputs"
    return {
        path.relative_to(root).as_posix()
        for path in inputs_root.rglob("*")
        if path.is_file()
    }


def _corpus_index_has_raw_text(path: Path) -> bool:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        payload = json.load(stream)
    return any("data" in row for partition in ("development", "test")
               for row in payload[partition])


def verify_inputs(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    manifest = load_manifest(root)
    expected = manifest["artifacts"]
    actual_paths = _actual_artifact_paths(root)
    expected_paths = set(expected)
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    if missing or extra:
        raise ValueError(f"artifact inventory mismatch; missing={missing}, extra={extra}")

    mismatches = [
        path for path, expected_hash in expected.items()
        if sha256(root / path) != expected_hash
    ]
    if mismatches:
        raise ValueError(f"artifact checksum mismatch: {mismatches}")
    reference_mismatches = [
        path for path, expected_hash in manifest.get("references", {}).items()
        if not (root / path).is_file() or sha256(root / path) != expected_hash
    ]
    if reference_mismatches:
        raise ValueError(f"reference checksum mismatch: {reference_mismatches}")

    raw_text_files = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "dataset" in path.relative_to(root).parts
    ]
    corpus_index = root / "inputs" / "aicup_zh" / "corpus_index.json.gz"
    if _corpus_index_has_raw_text(corpus_index):
        raw_text_files.append(corpus_index.relative_to(root).as_posix())
    if raw_text_files:
        raise ValueError(f"raw text artifacts are not allowed: {raw_text_files}")

    prediction_files = sum(path.endswith(".csv.gz") for path in expected)
    if prediction_files != manifest["prediction_files"]:
        raise ValueError(
            f"manifest declares {manifest['prediction_files']} predictions, "
            f"but inventories {prediction_files}"
        )
    return {
        "artifact_files": len(expected),
        "prediction_files": prediction_files,
        "raw_text_files": 0,
        "source_commit": manifest["source_commit"],
        "status": "ok",
    }


def reproduce_results(output_dir: Path) -> dict:
    """Run the frozen CPU analysis and byte-check manuscript-facing outputs."""
    output_dir = Path(output_dir).resolve()
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    from analysis.__main__ import main as analysis_main

    previous_argv = sys.argv
    try:
        sys.argv = [
            "python -m analysis",
            "--out-dir", str(tables_dir),
            "--figures-dir", str(figures_dir),
        ]
        analysis_main()
    finally:
        sys.argv = previous_argv

    reference_tables = ROOT / "reference" / "tables"
    mismatches = []
    for stem in PAPER_TABLE_STEMS:
        for suffix in (".tex", "_caption.txt"):
            name = stem + suffix
            if (tables_dir / name).read_bytes() != (reference_tables / name).read_bytes():
                mismatches.append(name)
    if mismatches:
        raise ValueError(f"regenerated manuscript outputs differ: {mismatches}")

    from analysis.figure1 import DEFS_NAME, write_defs

    source_name = "figure1_hierarchy.tex"
    shutil.copyfile(ROOT / "figures" / source_name, figures_dir / source_name)
    write_defs(figures_dir / DEFS_NAME)
    figure_source_verified = all(
        (figures_dir / name).read_bytes() == (ROOT / "figures" / name).read_bytes()
        for name in (source_name, DEFS_NAME)
    )
    if not figure_source_verified:
        raise ValueError("regenerated Figure 1 source differs from the release")
    return {
        "figure_source_verified": True,
        "status": "ok",
        "tables_verified": len(PAPER_TABLE_STEMS),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-inputs",
        action="store_true",
        help="validate the curated artifacts and exit without recomputing tables",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs",
        help="directory for regenerated tables and figure files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = verify_inputs()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"input verification failed: {error}", file=sys.stderr)
        return 2
    if args.verify_inputs:
        print(json.dumps(report, sort_keys=True))
        return 0
    try:
        result = reproduce_results(args.output_dir)
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(f"result reproduction failed: {error}", file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
