"""Text-free corpus metadata used by the public result reproduction."""

from __future__ import annotations

import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
INPUTS_ROOT = REPO_ROOT / "inputs"
AICUP_ROOT = INPUTS_ROOT / "aicup_zh"
CORPUS_INDEX_PATH = AICUP_ROOT / "corpus_index.json.gz"
AICUP_SPLITS_DIR = AICUP_ROOT / "splits"
AICUP_PRIMARY_RUN_ROOT = AICUP_ROOT / "runs" / "main"

# The table provenance API expects three source paths. The public capsule has
# one text-free index in place of the three non-redistributed source files.
TRAIN_PATH = CORPUS_INDEX_PATH
VAL_PATH = CORPUS_INDEX_PATH
TEST_PATH = CORPUS_INDEX_PATH

LABEL_KEYS = (
    "promise_status",
    "verification_timeline",
    "evidence_status",
    "evidence_quality",
)


@lru_cache(maxsize=1)
def _index() -> dict:
    with gzip.open(CORPUS_INDEX_PATH, "rt", encoding="utf-8") as stream:
        payload = json.load(stream)
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported corpus-index schema")
    return payload


def load_dev() -> list[dict]:
    rows = _index()["development"]
    _assert_ids_usable(rows)
    return rows


def load_test() -> list[dict]:
    rows = _index()["test"]
    _assert_ids_usable(rows)
    return rows


def canonical_row_order(rows: list[dict] | None = None) -> list[str]:
    return [row["id"] for row in (rows if rows is not None else load_dev())]


def index_by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def data_checksum(rows: list[dict] | None = None) -> str:
    """Return the source checksum frozen into the published split manifest."""
    candidate = rows if rows is not None else load_dev()
    if [row["id"] for row in candidate] != canonical_row_order(load_dev()):
        raise ValueError("the public capsule only records the full development checksum")
    split = AICUP_SPLITS_DIR / "pdf_group_seed42.json"
    return json.loads(split.read_text(encoding="utf-8"))["data_checksum"]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _assert_ids_usable(rows: list[dict]) -> None:
    ids = [row["id"] for row in rows]
    if any(not isinstance(row_id, str) for row_id in ids):
        raise TypeError("row ids must be strings")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate row ids in corpus index")
