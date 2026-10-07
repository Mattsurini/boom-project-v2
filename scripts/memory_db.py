#!/usr/bin/env python3
"""Boom Project structured memory database.

This database is deliberately separate from Hermes native memory/session history.
It stores source-backed project facts, durable project decisions, and entities.

Usage:
    python scripts/memory_db.py init
    python scripts/memory_db.py status
    python scripts/memory_db.py add-source --title "..." --path "..."
    python scripts/memory_db.py add-claim --claim "..." --source-id 1
    python scripts/memory_db.py add-memory --content "..." --category workflow
    python scripts/memory_db.py sync-manifest
    python scripts/memory_db.py search "query"
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "cache" / "boom_project_registry.sqlite3"
MANIFEST_PATH = PROJECT_ROOT / "Knowledge" / "indexes" / "project_manifest.json"
SCHEMA_VERSION = 1

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'project-file',
    path_or_url TEXT NOT NULL,
    source_hash TEXT,
    accessed_at TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,
    name TEXT NOT NULL,
    canonical_key TEXT NOT NULL UNIQUE,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY,
    claim TEXT NOT NULL,
    topic TEXT,
    status TEXT NOT NULL DEFAULT 'working'
        CHECK (status IN ('raw', 'working', 'verified', 'rejected', 'superseded')),
    confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    source_id INTEGER,
    evidence_note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS project_memory (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'superseded', 'archived')),
    source_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS claim_tags (
    claim_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (claim_id, tag_id),
    FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (memory_id, tag_id),
    FOREIGN KEY (memory_id) REFERENCES project_memory(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_claims_topic_status ON claims(topic, status);
CREATE INDEX IF NOT EXISTS idx_memory_category_status ON project_memory(category, status);
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);

CREATE VIRTUAL TABLE IF NOT EXISTS claims_fts USING fts5(
    claim, topic, evidence_note, content='claims', content_rowid='id'
);
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    category, content, content='project_memory', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS claims_ai AFTER INSERT ON claims BEGIN
    INSERT INTO claims_fts(rowid, claim, topic, evidence_note)
    VALUES (new.id, new.claim, new.topic, new.evidence_note);
END;
CREATE TRIGGER IF NOT EXISTS claims_ad AFTER DELETE ON claims BEGIN
    INSERT INTO claims_fts(claims_fts, rowid, claim, topic, evidence_note)
    VALUES ('delete', old.id, old.claim, old.topic, old.evidence_note);
END;
CREATE TRIGGER IF NOT EXISTS claims_au AFTER UPDATE ON claims BEGIN
    INSERT INTO claims_fts(claims_fts, rowid, claim, topic, evidence_note)
    VALUES ('delete', old.id, old.claim, old.topic, old.evidence_note);
    INSERT INTO claims_fts(rowid, claim, topic, evidence_note)
    VALUES (new.id, new.claim, new.topic, new.evidence_note);
END;
CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON project_memory BEGIN
    INSERT INTO memory_fts(rowid, category, content)
    VALUES (new.id, new.category, new.content);
END;
CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON project_memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, category, content)
    VALUES ('delete', old.id, old.category, old.content);
END;
CREATE TRIGGER IF NOT EXISTS memory_au AFTER UPDATE ON project_memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, category, content)
    VALUES ('delete', old.id, old.category, old.content);
    INSERT INTO memory_fts(rowid, category, content)
    VALUES (new.id, new.category, new.content);
END;
"""


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        timestamp = now()
        conn.execute(
            "INSERT INTO schema_meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        conn.execute(
            "INSERT INTO schema_meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("project_root", str(PROJECT_ROOT)),
        )
        conn.execute(
            "INSERT INTO schema_meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("updated_at", timestamp),
        )
    print(f"initialized: {DB_PATH}")


def status() -> None:
    init_db()
    with connect() as conn:
        tables = ["sources", "entities", "claims", "project_memory", "tags"]
        counts = {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}
        print(f"database: {DB_PATH}")
        schema_version = conn.execute(
            "SELECT value FROM schema_meta WHERE key='schema_version'"
        ).fetchone()[0]
        print(f"schema_version: {schema_version}")
        for table, count in counts.items():
            print(f"{table}: {count}")


def add_source(args: argparse.Namespace) -> None:
    init_db()
    timestamp = now()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO sources(title, source_type, path_or_url, source_hash, accessed_at, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (args.title, args.source_type, args.path_or_url, args.source_hash, timestamp, args.notes, timestamp, timestamp),
        )
        print(f"source_id: {cur.lastrowid}")


def add_claim(args: argparse.Namespace) -> None:
    init_db()
    timestamp = now()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO claims(claim, topic, status, confidence, source_id, evidence_note, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (args.claim, args.topic, args.status, args.confidence, args.source_id, args.evidence_note, timestamp, timestamp),
        )
        print(f"claim_id: {cur.lastrowid}")


