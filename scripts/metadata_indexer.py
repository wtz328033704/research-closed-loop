"""
Metadata indexer: builds a searchable JSON index from the Zotero library.
Supports incremental updates and exports citation-key -> item mappings.
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from zotero_connector import ZoteroConnector


class MetadataIndexer:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "zotero_config.json"
        with open(config_path) as f:
            self.config = json.load(f)
        self.index_path = self.config["index"]["index_path"]
        self.zotero = ZoteroConnector(config_path)

    def build_index(self, force: bool = False) -> dict:
        """Build or update the JSON metadata index."""
        index = self._load_existing() if not force else {"version": 1, "items": {}}

        stats = self.zotero.get_stats()
        if stats.get("empty_library"):
            print("Zotero library is empty. Nothing to index.")
            return {"version": 1, "items": {}, "generated_at": datetime.now().isoformat(),
                    "empty": True}

        items = self.zotero.get_items_by_collection(limit=10000)
        citations = {}  # citation_key -> item mapping
        dois = {}       # DOI -> item mapping

        for item in items:
            key = item["key"]
            entry = {
                "key": key, "title": item["title"], "item_type": item["item_type"],
                "authors": item["authors"], "year": item["year"], "doi": item["doi"],
                "url": item["url"], "abstract": item["abstract"],
                "tags": item["tags"], "collections": item["collections"],
                "publication": item["publication"],
                "volume": item["volume"], "issue": item["issue"], "pages": item["pages"],
                "citation_key": item["citation_key"],
                "has_pdf": len(item["attachments"]) > 0,
            }
            index["items"][key] = entry

            if item["citation_key"]:
                citations[item["citation_key"]] = key
            if item["doi"]:
                dois[item["doi"].lower()] = key

        index["_citations"] = citations
        index["_dois"] = dois
        index["total_items"] = len(index["items"])
        index["generated_at"] = datetime.now().isoformat()

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        print(f"Index built: {len(index['items'])} items -> {self.index_path}")
        return index

    def lookup_by_citekey(self, cite_key: str) -> dict:
        index = self._load_existing()
        item_key = index.get("_citations", {}).get(cite_key)
        if not item_key:
            return {}
        return index["items"].get(item_key, {})

    def lookup_by_doi(self, doi: str) -> dict:
        index = self._load_existing()
        item_key = index.get("_dois", {}).get(doi.lower())
        if not item_key:
            return {}
        return index["items"].get(item_key, {})

    def search(self, query: str, field: str = "title") -> list[dict]:
        """Simple search over the indexed metadata."""
        index = self._load_existing()
        query_lower = query.lower()
        results = []
        for key, entry in index.get("items", {}).items():
            text = entry.get(field, "").lower()
            if query_lower in text:
                results.append(entry)
        return sorted(results, key=lambda r: r.get("year", ""), reverse=True)

    def _load_existing(self) -> dict:
        if os.path.exists(self.index_path):
            with open(self.index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": 1, "items": {}}

    def close(self):
        self.zotero.close()


if __name__ == "__main__":
    idx = MetadataIndexer()
    result = idx.build_index(force=True)
    idx.close()
