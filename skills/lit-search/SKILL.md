---
name: lit-search
description: Unified literature search across PubMed, arXiv, bioRxiv, Semantic Scholar, and OpenAlex. Results auto-imported into Zotero. Powered by OpenClaw Medical Skills + ARS.
metadata:
  type: skill
  tags: [literature, search, pubmed, arxiv, zotero]
---

# Unified Literature Search

## Purpose
Search multiple academic databases simultaneously from a topic description, deduplicate results, rank by relevance, and auto-import into Zotero for downstream processing.

## When to Use
- User provides a research topic / question and needs to find relevant papers
- User wants to expand their literature base before gap analysis
- User needs to update their Zotero library with recent publications

## Search Strategy (Multi-Source Parallel)

### 1. PubMed (Biomedical)
Trigger the `pubmed-search` or `pubmed-database` skill from OpenClaw Medical Skills.
Use MeSH terms for precision. Best for: clinical, biomedical, life sciences.

### 2. Semantic Scholar / OpenAlex (Cross-disciplinary)
Trigger the `openalex-database` or `deep-research` skill.
Use natural language queries. Best for: CS, engineering, interdisciplinary.

### 3. arXiv / bioRxiv / medRxiv (Preprints)
Trigger the `arxiv-search`, `biorxiv-database`, or `medrxiv-search` skills.
Best for: cutting-edge, not-yet-published work.

### 4. Citation chasing (snowballing)
For each highly relevant paper found:
- Backward: check its references (cited papers)
- Forward: check papers that cite it (via Semantic Scholar / OpenAlex citation graph)

### 5. Manual Import (user-provided database exports)
Support user uploading exported files from proprietary databases:
- **Embase**: .ris / .bib / .txt
- **Web of Science**: .ris / .bib / .txt
- **Scopus**: .ris / .bib / .csv
- **Cochrane Library**: .ris / .txt
- **CNKI (知网)**: .txt (EndNote format)
- **WanFang (万方)**: .txt
- Parse with `bibliography_agent` or manual RIS/BibTeX parser
- Normalize to same format as automated results, merge and cross-deduplicate by DOI + title similarity

## Workflow

### Step 1: Source selection
Ask user which automated databases + which manual databases to use (see Phase 1 Step 1.1).

### Step 2: Parse user topic into search queries
- Extract key concepts, synonyms, and MeSH terms
- Formulate 3-5 query variants per database

### Step 2: Execute parallel searches
Run searches across all selected databases. Collect:
- Title, authors, year, DOI, abstract, citation count
- Direct PDF link (Unpaywall / OA button) when available

### Step 3: Deduplicate and rank
- Remove duplicates by DOI (primary) and title similarity (secondary)
- Rank by: relevance × citation count × recency
- Mark: "must-read" (top 10), "relevant" (top 50), "background" (rest)

### Step 4: Import into Zotero
Use `pyzotero` or the Zotero browser connector to add items to a named collection.

For pyzotero API approach (requires Zotero API key in config):
```python
from pyzotero import zotero
zot = zotero.Zotero(library_id, 'user', api_key)
# Create collection, add items with DOI, attach PDFs
```

If Zotero API key not configured, guide the user to:
1. Generate key at https://www.zotero.org/settings/keys
2. Add `api_key` and `library_id` to `config/zotero_config.json`
3. Re-run import

### Step 5: Trigger PDF extraction
After import, trigger `zotero-lit-index` skill to extract full-text and rebuild index.

## Output Format
```
Search results for: [topic]
- Total found: X (after dedup)
- Must-read (top 10): [list with DOI, relevance score, 1-line reason]
- Relevant (top 50): [count]
- Imported to Zotero collection: [collection name]
- PDFs attached: Y / Z
```

## Key Skills to Leverage
| Skill | Source | Purpose |
|-------|--------|---------|
| `pubmed-search` | OpenClaw | PubMed literature search |
| `pubmed-database` | OpenClaw | PubMed direct API |
| `openalex-database` | OpenClaw | Cross-disciplinary search |
| `arxiv-search` | OpenClaw | Preprint search |
| `biorxiv-database` | OpenClaw | bioRxiv preprints |
| `deep-research` | OpenClaw | Multi-source deep research |
| `literature-review` | OpenClaw | Systematic literature review |
| `pyzotero` | OpenClaw | Zotero API integration |
