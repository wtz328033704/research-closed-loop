# Research Closed-Loop · 学术自动化闭环

A hallucination-free academic research automation system integrating **Google NotebookLM + Claude Code + Zotero + ARS + OpenClaw Medical Skills**.

> Input a research topic → automatic literature search → source-grounded Q&A → gap analysis → hypothesis generation → interactive planning → writing with verified citations → Zotero sync.

[中文说明](README_zh.md)

---

## Architecture

```
User inputs research topic
     ↓
Phase 0  Setup       → Environment check + skill verification + credential dashboard
Phase 1  Discovery   → Multi-DB search (PubMed/arXiv/Semantic Scholar/OpenAlex + manual Embase/WoS/CNKI)
Phase 2  Deep Read   → PDF extraction → NotebookLM source-grounded Q&A (zero hallucination)
Phase 3  Gap Analysis → Contradiction detection → feasibility ranking → hypothesis generation
Phase 4  Planning    → Socratic dialog → methodology blueprint
Phase 4.5 Data Upload → (Optional) real data/figures → cross-ref with literature
Phase 5  Writing     → Section drafting → sentence-level source tracing → auto-citation → format output
Phase 6  Revision    → Feedback iteration → Zotero bidirectional sync
```

Every phase has a 🛑 **human-in-the-loop gate** — the system pauses and waits for your explicit confirmation before proceeding.

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- [Zotero](https://www.zotero.org/) (with Better BibTeX plugin recommended)
- A Google account with NotebookLM access
- Claude Code (with ARS plugin & OpenClaw Medical Skills)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/research-closed-loop.git
cd research-closed-loop

# 2. Install Python dependencies
pip install pyzotero PyMuPDF markitdown chromadb google-genai notebooklm-mcp-cli bibtexparser

# 3. Install NotebookLM MCP CLI
pip install notebooklm-mcp-cli

# 4. Copy and edit config
cp config/zotero_config.template.json config/zotero_config.json
# Edit config/zotero_config.json with your Zotero paths, API keys, and Gemini key

# 5. Authenticate NotebookLM
nlm login

# 6. Verify setup
python scripts/env_setup.py
```

### Configuration

Edit `config/zotero_config.json`:

| Field | Where to get it |
|-------|----------------|
| `zotero.api_key` | https://www.zotero.org/settings/keys → "Create New Private Key" |
| `zotero.library_id` | Same page — your numeric User ID |
| `zotero.data_dir` | Your Zotero data directory (contains `zotero.sqlite` and `storage/`) |
| `zotero.install_path` | Your Zotero application directory |
| `notebooklm.gemini_api_key` | https://aistudio.google.com/apikey |
| `notebooklm.gemini_model` | Default: `gemini-2.5-pro` |

### Start Researching

In Claude Code, say:

```
帮我研究 [your topic]
```

Or jump to a specific phase:

```
帮我搜索关于 [topic] 的文献      → Phase 1
帮我读这些论文                    → Phase 2
找出这个领域的研究空白             → Phase 3
帮我规划研究方法                  → Phase 4
帮我写文献综述                    → Phase 5
```

---

## Project Structure

```
research-closed-loop/
├── README.md
├── README_zh.md
├── CLAUDE.md                        # Project documentation for Claude Code
├── .gitignore
├── config/
│   ├── zotero_config.template.json   # Template (safe to commit)
│   └── zotero_config.json            # Real config (gitignored)
├── scripts/
│   ├── env_setup.py                  # One-click environment check
│   ├── zotero_connector.py           # Zotero SQLite + pyzotero API reader
│   ├── pdf_extractor.py              # PDF → Markdown batch pipeline
│   ├── metadata_indexer.py           # Literature metadata JSON index
│   ├── ref_importer.py               # RIS/BibTeX/CSV/CNKI parser for manual imports
│   ├── notebooklm_bridge.py          # NotebookLM MCP + Gemini dual-channel bridge
│   └── state_manager.py             # Project state persistence (cross-session resume)
└── skills/
    ├── research-closed-loop/         # ★ Master workflow skill (all 6 phases + HITL gates)
    ├── lit-search/                   # Unified literature search skill
    ├── zotero-lit-index/             # Zotero literature index skill
    ├── notebooklm-qa/                # Source-grounded Q&A skill
    ├── gap-finder/                   # Research gap analysis skill
    └── citation-writer/              # Hallucination-free writing with citations
```

---

## Key Features

### Zero-Hallucination Citation Protocol
- Every factual claim must be traceable to a source document in Zotero
- NotebookLM answers are source-grounded by design (only uses uploaded sources)
- During writing, every sentence with a factual claim runs through source verification
- Unverifiable claims are flagged and NEVER included in the final output

### Human-in-the-Loop Gates
- 8 mandatory checkpoints where the system pauses for user confirmation
- User selects papers, notebook, research gap, approves plan, reviews each section
- No automatic pass-through — you control every decision

### Dual Writing Modes
- **Review Mode**: High-quality systematic/narrative review for top-tier journals (PRISMA 2020)
- **Data-Driven Mode**: Original research article with real experimental data, customized to target journal style (AJSM, BJSM, Nature, etc.)

### Multi-Database Import
- Automated: PubMed, arXiv, bioRxiv, Semantic Scholar, OpenAlex
- Manual: Embase, Web of Science, Scopus, Cochrane, CNKI, WanFang (RIS/BibTeX/CSV)

---

## Skills That Power This Workflow

### ARS Plugin (Academic Research Skills)
`ars-outline` · `ars-lit-review` · `ars-plan` · `ars-citation-check` · `ars-abstract` · `ars-format-convert` · `ars-revision` · `ars-revision-coach`

### OpenClaw Medical Skills (869 curated skills)
`pubmed-search` · `scientific-writing` · `scientific-manuscript` · `literature-review` · `peer-review` · `hypothesis-generation` · `scientific-problem-selection` · `knowledge-synthesis` · `citation-management` · `pyzotero` · `deep-research` · and 850+ more

---

## License

MIT
