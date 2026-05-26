"""
PDF extraction pipeline: Zotero PDF -> Markdown -> chunked text.
Uses PyMuPDF for fast text extraction + markitdown for structure.
Outputs chunked text with source metadata for NotebookLM upload / RAG.
"""
import json, os, sys
from pathlib import Path
from typing import Optional
import fitz
from markitdown import MarkItDown

sys.path.insert(0, str(Path(__file__).parent))
from zotero_connector import ZoteroConnector


class PDFExtractor:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "zotero_config.json"
        with open(config_path) as f:
            self.config = json.load(f)
        self.chunk_size = self.config["extraction"]["chunk_size"]
        self.chunk_overlap = self.config["extraction"]["chunk_overlap"]
        self.zotero = ZoteroConnector(config_path)
        self.md_converter = MarkItDown()

    def extract_single(self, pdf_path: str, item_key: str = None) -> dict:
        item_meta = {}
        if item_key:
            item_meta = self.zotero.get_item_by_key(item_key)

        text_parts = []
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                t = page.get_text("text")
                if t.strip():
                    text_parts.append({"page": page_num + 1, "text": t, "char_count": len(t)})

        full_text = "\n\n".join(p["text"] for p in text_parts)

        # Use markitdown for richer structure on smaller files
        try:
            if os.path.getsize(pdf_path) < 50 * 1024 * 1024:
                md_result = self.md_converter.convert(pdf_path)
                full_text = md_result.text_content if hasattr(md_result, "text_content") else str(md_result)
        except Exception:
            pass

        chunks = self._chunk_text(full_text, item_meta.get("title", ""),
                                  item_meta.get("citation_key", ""))

        return {
            "filename": os.path.basename(pdf_path), "pdf_path": pdf_path,
            "item_key": item_key,
            "title": item_meta.get("title", ""),
            "authors": item_meta.get("authors", []),
            "year": item_meta.get("year", ""),
            "doi": item_meta.get("doi", ""),
            "citation_key": item_meta.get("citation_key", ""),
            "total_pages": len(text_parts), "total_chars": len(full_text),
            "total_chunks": len(chunks), "full_text": full_text, "chunks": chunks,
        }

    def batch_extract(self, collection_name: str = None, max_items: int = 20,
                      output_dir: str = None) -> list[dict]:
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "data" / "extracted"
        os.makedirs(output_dir, exist_ok=True)

        items = self.zotero.get_items_by_collection(collection_name, limit=max_items)
        results = []
        for item in items:
            pdf_path = self.zotero.find_pdf_for_item(item["key"])
            if not pdf_path:
                continue
            print(f"Extracting: {item['title'][:80]}...")
            try:
                extracted = self.extract_single(pdf_path, item["key"])
                results.append(extracted)
                out_name = f"{item['key']}.json"
                with open(os.path.join(output_dir, out_name), "w", encoding="utf-8") as f:
                    json.dump(extracted, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"  ERROR: {e}")

        manifest = {
            "collection": collection_name, "total_extracted": len(results),
            "items": [{"key": r["item_key"], "title": r["title"],
                        "chunks": r["total_chunks"], "citation_key": r["citation_key"]}
                      for r in results],
        }
        with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"\nDone. {len(results)} PDFs extracted -> {output_dir}")
        return results

    def _chunk_text(self, text: str, title: str, cite_key: str) -> list[dict]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            if len(chunk_words) < 50:
                continue
            chunks.append({
                "chunk_id": len(chunks),
                "chunk_text": " ".join(chunk_words),
                "word_count": len(chunk_words),
                "source_title": title,
                "citation_key": cite_key,
                "start_pos": i,
            })
        return chunks

    def close(self):
        self.zotero.close()


if __name__ == "__main__":
    ext = PDFExtractor()
    stats = ext.zotero.get_stats()
    if stats.get("empty_library"):
        print("Zotero library is empty. Add papers first, then run extraction.")
    else:
        results = ext.batch_extract(max_items=3)
        for r in results:
            print(f"  {r['title'][:80]} - {r['total_chunks']} chunks, {r['total_chars']} chars")
    ext.close()