def add_memory(args: argparse.Namespace) -> None:
    init_db()
    timestamp = now()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO project_memory(category, content, status, source_id, created_at, updated_at) "
            "VALUES (?, ?, 'active', ?, ?, ?)",
            (args.category, args.content, args.source_id, timestamp, timestamp),
        )
        print(f"project_memory_id: {cur.lastrowid}")


def sync_manifest() -> None:
    """Sync the generated project manifest into the source registry."""
    init_db()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])
    timestamp = now()
    with connect() as conn:
        synced = 0
        for entry in entries:
            # Manifest uses compact keys (p/t/s/tp/fm/sz/mt/hsh); accept legacy long keys too.
            rel_path = str(entry.get("p") or entry.get("path") or "").replace("\\", "/")
            if not rel_path:
                continue
            title = entry.get("t") or entry.get("title") or rel_path
            notes = json.dumps(
                {
                    "stage": entry.get("s") or entry.get("stage", ""),
                    "topics": entry.get("tp") or entry.get("topics", []),
                    "frontmatter": bool(entry.get("fm", entry.get("frontmatter", False))),
                    "size": entry.get("sz") if "sz" in entry else entry.get("size"),
                    "mtime": entry.get("mt") if "mt" in entry else entry.get("mtime"),
                },
                ensure_ascii=False,
            )
            source_hash = entry.get("hsh") or entry.get("sha1_64k")
            existing = conn.execute(
                "SELECT id FROM sources WHERE path_or_url = ? ORDER BY id LIMIT 1",
                (rel_path,),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE sources SET title=?, source_hash=?, accessed_at=?, notes=?, updated_at=? WHERE id=?",
                    (title, source_hash, timestamp, notes, timestamp, existing[0]),
                )
            else:
                conn.execute(
                    "INSERT INTO sources(title, source_type, path_or_url, source_hash, accessed_at, notes, created_at, updated_at) "
                    "VALUES (?, 'project-manifest', ?, ?, ?, ?, ?, ?)",
                    (title, rel_path, source_hash, timestamp, notes, timestamp, timestamp),
                )
            synced += 1
    print(f"manifest_entries_synced: {synced}")
    if synced == 0:
        print("WARNING: no manifest entries matched expected keys — check manifest schema")
    print(f"database: {DB_PATH}")


def search(args: argparse.Namespace) -> None:
    init_db()
    with connect() as conn:
        query = args.query.replace('"', ' ')
        claims = conn.execute(
            "SELECT c.id, c.claim, c.topic, c.status FROM claims_fts f "
            "JOIN claims c ON c.id = f.rowid WHERE claims_fts MATCH ? LIMIT 10",
            (query,),
        ).fetchall()
        memories = conn.execute(
            "SELECT m.id, m.category, m.content, m.status FROM memory_fts f "
            "JOIN project_memory m ON m.id = f.rowid WHERE memory_fts MATCH ? LIMIT 10",
            (query,),
        ).fetchall()
        print("claims:")
        for row in claims:
            print(f"  [{row['id']}] ({row['status']}) {row['topic'] or '-'}: {row['claim']}")
        print("project_memory:")
        for row in memories:
            print(f"  [{row['id']}] ({row['status']}) {row['category']}: {row['content']}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("sync-manifest")

    source = sub.add_parser("add-source")
    source.add_argument("--title", required=True)
    source.add_argument("--path-or-url", required=True)
    source.add_argument("--source-type", default="project-file")
    source.add_argument("--source-hash")
    source.add_argument("--notes")

    claim = sub.add_parser("add-claim")
    claim.add_argument("--claim", required=True)
    claim.add_argument("--topic")
    claim.add_argument("--status", choices=["raw", "working", "verified", "rejected", "superseded"], default="working")
    claim.add_argument("--confidence", type=float)
    claim.add_argument("--source-id", type=int)
    claim.add_argument("--evidence-note")

    memory = sub.add_parser("add-memory")
    memory.add_argument("--category", required=True)
    memory.add_argument("--content", required=True)
    memory.add_argument("--source-id", type=int)

    search_cmd = sub.add_parser("search")
    search_cmd.add_argument("query")
    return p


def main() -> None:
    args = parser().parse_args()
    if args.command == "init":
        init_db()
    elif args.command == "status":
        status()
    elif args.command == "sync-manifest":
        sync_manifest()
    elif args.command == "add-source":
        add_source(args)
    elif args.command == "add-claim":
        add_claim(args)
    elif args.command == "add-memory":
        add_memory(args)
    elif args.command == "search":
        search(args)


if __name__ == "__main__":
    main()
