"""Explicit Pretorius schema-4 to schema-5 migration.

Migration never edits the source database. It copies the persisted RC snapshot,
adds the schema-5 historical-continuity envelope, and writes a manifest mapping
every migrated identity-bearing collection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from digital_subject.cartridge import load_cartridge

from .pretorius import DEFAULT_CARTRIDGE
from .pretorius_v03 import PretoriusV03Subject, SCHEMA5, schema5_extension


SOURCE_SCHEMA = 4
MIGRATION_ID = "pretorius-schema4-to-schema5-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_source_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    uri = f"{path.resolve().as_uri()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=60)) as db:
        row = db.execute("SELECT payload FROM subject WHERE id=1").fetchone()
    if row is None:
        raise ValueError("source database has no persisted subject")
    raw = json.loads(row[0])
    if int(raw.get("schema", -1)) != SOURCE_SCHEMA:
        raise ValueError("migration source must be Pretorius schema 4")
    return raw


def _implementation_fingerprint() -> dict[str, Any]:
    root = Path(__file__).resolve().parent
    package_root = root.parent
    paths = [
        root / "autobiography.py",
        root / "consolidation.py",
        root / "pretorius_v03.py",
        root / "migration.py",
        root / "pretorius.py",
        root / "history.py",
        package_root / "pyproject.toml",
    ]
    files = {}
    for path in paths:
        relative = str(path.relative_to(package_root)).replace("\\", "/")
        files[relative] = _sha256_bytes(path.read_bytes())
    return {
        "files": files,
        "sha256": _sha256_bytes(_canonical(files)),
    }


def _identity_mapping(keys) -> dict[str, str]:
    return {str(key): str(key) for key in sorted(str(item) for item in keys)}


def build_migration_manifest(
    source_path: Path,
    source_payload: dict[str, Any],
) -> dict[str, Any]:
    engine = source_payload["engine"]
    continuity = source_payload["continuity"]
    history_imports = source_payload.get("history_imports", {})
    implementation = _implementation_fingerprint()
    return {
        "migration_id": MIGRATION_ID,
        "source_schema": SOURCE_SCHEMA,
        "target_schema": SCHEMA5,
        "subject_id": engine["subject_id"],
        "source_database_fingerprint": _sha256_bytes(source_path.read_bytes()),
        "source_payload_sha256": _sha256_bytes(_canonical(source_payload)),
        "source_history_artifact_fingerprints": {
            history_id: item.get("sha256")
            for history_id, item in sorted(history_imports.items())
        },
        "target_implementation_fingerprint": implementation,
        "mappings": {
            "memories": _identity_mapping(
                memory["id"] for memory in engine.get("memories", [])
            ),
            "relationships": _identity_mapping(
                engine.get("relationships", {}).keys()
            ),
            "beliefs": _identity_mapping(engine.get("beliefs", {}).keys()),
            "narrative_claims": _identity_mapping(
                engine.get("narrative", {}).keys()
            ),
            "continuity_records": _identity_mapping(
                item["id"]
                for item in continuity.get("epistemic_records", [])
            ),
            "expectations": _identity_mapping(
                continuity.get("expectations", {}).keys()
            ),
            "commitments": _identity_mapping(
                continuity.get("commitments", {}).keys()
            ),
            "reflection_insights": _identity_mapping(
                item["id"] for item in continuity.get("insights", [])
            ),
        },
        "archive_initialization": {
            "active_memory_count": len(engine.get("memories", [])),
            "archive_record_count": 0,
            "policy": "preserve schema-4 active set; no migration-time reinterpretation",
        },
        "autobiography_initialization": {
            "lived_event_count": 0,
            "policy": (
                "schema-4 snapshot is preserved as inherited state; migration does not "
                "retroactively claim that old records are lived:v1 events"
            ),
        },
    }


def migrate_schema4_to_schema5(
    source_db: str | Path,
    target_db: str | Path,
    *,
    cartridge_path: str | Path = DEFAULT_CARTRIDGE,
) -> dict[str, Any]:
    source_path = Path(source_db)
    target_path = Path(target_db)
    if source_path.resolve() == target_path.resolve():
        raise ValueError("schema migration requires a separate target database")
    if target_path.exists():
        raise FileExistsError(
            "target database already exists; migration never overwrites a subject store"
        )

    raw = _read_source_payload(source_path)
    subject_id = str(raw["engine"]["subject_id"])
    extension = schema5_extension(
        subject_id,
        active_memory_ids=[
            memory["id"] for memory in raw["engine"].get("memories", [])
        ],
    )
    manifest = build_migration_manifest(source_path, raw)

    target = {
        **raw,
        "schema": SCHEMA5,
        **extension,
        "migration_manifest": manifest,
    }
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(target_path, timeout=60)) as db:
        db.execute(
            "CREATE TABLE subject (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO subject VALUES (1, ?)",
            (json.dumps(target, allow_nan=False),),
        )
        db.commit()

    cartridge = load_cartridge(cartridge_path)
    validated = PretoriusV03Subject(
        target_path,
        cartridge,
        subject_id=subject_id,
    )
    snapshot = validated.inspect()
    if snapshot["engine"] != raw["engine"]:
        raise RuntimeError("migration validation failed: engine state changed")
    if snapshot["continuity"] != raw["continuity"]:
        raise RuntimeError("migration validation failed: continuity state changed")
    if snapshot.get("history_imports", {}) != raw.get("history_imports", {}):
        raise RuntimeError("migration validation failed: history imports changed")

    return {
        "source": str(source_path),
        "target": str(target_path),
        "manifest": snapshot["migration_manifest"],
        "target_payload_sha256": _sha256_bytes(_canonical(snapshot)),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Explicitly migrate Pretorius schema 4 to schema 5"
    )
    parser.add_argument("source_db", type=Path)
    parser.add_argument("target_db", type=Path)
    parser.add_argument("--cartridge", type=Path, default=DEFAULT_CARTRIDGE)
    args = parser.parse_args()
    report = migrate_schema4_to_schema5(
        args.source_db,
        args.target_db,
        cartridge_path=args.cartridge,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
