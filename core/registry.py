#!/usr/bin/env python
"""
hermes.core.registry — the single discovery surface for the Boom rebuild.

Design contract (SPEC.md §2): registry = discovery. Nothing else in the system
may hardcode a path to a skill, script, agent or project. If it exists, it is
registered here; if it is not here, the system does not believe it exists.

Token contract (SPEC.md §6): find() returns NAMES + tiny descriptors only.
Bodies are never returned by discovery. Loading a body is a separate,
explicitly-priced call.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass, asdict, field
from typing import Any

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")
HERMES = os.environ.get("HERMES_HOME", r"C:\Users\Turbo\AppData\Local\hermes")

# A descriptor may never exceed this. Discovery is allowed to be cheap.
MAX_DESCRIPTOR_CHARS = 400


@dataclass(frozen=True)
class Descriptor:
    """What discovery returns. Never contains a body."""

    id: str
    kind: str  # skill | script | agent | project | artifact | mcp
    title: str
    trigger: str  # the ONLY text injected into the prompt
    path: str
    tags: tuple[str, ...] = ()
    cost: int = 0  # 0 = free, 1 = lazy-load, 2 = delegate
    deprecated: bool = False
    supersedes: str = ""
    replaced_by: str = ""
    aliases: tuple[str, ...] = ()  # explicit routing vocabulary (high weight)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(self.tags)
        d["aliases"] = list(self.aliases)
        return d


class Registry:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or os.path.join(BOOM, "cache", "registry.sqlite3")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    # ---------------------------------------------------------------- storage
    def _init_db(self) -> None:
        c = sqlite3.connect(self.db_path)
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                trigger TEXT NOT NULL,
                path TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                cost INTEGER NOT NULL DEFAULT 1,
                deprecated INTEGER NOT NULL DEFAULT 0,
                supersedes TEXT DEFAULT '',
                replaced_by TEXT DEFAULT '',
                body_hash TEXT DEFAULT '',
                registered_at REAL
            );
            CREATE INDEX IF NOT EXISTS ix_comp_kind ON components(kind, deprecated);
            CREATE VIRTUAL TABLE IF NOT EXISTS comp_fts USING fts5(
                id UNINDEXED, title, trigger, tags, tokenize='porter'
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                type TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'draft',
                path TEXT NOT NULL,
                sources TEXT NOT NULL DEFAULT '[]',
                skills TEXT NOT NULL DEFAULT '[]',
                scripts TEXT NOT NULL DEFAULT '[]',
                agents TEXT NOT NULL DEFAULT '[]',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_art_project ON artifacts(project_id, type);
            CREATE TABLE IF NOT EXISTS lineage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                note TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS trace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                component_id TEXT,
                action TEXT NOT NULL,
                detail TEXT
            );
            """
        )
        c.commit()
        c.close()

    # ----------------------------------------------------------------- writes
    def register(self, d: Descriptor) -> None:
        if len(d.trigger) > MAX_DESCRIPTOR_CHARS:
            raise ValueError(
                f"{d.id}: trigger is {len(d.trigger)} chars; discovery descriptors "
                f"must be <= {MAX_DESCRIPTOR_CHARS}. Put the detail in the body."
            )
        c = sqlite3.connect(self.db_path)
        c.execute(
            """INSERT INTO components
               (id,kind,title,trigger,path,tags,cost,deprecated,supersedes,replaced_by,aliases,registered_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 kind=excluded.kind, title=excluded.title, trigger=excluded.trigger,
                 path=excluded.path, tags=excluded.tags, cost=excluded.cost,
                 deprecated=excluded.deprecated, supersedes=excluded.supersedes,
                 replaced_by=excluded.replaced_by, aliases=excluded.aliases""",
            (
                d.id, d.kind, d.title, d.trigger, d.path, ",".join(d.tags),
                d.cost, int(d.deprecated), d.supersedes, d.replaced_by,
                ",".join(d.aliases), time.time(),
            ),
        )
        c.execute("DELETE FROM comp_fts WHERE id=?", (d.id,))
        c.execute(
            "INSERT INTO comp_fts (id,title,trigger,tags) VALUES (?,?,?,?)",
            (d.id, d.title, d.trigger + " " + " ".join(d.aliases), ",".join(d.tags)),
        )
        c.execute("INSERT INTO trace(ts,component_id,action,detail) VALUES (?,?,?,?)",
                  (time.time(), d.id, "register", d.kind))
        c.commit()
        c.close()

    def deprecate(self, component_id: str, replaced_by: str = "") -> None:
        c = sqlite3.connect(self.db_path)
        c.execute(
            "UPDATE components SET deprecated=1, replaced_by=? WHERE id=?",
            (replaced_by, component_id),
        )
        c.execute("INSERT INTO trace(ts,component_id,action,detail) VALUES (?,?,?,?)",
                  (time.time(), component_id, "deprecate", replaced_by))
        c.commit()
        c.close()

    def trace(self, component_id: str, action: str, detail: str = "") -> None:
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO trace(ts,component_id,action,detail) VALUES (?,?,?,?)",
                  (time.time(), component_id, action, detail))
        c.commit()
        c.close()

    def trace_rows(self, action: str | None = None, limit: int = 500) -> list[tuple]:
        """Read back the audit trail (used by context.audit and validator)."""
        c = sqlite3.connect(self.db_path)
        sql, params = "SELECT component_id, action, detail, ts FROM trace", []
        if action:
            sql += " WHERE action=?"
            params.append(action)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = c.execute(sql, params).fetchall()
        c.close()
        return rows

    # -------------------------------------------------------------- discovery
    def find(self, query: str, kind: str | None = None, limit: int = 5) -> list[Descriptor]:
        """Cheap discovery. Returns descriptors, never bodies."""
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        if query.strip():
            q = " OR ".join(f'"{t}"' for t in query.split()[:8])
            sql = (
                "SELECT c.* FROM comp_fts f JOIN components c ON c.id=f.id "
                f"WHERE comp_fts MATCH ?"
            )
            params: list[Any] = [q]
            if kind:
                sql += " AND c.kind=?"
                params.append(kind)
            sql += " AND c.deprecated=0 ORDER BY rank LIMIT ?"
            params.append(limit)
            rows = c.execute(sql, params).fetchall()
        else:
            sql = "SELECT * FROM components WHERE deprecated=0"
            params = []
            if kind:
                sql += " AND kind=?"
                params.append(kind)
            sql += " ORDER BY id LIMIT ?"
            params.append(limit)
            rows = c.execute(sql, params).fetchall()
        c.close()
        return [self._row(r) for r in rows]

    def get(self, component_id: str) -> Descriptor | None:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        r = c.execute("SELECT * FROM components WHERE id=?", (component_id,)).fetchone()
        c.close()
        return self._row(r) if r else None

    def all(self, kind: str | None = None, include_deprecated: bool = False) -> list[Descriptor]:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        sql = "SELECT * FROM components"
        where, params = [], []
        if kind:
            where.append("kind=?")
            params.append(kind)
        if not include_deprecated:
            where.append("deprecated=0")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY kind, id"
        rows = c.execute(sql, params).fetchall()
        c.close()
        return [self._row(r) for r in rows]

    def stats(self) -> dict[str, int]:
        c = sqlite3.connect(self.db_path)
        out = {}
        for (kind,) in c.execute("SELECT DISTINCT kind FROM components"):
            live = c.execute(
                "SELECT count(*) FROM components WHERE kind=? AND deprecated=0", (kind,)
            ).fetchone()[0]
            dep = c.execute(
                "SELECT count(*) FROM components WHERE kind=? AND deprecated=1", (kind,)
            ).fetchone()[0]
            out[kind] = live + dep
            out[f"{kind}_deprecated"] = dep
        c.close()
        return out

    @staticmethod
    def _row(r: sqlite3.Row) -> Descriptor:
        return Descriptor(
            id=r["id"], kind=r["kind"], title=r["title"], trigger=r["trigger"],
            path=r["path"], tags=tuple(t for t in (r["tags"] or "").split(",") if t),
            cost=r["cost"], deprecated=bool(r["deprecated"]),
            supersedes=r["supersedes"] or "", replaced_by=r["replaced_by"] or "",
            aliases=tuple(a for a in (r["aliases"] or "").split(",") if a),
        )

    # -------------------------------------------------------------- artifacts
    def put_artifact(
        self,
        artifact_id: str,
        project_id: str,
        type: str,
        path: str,
        sources: list[str] | None = None,
        skills: list[str] | None = None,
        scripts: list[str] | None = None,
        agents: list[str] | None = None,
        status: str = "draft",
    ) -> None:
        now = time.time()
        c = sqlite3.connect(self.db_path)
        prev = c.execute("SELECT version FROM artifacts WHERE artifact_id=?",
                         (artifact_id,)).fetchone()
        version = (prev[0] + 1) if prev else 1
        c.execute(
            """INSERT INTO artifacts
               (artifact_id,project_id,type,version,status,path,sources,skills,scripts,agents,created_at,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(artifact_id) DO UPDATE SET
                 version=excluded.version, status=excluded.status, path=excluded.path,
                 sources=excluded.sources, skills=excluded.skills,
                 scripts=excluded.scripts, agents=excluded.agents,
                 updated_at=excluded.updated_at""",
            (artifact_id, project_id, type, version, status, path,
             json.dumps(sources or []), json.dumps(skills or []),
             json.dumps(scripts or []), json.dumps(agents or []), now, now),
        )
        c.execute("INSERT INTO trace(ts,component_id,action,detail) VALUES (?,?,?,?)",
                  (now, artifact_id, "artifact", f"{type} v{version} {status}"))
        c.commit()
        c.close()

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        r = c.execute("SELECT * FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
        c.close()
        if not r:
            return None
        d = dict(r)
        for k in ("sources", "skills", "scripts", "agents"):
            d[k] = json.loads(d[k])
        return d

    def artifacts(self, project_id: str | None = None, type: str | None = None) -> list[dict[str, Any]]:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        sql, params = "SELECT * FROM artifacts WHERE 1=1", []
        if project_id:
            sql += " AND project_id=?"
            params.append(project_id)
        if type:
            sql += " AND type=?"
            params.append(type)
        sql += " ORDER BY updated_at DESC"
        rows = [dict(r) for r in c.execute(sql, params).fetchall()]
        c.close()
        for r in rows:
            for k in ("sources", "skills", "scripts", "agents"):
                r[k] = json.loads(r[k])
        return rows

    def link(self, parent_id: str, child_id: str, relation: str, note: str = "") -> None:
        c = sqlite3.connect(self.db_path)
        c.execute(
            "INSERT INTO lineage(parent_id,child_id,relation,note) VALUES (?,?,?,?)",
            (parent_id, child_id, relation, note),
        )
        c.commit()
        c.close()


if __name__ == "__main__":
    import sys

    r = Registry()
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print(json.dumps(r.stats(), indent=2))
    elif len(sys.argv) > 2 and sys.argv[1] == "find":
        for d in r.find(" ".join(sys.argv[2:]), limit=8):
            print(f"[{d.kind:7}] {d.id:28} cost={d.cost}  {d.trigger[:90]}")
    elif len(sys.argv) > 2 and sys.argv[1] == "get":
        d = r.get(sys.argv[2])
        print(json.dumps(d.to_dict(), indent=2) if d else "not found")
    else:
        print("usage: registry.py stats | find <query> | get <id>")