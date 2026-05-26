---
name: zotero-lit-index
description: Zotero literature indexing and full-text extraction. Builds searchable metadata index from local Zotero library, extracts PDF full-text to Markdown, and manages bidirectional citation sync.
metadata:
  type: skill
  tags: [zotero, literature, pdf-extraction, citation, indexing]
---

# Zotero Literature Index

## Purpose
Connect to the local Zotero library, build a searchable metadata index, extract PDF full-text as Markdown, and keep citations synced bidirectionally between Zotero and generated content.

## When to Use
- User wants to search their Zotero library by keyword, author, DOI, or citation key
- User wants to extract full-text from PDFs for NotebookLM upload or RAG
- User wants to sync generated citations back to Zotero
- Before any literature review or research gap analysis — the index must be current

## Workflow

### Step 1: Check library status
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python scripts/zotero_connector.py
```
If `empty_library: true`, inform the user and suggest running the `lit-search` skill first to import papers.

### Step 2: Build / update metadata index
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python scripts/metadata_indexer.py
```
This creates `data/zotero_index.json` with:
- All items keyed by Zotero key
- Citation key → item mapping
- DOI → item mapping

### Step 3: Extract PDF full-text (optional, for specific collection)
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python -c "
from scripts.pdf_extractor import PDFExtractor
ext = PDFExtractor()
ext.batch_extract(collection_name='COLLECTION_NAME', max_items=20)
ext.close()
"
```
Replace `COLLECTION_NAME` with the target collection. Extracted JSON files go to `data/extracted/`.

### Step 4: Lookup
Use `metadata_indexer.py` methods:
- `lookup_by_citekey("cite_key")` — find item by Better BibTeX citation key
- `lookup_by_doi("10.xxx/yyy")` — find item by DOI
- `search("keyword", field="title")` — search across titles

## Key Files
| File | Purpose |
|------|---------|
| `scripts/zotero_connector.py` | Read Zotero SQLite library |
| `scripts/pdf_extractor.py` | PDF → Markdown + chunking |
| `scripts/metadata_indexer.py` | Build/search metadata JSON index |
| `config/zotero_config.json` | Zotero paths and settings |
| `data/zotero_index.json` | Generated metadata index |

## Environment Requirements
- Zotero installed and library synced
- Python packages: `pyzotero`, `PyMuPDF`, `markitdown`
- Better BibTeX Zotero plugin (recommended for citation keys)
