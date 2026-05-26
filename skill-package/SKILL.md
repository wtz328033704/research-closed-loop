---
name: research-closed-loop
description: >
  Complete academic research automation closed loop.
  NotebookLM + Claude Code + Zotero + ARS + OpenClaw.
  Input a research topic → literature search → source-grounded Q&A →
  gap analysis → hypothesis → planning → writing with verified citations.
  15 slash commands: /r /rw /rg /rl /rr /rp /rv /rs /re
metadata:
  version: "1.0.0"
  author: "WTZ328033704"
  repo: "https://github.com/wtz328033704/research-closed-loop"
  license: MIT
  tags:
    - research
    - academic
    - literature-review
    - writing
    - citation
    - zotero
    - notebooklm
    - paper
    - gap-analysis
  dependencies:
    python: ">=3.12"
    packages: [pyzotero, PyMuPDF, markitdown, chromadb, google-genai, bibtexparser, notebooklm-mcp-cli]
    external: [zotero, notebooklm, gemini-api-key]
    plugins: [academic-research-skills, openclaw-medical-skills]
---

# Research Closed-Loop Skill

Full academic research automation: NotebookLM + Claude Code + Zotero closed loop.

## Installation

```bash
# 1. Clone the full project (includes Python scripts)
git clone https://github.com/wtz328033704/research-closed-loop.git ~/research-closed-loop

# 2. Install dependencies
pip install pyzotero PyMuPDF markitdown chromadb google-genai notebooklm-mcp-cli bibtexparser

# 3. Configure
cp ~/research-closed-loop/config/zotero_config.template.json ~/research-closed-loop/config/zotero_config.json
# Edit the config file with your Zotero paths, API keys, and Gemini key

# 4. Authenticate NotebookLM
nlm login
```

## Slash Commands

| Command | Phase | Action |
|---------|-------|--------|
| `/r [topic]` | All | Start full pipeline |
| `/re` | 0 | Environment check |
| `/rs` | 0 | Credential dashboard |
| `/rl` | 1 | Literature search + Zotero import |
| `/rr` | 2 | Deep reading via NotebookLM |
| `/rg` | 3 | Gap analysis + hypothesis |
| `/rp` | 4 | Interactive planning |
| `/rw` | 5 | Writing with citations |
| `/rv` | 6 | Revision + refinement |

## Workflow Overview

```
Phase 0  🛑 Setup → env check + skill verification + credentials
Phase 1  🛑 Discovery → multi-DB search → Zotero import
Phase 2  🛑 Deep Read → PDF → NotebookLM source-grounded Q&A
Phase 3  🛑 Gap Analysis → contradiction detection → feasibility ranking
Phase 4  🛑 Planning → Socratic dialog → methodology blueprint
Phase 4.5 🛑 Data Upload → (optional) real data/figures → cross-ref
Phase 5  🛑 Writing → auto skill invocation → sentence-level tracing → citations
Phase 6  🛑 Revision → feedback → Zotero sync
```

🛑 = Human-in-the-loop gate. Claude MUST pause and wait for user confirmation.

## Phase 0: Environment Setup

When `/re` or `/rs` is invoked, or at the start of any `/r [topic]`:

### Step 0.1: Check Python environment
```bash
cd ~/research-closed-loop && python scripts/env_setup.py
```

### Step 0.2: Check skills
Verify ARS plugin skills are available by attempting to invoke one.
Verify OpenClaw Medical Skills are installed (check for key skills: scientific-writing, pubmed-search, etc.)

### Step 0.3: Present credential dashboard
Show Zotero API, NotebookLM MCP, Gemini API status.
For each missing credential, guide the user to the correct URL to obtain it.
Save all credentials to `config/zotero_config.json`.

### 🛑 GATE 0: Confirm all systems green before proceeding.

## Phase 1: Literature Discovery

When `/rl [topic]` is invoked:

1. Ask user which databases to search:
   - Auto: PubMed / arXiv / Semantic Scholar / OpenAlex
   - Manual: Embase / Web of Science / Scopus / CNKI / WanFang
