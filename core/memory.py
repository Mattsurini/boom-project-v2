#!/usr/bin/env python
"""
hermes.core.memory — Memory Manager.

Three stores, one owner each. The previous architecture had four and no owner,
which is why nothing was trustworthy.

    Notes (markdown, human-written)   SOURCE OF TRUTH
    registry.sqlite3 / boom_project_registry  INDEX + RETRIEVAL
    Hermes holographic provider        ALWAYS-ON RUNTIME CONTEXT

Rules enforced here:
  * Hermes is never a database of record. Writes go to Notes.
  * The index is disposable. If it is lost, it is rebuilt from Notes.
  * Nothing is read into context without passing through the budget.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Any

from .registry import Registry

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")
NOTES_DIR = os.path.join(BOOM, "wiki")
KNOWLEDGE_INDEX = os.path.join(BOOM, "Knowledge", "indexes")
REGISTRY_DB = os.path.join(BOOM, "cache", "boom_project_registry.sqlite3")
HERMES_MEMORY_DB = os.path.join(BOOM, "cache", "hermes_memory.sqlite3")


def _sha(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:32]


@dataclass
class Retrieval:
    source: str          # "notes" | "index" | "runtime"
    ref: str             # path or fact id
    excerpt: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "ref": self.ref,
                "excerpt": self.excerpt[:300], "score": round(self.score, 3)}


class MemoryManager:
    """Delegates to the right store, and knows which store is authoritative."""

    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()
        self.notes_dir = NOTES_DIR

    # ------------------------------------------------------------- retrieval
    def search(self, query: str, limit: int = 5) -> list[Retrieval]:
        """Dynamic retrieval: index first, notes only when the index misses.

        Order matters — the index is cheap and disposable; Notes are the truth
        but expensive to read.
        """
        hits: list[Retrieval] = []
        hits += self._search_index(query, limit)
        if len(hits) < limit:
            hits += self._search_notes(query, limit - len(hits))
        hits.sort(key=lambda r: -r.score)
        return hits[:limit]

    def _search_index(self, query: str, limit: int) -> list[Retrieval]:
        """Cheap tier. Ranked, not flat: a title hit must outrank a path hit,
        otherwise every result ties and the Notes tier is never consulted."""
        if not os.path.exists(REGISTRY_DB):
            return []
        try:
            c = sqlite3.connect(f"file:{REGISTRY_DB}?mode=ro", uri=True)
            terms = [t for t in re.split(r"\W+", query.lower()) if len(t) > 2][:6]
            if not terms:
                c.close()
                return []
            n = len(terms)
            like = [f"%{t}%" for t in terms]
            # One score placeholder per term; the WHERE clause repeats each term
            # twice (path OR title) and LIMIT takes one more.
            score_expr = " + ".join(
                "(CASE WHEN lower(title) LIKE ? THEN 3 ELSE 0 END)" for _ in range(n))
            score_expr += " + " + " + ".join(
                "(CASE WHEN lower(path_or_url) LIKE ? THEN 1 ELSE 0 END)"
                for _ in range(n))
            where = " OR ".join(
                ["lower(path_or_url) LIKE ? OR lower(title) LIKE ?"] * n)
            # Two directories are excluded from retrieval by design:
            #   .rebuild/    the verified backup — a safety copy that mirrors
            #                every file in the project
            #   .quarantine/ retired harness files that must not be cited as
            #                live knowledge
            # Leaving either in made it the top hit for most queries.
            where += (" AND path_or_url NOT LIKE '%.rebuild%'"
                      " AND path_or_url NOT LIKE '%.quarantine%'")
            sql = (f"SELECT path_or_url, title, ({score_expr}) AS rel "
                   f"FROM sources WHERE {where} ORDER BY rel DESC LIMIT ?")
            params = like + like + [v for t in terms for v in (f"%{t}%", f"%{t}%")] + [limit]
            rows = c.execute(sql, params).fetchall()
            c.close()
            return [Retrieval("index", p, t or "", float(rel or 0))
                    for p, t, rel in rows]
        except Exception as e:
            print(f"_search_index failed: {type(e).__name__}: {e}")
            return []

    def _search_notes(self, query: str, limit: int) -> list[Retrieval]:
        out: list[Retrieval] = []
        terms = [t for t in re.split(r"\W+", query.lower()) if len(t) > 2]
        if not terms:
            return out
        for root in (self.notes_dir, KNOWLEDGE_INDEX):
            if not os.path.isdir(root):
                continue
            # never walk the safety backup — it mirrors the whole project
            for dp, dn, fn in os.walk(root):
                dn[:] = [d for d in dn if d != "_archive"]
                for f in fn:
                    if not f.endswith((".md", ".txt")):
                        continue
                    p = os.path.join(dp, f)
                    try:
                        text = open(p, encoding="utf-8", errors="replace").read()
                    except Exception:
                        continue
                    low = text.lower()
                    score = sum(low.count(t) for t in terms)
                    if score:
                        i = min((low.find(t) for t in terms if low.find(t) >= 0), default=0)
                        out.append(Retrieval(
                            "notes", os.path.relpath(p, BOOM),
                            text[max(0, i - 60): i + 240], float(score)))
            if len(out) >= limit * 2:
                break
        out.sort(key=lambda r: -r.score)
        return out[:limit]

    # ------------------------------------------------------------ selective persistence
    def remember(self, fact: str, category: str = "project",
                 tags: list[str] | None = None) -> str:
        """Selective persistence: only durable facts, written to the runtime store.

        This is deliberately NOT the Notes store. Notes are for things a human
        will read later; this is for things Hermes should know next session.
        """
        if os.path.exists(HERMES_MEMORY_DB):
            try:
                c = sqlite3.connect(HERMES_MEMORY_DB)
                cur = c.execute(
                    "INSERT INTO facts (content, category, created_at) VALUES (?,?,?)"
                    if self._has_col(c, "facts", "content")
                    else "INSERT INTO facts (text) VALUES (?)",
                    (fact, category, time.time()) if self._has_col(c, "facts", "content")
                    else (fact,),
                )
                c.commit()
                c.close()
                return f"fact #{cur.lastrowid}"
            except Exception:
                pass
        # Durable but no store available: file-backed fallback, still not Notes.
        p = os.path.join(BOOM, "cache", "memory_fallback.jsonl")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": time.time(), "fact": fact,
                                 "category": category, "tags": tags or []}) + "\n")
        return "appended to cache/memory_fallback.jsonl"

    @staticmethod
    def _has_col(c: sqlite3.Connection, table: str, col: str) -> bool:
        try:
            return any(r[1] == col for r in c.execute(f"PRAGMA table_info({table})"))
        except sqlite3.Error:
            return False

    # ----------------------------------------------------------------- notes
    def note_path(self, slug: str) -> str:
        os.makedirs(self.notes_dir, exist_ok=True)
        return os.path.join(self.notes_dir, f"{slug}.md")

    def write_note(self, slug: str, body: str, frontmatter: dict | None = None) -> str:
        """Notes are the source of truth and are human-readable by construction."""
        p = self.note_path(slug)
        fm = frontmatter or {}
        meta = "---\n" + "\n".join(
            f"{k}: {json.dumps(v) if isinstance(v,(list,dict)) else v}"
            for k, v in fm.items()) + "\n---\n\n"
        open(p, "w", encoding="utf-8").write(meta + body)
        self.index_note(p)
        return p

    def index_note(self, path: str) -> bool:
        """Rebuild-safe: the index can always be regenerated from Notes.

        Schema is owned by scripts/memory_db.py, not by this module — read the
        real columns rather than assuming them (the earlier version guessed
        `path`/`title` and silently failed against `path_or_url`/`title`).
        """
        if not os.path.exists(REGISTRY_DB):
            return False
        try:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            c = sqlite3.connect(REGISTRY_DB)
            cols = {r[1] for r in c.execute("PRAGMA table_info(sources)")}
            if "path_or_url" not in cols:
                return False
            rel = os.path.relpath(path, BOOM)
            text = open(path, encoding="utf-8", errors="replace").read()
            title = next((l.lstrip("# ").strip() for l in text.splitlines()
                          if l.startswith("#")), os.path.basename(rel))
            row = c.execute(
                "SELECT id FROM sources WHERE path_or_url=?", (rel,)).fetchone()
            if row:
                c.execute(
                    "UPDATE sources SET title=?, updated_at=?, source_hash=? WHERE id=?",
                    (title, now, _sha(text), row[0]))
            else:
                vals = {
                    "title": title, "source_type": "note",
                    "path_or_url": rel, "source_hash": _sha(text),
                    "created_at": now, "updated_at": now, "accessed_at": now,
                    "notes": "written by core/memory.py",
                }
                use = [k for k in vals if k in cols]
                c.execute(
                    f"INSERT INTO sources ({','.join(use)}) VALUES ({','.join('?'*len(use))})",
                    [vals[k] for k in use])
            c.commit()
            c.close()
            return True
        except Exception as e:
            print(f"index_note failed: {type(e).__name__}: {e}")
            return False

    def prune_missing(self) -> int:
        """Drop index rows whose file no longer exists.

        The index is disposable and rebuildable, so a row pointing at a deleted
        path is worse than useless — it makes retrieval return ghosts. After a
        teardown this is how the index stops lying.
        """
        if not os.path.exists(REGISTRY_DB):
            return 0
        try:
            c = sqlite3.connect(REGISTRY_DB)
            rows = c.execute(
                "SELECT id, path_or_url FROM sources").fetchall()
            gone = [(i, p) for i, p in rows
                    if not p.lower().startswith(("http://", "https://"))
                    and not os.path.exists(os.path.join(BOOM, p))]
            for i, _ in gone:
                c.execute("DELETE FROM sources WHERE id=?", (i,))
            c.commit()
            c.close()
            return len(gone)
        except Exception as e:
            print(f"prune_missing failed: {type(e).__name__}: {e}")
            return 0

    def reindex_all_notes(self) -> int:
        """Notes are the source of truth — this rebuilds the index from them."""
        n = 0
        for dp, dn, fn in os.walk(self.notes_dir):
            dn[:] = [d for d in dn if d != "_archive"]
            for f in fn:
                if f.endswith((".md", ".txt")) and self.index_note(os.path.join(dp, f)):
                    n += 1
        return n

    def status(self) -> str:
        lines = ["MEMORY STATUS", "=" * 46]
        lines.append(f"Notes (source of truth) : {self.notes_dir}")
        n = sum(1 for dp, dn, fn in os.walk(self.notes_dir) for f in fn
                if f.endswith((".md", ".txt"))) if os.path.isdir(self.notes_dir) else 0
        lines.append(f"  files: {n}")
        for label, p in (("Retrieval index", REGISTRY_DB),
                         ("Runtime memory", HERMES_MEMORY_DB)):
            if os.path.exists(p):
                lines.append(f"{label:25}: {os.path.basename(p)} "
                             f"({os.path.getsize(p)/1e6:.2f} MB) — disposable, rebuildable")
            else:
                lines.append(f"{label:25}: MISSING")
        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    m = MemoryManager()
    print(m.status())
    if len(sys.argv) > 1:
        print("\nRETRIEVAL:", " ".join(sys.argv[1:]))
        for r in m.search(" ".join(sys.argv[1:])):
            print(f"  [{r.source}] {r.ref}  score={r.score:.1f}")
            print(f"      {r.excerpt[:160]}")