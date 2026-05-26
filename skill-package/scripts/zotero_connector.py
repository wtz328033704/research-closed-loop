"""
Zotero connector — reads local Zotero library via SQLite (fast) + pyzotero API (cloud).
Handles empty libraries gracefully. Primary: local SQLite. Fallback: pyzotero Web API.
"""
import json
import sqlite3
import os
import re
from pathlib import Path
from typing import Optional


class ZoteroConnector:
    """Read Zotero library from local SQLite (read-only, auto-copies if locked)."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "zotero_config.json"
        with open(config_path) as f:
            self.config = json.load(f)
        self.sqlite_path = self.config["zotero"]["sqlite_path"]
        self.storage_dir = self.config["zotero"]["storage_dir"]
        self._conn: Optional[sqlite3.Connection] = None
        self._temp_db: Optional[str] = None
        self._has_tables: Optional[bool] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(self.sqlite_path)
                self._conn.execute("PRAGMA query_only = ON")
            except sqlite3.OperationalError:
                import tempfile, shutil
                tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
                tmp.close()
                shutil.copy2(self.sqlite_path, tmp.name)
                self._conn = sqlite3.connect(tmp.name)
                self._temp_db = tmp.name
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
        if self._temp_db and os.path.exists(self._temp_db):
            os.unlink(self._temp_db)
            self._temp_db = None

    @property
    def is_empty(self) -> bool:
        """Check if the Zotero library has any data."""
        if self._has_tables is not None:
            return self._has_tables
        try:
            tables = [r[0] for r in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "items" not in tables:
                self._has_tables = True
                return True
            count = self.conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            self._has_tables = count == 0
        except Exception:
            self._has_tables = True
        return self._has_tables

    # ── Library stats ──────────────────────────────────────────

    def get_stats(self) -> dict:
        if self.is_empty:
            return {"total_items": 0, "pdfs": 0, "notes": 0,
                    "unique_tags": 0, "collections": 0, "empty_library": True}
        c = self.conn
        try:
            total = c.execute("SELECT COUNT(*) FROM items WHERE itemTypeID != 14").fetchone()[0]
            pdfs  = c.execute("SELECT COUNT(*) FROM itemAttachments WHERE contentType='application/pdf'").fetchone()[0]
            notes = c.execute("SELECT COUNT(*) FROM itemNotes").fetchone()[0]
            tags  = c.execute("SELECT COUNT(DISTINCT tagID) FROM itemTags").fetchone()[0]
            colls = c.execute("SELECT COUNT(*) FROM collections").fetchone()[0]
        except sqlite3.OperationalError:
            return {"total_items": 0, "pdfs": 0, "notes": 0,
                    "unique_tags": 0, "collections": 0, "empty_library": True}
        return {"total_items": total, "pdfs": pdfs, "notes": notes,
                "unique_tags": tags, "collections": colls}

    # ── Item retrieval (safe) ───────────────────────────────────

    def get_items_by_collection(self, collection_name: str = None, limit: int = 500) -> list[dict]:
        if self.is_empty:
            return []
        c = self.conn
        try:
            if collection_name:
                rows = c.execute("""
                    SELECT DISTINCT i.itemID, i.key, fd.itemTypeID
                    FROM items i
                    JOIN collectionItems ci ON i.itemID = ci.itemID
                    JOIN collections co ON ci.collectionID = co.collectionID
                    JOIN fieldData fd ON i.itemID = fd.itemID
                    WHERE co.collectionName = ? AND i.itemTypeID != 14
                    LIMIT ?
                """, (collection_name, limit)).fetchall()
            else:
                rows = c.execute("""
                    SELECT DISTINCT i.itemID, i.key, fd.itemTypeID
                    FROM items i
                    JOIN fieldData fd ON i.itemID = fd.itemID
                    WHERE i.itemTypeID != 14
                    LIMIT ?
                """, (limit,)).fetchall()
        except sqlite3.OperationalError:
            return []
        return [self._build_item_dict(r["itemID"], r["key"], r["itemTypeID"]) for r in rows]

    def search_items(self, query: str, limit: int = 100) -> list[dict]:
        if self.is_empty:
            return []
        c = self.conn
        try:
            rows = c.execute("""
                SELECT DISTINCT i.itemID, i.key, fd.itemTypeID
                FROM items i
                JOIN fieldData fd ON i.itemID = fd.itemID
                JOIN itemData idt ON i.itemID = idt.itemID
                JOIN itemDataValues idv ON idt.valueID = idv.valueID
                WHERE idv.value LIKE ? AND i.itemTypeID != 14
                LIMIT ?
            """, (f"%{query}%", limit)).fetchall()
        except sqlite3.OperationalError:
            return []
        return [self._build_item_dict(r["itemID"], r["key"], r["itemTypeID"]) for r in rows]

    def get_item_by_key(self, key: str) -> dict:
        if self.is_empty:
            return {}
        c = self.conn
        try:
            row = c.execute("SELECT itemID, key FROM items WHERE key = ?", (key,)).fetchone()
            if not row:
                return {}
            iid = c.execute("SELECT itemTypeID FROM fieldData WHERE itemID = ?",
                            (row["itemID"],)).fetchone()
            return self._build_item_dict(row["itemID"], row["key"],
                                         iid["itemTypeID"] if iid else 0)
        except sqlite3.OperationalError:
            return {}

    # ── PDF attachments ────────────────────────────────────────

    def get_pdf_attachments(self, limit: int = None) -> list[dict]:
        if self.is_empty:
            return []
        c = self.conn
        try:
            q = """SELECT ia.itemID, ia.parentItemID, ia.path, ia.key as attKey,
                   i.key as parentKey
                   FROM itemAttachments ia
                   JOIN items i ON ia.parentItemID = i.itemID
                   WHERE ia.contentType = 'application/pdf'
                   ORDER BY ia.itemID DESC"""
            rows = c.execute(q + (" LIMIT ?" if limit else ""),
                             (limit,) if limit else ()).fetchall()
        except sqlite3.OperationalError:
            return []
        results = []
        for r in rows:
            full_path = os.path.join(self.storage_dir, r["path"])
            exists = os.path.exists(full_path)
            results.append({
                "attachment_id": r["itemID"], "parent_item_id": r["parentItemID"],
                "parent_key": r["parentKey"], "attachment_key": r["attKey"],
                "relative_path": r["path"], "full_path": full_path,
                "exists_on_disk": exists,
                "size_mb": round(os.path.getsize(full_path) / 1048576, 2) if exists else 0,
            })
        return results

    def find_pdf_for_item(self, item_key: str) -> Optional[str]:
        if self.is_empty:
            return None
        c = self.conn
        try:
            row = c.execute("""SELECT ia.path FROM itemAttachments ia
                               JOIN items i ON ia.parentItemID = i.itemID
                               WHERE i.key = ? AND ia.contentType = 'application/pdf'
                               LIMIT 1""", (item_key,)).fetchone()
        except sqlite3.OperationalError:
            return None
        if not row:
            return None
        full_path = os.path.join(self.storage_dir, row["path"])
        return full_path if os.path.exists(full_path) else None

    # ── Citation keys ──────────────────────────────────────────

    def get_citation_key(self, item_key: str) -> Optional[str]:
        if self.is_empty:
            return None
        c = self.conn
        try:
            row = c.execute("""SELECT idv.value FROM itemData idt
                               JOIN itemDataValues idv ON idt.valueID = idv.valueID
                               JOIN fields f ON idt.fieldID = f.fieldID
                               JOIN items i ON idt.itemID = i.itemID
                               WHERE i.key = ? AND f.fieldName = 'extra'
                            """, (item_key,)).fetchone()
        except sqlite3.OperationalError:
            return None
        if not row:
            return None
        m = re.search(r'citation-key:\s*(\S+)', row["value"] or "", re.I)
        return m.group(1) if m else None

    # ── Collections ────────────────────────────────────────────

    def list_collections(self) -> list[dict]:
        if self.is_empty:
            return []
        try:
            rows = self.conn.execute(
                "SELECT collectionID, collectionName, parentCollectionID "
                "FROM collections ORDER BY collectionName").fetchall()
        except sqlite3.OperationalError:
            return []
        return [{"id": r["collectionID"], "name": r["collectionName"],
                 "parent_id": r["parentCollectionID"]} for r in rows]

    # ── Internal helpers ───────────────────────────────────────

    def _build_item_dict(self, item_id: int, key: str, item_type_id: int) -> dict:
        c = self.conn
        type_row = c.execute("SELECT typeName FROM itemTypes WHERE itemTypeID = ?",
                             (item_type_id,)).fetchone()
        item_type = type_row["typeName"] if type_row else "unknown"

        field_data = {}
        for row in c.execute("""SELECT f.fieldName, idv.value FROM itemData idt
                                JOIN fields f ON idt.fieldID = f.fieldID
                                JOIN itemDataValues idv ON idt.valueID = idv.valueID
                                WHERE idt.itemID = ?""", (item_id,)):
            fname = row["fieldName"]
            if fname not in field_data:
                field_data[fname] = row["value"]

        creators = []
        for row in c.execute("""SELECT c.firstName, c.lastName, ct.creatorType
                                FROM creators c
                                JOIN itemCreators ic ON c.creatorID = ic.creatorID
                                JOIN creatorTypes ct ON ic.creatorTypeID = ct.creatorTypeID
                                WHERE ic.itemID = ? ORDER BY ic.orderIndex""", (item_id,)):
            name = f"{row['firstName'] or ''} {row['lastName'] or ''}".strip()
            if name:
                creators.append({"name": name, "type": row["creatorType"]})

        tags = [r["name"] for r in c.execute(
            "SELECT t.name FROM tags t JOIN itemTags it ON t.tagID = it.tagID WHERE it.itemID = ?",
            (item_id,))]

        collections = [r["collectionName"] for r in c.execute(
            "SELECT co.collectionName FROM collections co "
            "JOIN collectionItems ci ON co.collectionID = ci.collectionID WHERE ci.itemID = ?",
            (item_id,))]

        attachments = []
        for row in c.execute(
            "SELECT ia.path, ia.contentType, ia.key FROM itemAttachments ia "
            "WHERE ia.parentItemID = ? AND ia.contentType = 'application/pdf'", (item_id,)):
            full_path = os.path.join(self.storage_dir, row["path"])
            attachments.append({
                "key": row["key"], "path": full_path,
                "exists": os.path.exists(full_path),
                "size_mb": round(os.path.getsize(full_path) / 1048576, 2)
                if os.path.exists(full_path) else 0,
            })

        cite_key = self.get_citation_key(key)
        date = field_data.get("date", "")
        year = date[:4] if date else ""

        return {
            "item_id": item_id, "key": key,
            "title": field_data.get("title", "Untitled"),
            "item_type": item_type,
            "authors": [c["name"] for c in creators if c["type"] == "author"],
            "year": year, "date": date,
            "doi": field_data.get("DOI", ""),
            "url": field_data.get("url", ""),
            "abstract": field_data.get("abstractNote", ""),
            "tags": tags, "collections": collections,
            "publication": field_data.get("publicationTitle", ""),
            "volume": field_data.get("volume", ""),
            "issue": field_data.get("issue", ""),
            "pages": field_data.get("pages", ""),
            "date_added": field_data.get("dateAdded", ""),
            "citation_key": cite_key or "",
            "attachments": attachments,
            "extra": field_data.get("extra", ""),
        }


if __name__ == "__main__":
    zc = ZoteroConnector()
    stats = zc.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    if not stats.get("empty_library"):
        colls = zc.list_collections()
        print(f"\nCollections ({len(colls)}):")
        for c in colls[:10]:
            print(f"  {c['name']}")
        items = zc.get_items_by_collection(limit=5)
        print(f"\nRecent items ({len(items)}):")
        for item in items:
            print(f"  [{item['year']}] {item['title'][:80]}")
    zc.close()