2. Execute searches via WebSearch
3. For manual imports: guide user to export .ris/.bib/.csv → parse with `scripts/ref_importer.py`
4. Merge, deduplicate (DOI + title similarity)
5. 🛑 GATE 1: Present ranked results, user selects which to import
6. Import to Zotero via pyzotero API
7. Run `scripts/metadata_indexer.py`

## Phase 2: Deep Reading

When `/rr` is invoked:

1. List existing NotebookLM notebooks: `nlm notebook list`
2. 🛑 GATE 2a: User chooses existing or creates new notebook
3. Upload sources: `nlm source add <notebook-id> --url <url> --wait`
4. 🛑 GATE 2b: User reviews uploaded sources
5. Run systematic Q&A: `nlm query notebook <id> "<question>" --timeout 180`
6. Store all answers in project state

## Phase 3: Gap Analysis

When `/rg` is invoked:

1. Query NotebookLM with gap-focused questions based on Phase 2 findings
2. Build contradiction & gap matrix
3. Score each gap: data availability, method maturity, time, novelty, publication potential
4. 🛑 GATE 3: Present ranked gaps, user selects direction
5. Generate hypotheses (H0/H1) with test strategies

## Phase 4: Planning

When `/rp` is invoked:

1. Initiate Socratic dialog for research design
2. Invoke `academic-research-skills:ars-plan` for chapter-by-chapter planning
3. Invoke `research_architect_agent` (ARS) for methodology blueprint
4. 🛑 GATE 4: User approves research plan
5. 🛑 GATE 4.5: Optional data/figures upload

## Phase 5: Writing

When `/rw` is invoked:

### Writing Type Selection
🛑 Ask user to specify:
- Writing type: Original Article / Systematic Review (PRISMA) / Narrative Review / Case Report
- Target journal (for formatting)
- Real data available? → Evidence-Driven vs Hypothetical mode

### Auto Skill Invocation
Automatically invoke skills (use the Skill tool):

| Step | Skill | What it does |
|------|-------|-------------|
| Outline | `academic-research-skills:ars-outline` | Section structure + evidence map |
| Bib | `academic-research-skills:ars-lit-review` | Annotated bibliography |
| Intro | `scientific-writing` (OpenClaw) | Introduction draft |
| Methods | `academic-research-skills:research_architect_agent` | Methods section |
| Citation | `academic-research-skills:ars-citation-check` | Citation error scan |
| Abstract | `academic-research-skills:ars-abstract` | Bilingual abstract |
| Format | `academic-research-skills:ars-format-convert` | LaTeX/DOCX/PDF output |

### Citation Quality Guard
- Every citation key MUST resolve to a real Zotero item (verify via `scripts/metadata_indexer.py`)
- Every factual claim MUST pass NotebookLM source verification
- NO hallucinated references allowed
- Flag unverifiable claims: 🟡 partial / 🔴 no source

### Review Gates
- 🛑 GATE 5a: Outline approval
- 🛑 GATE 5b: Per-section review (with verification report)
- 🛑 GATE 5c: Final manuscript approval

## Phase 6: Revision

When `/rv` is invoked:

1. User reviews draft, provides feedback
2. Re-verify affected claims via NotebookLM
3. Revise, update citations, sync to Zotero
4. Optionally use `peer-review` (OpenClaw) for simulation
5. 🛑 GATE 6: Approve each revision round

## Hallucination Prevention Protocol

1. Every factual claim must be traceable to a source document in Zotero
2. NotebookLM answers are source-grounded by design (only uploaded sources used)
3. During writing, every sentence with a factual claim runs through source verification
4. Unverifiable claims are flagged and NEVER included in final output
5. Zotero is the single source of truth for all citation metadata

## Environment Reference

| Component | How to check |
|-----------|-------------|
| Zotero API | `python -c "from pyzotero import zotero; zotero.Zotero(library_id, 'user', api_key).top(limit=1)"` |
| NotebookLM MCP | `nlm --version && nlm notebook list` |
| Gemini API | `python -c "from google import genai; genai.Client(api_key='...').models.list()"` |
| Python packages | `python scripts/env_setup.py` |
| ARS plugin | `Skill("academic-research-skills:ars-outline")` |
| OpenClaw skills | Check `.claude_skills/` directory for target skills |
