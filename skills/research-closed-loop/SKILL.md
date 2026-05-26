---
name: research-closed-loop
description: Complete academic research automation closed loop. Input a research topic → automatic literature search → Zotero import → PDF full-text extraction → NotebookLM source-grounded Q&A → research gap identification → hypothesis generation → interactive planning → hallucination-free writing with citations → Zotero sync. Integrates NotebookLM + Claude Code + Zotero + ARS + OpenClaw Medical Skills.
metadata:
  type: workflow
  tags: [research, automation, closed-loop, literature, writing, citation, zotero, notebooklm]
  dependencies:
    - zotero-lit-index
    - notebooklm-qa
    - lit-search
    - gap-finder
    - citation-writer
    - academic-research-skills (ARS plugin)
    - OpenClaw Medical Skills
---

# Research Closed-Loop Workflow

## Purpose
A universal, hallucination-free academic automation system. The user inputs a research topic direction — Claude orchestrates the complete research pipeline: literature discovery → source-grounded reading → gap analysis → hypothesis formulation → interactive planning → writing with verified citations → Zotero synchronization. Powered by the three-engine architecture: **NotebookLM** (source grounding) + **Claude Code** (orchestration) + **Zotero** (reference truth source).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH CLOSED LOOP                         │
│                                                                 │
│  User: "I want to research [TOPIC]"                            │
│       │                                                        │
│       ↓                                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 0: Preparation & Credential Setup                  │  │
│  │   Check Zotero → nlm login → Gemini key → all green      │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 1: Literature Discovery & Import                   │  │
│  │   lit-search → Zotero import → zotero-lit-index          │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 2: Deep Reading & Understanding                    │  │
│  │   pdf_extractor → NotebookLM upload → source-grounded QA │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 3: Gap Analysis & Hypothesis                       │  │
│  │   synthesis_agent → gap-finder → hypothesis-generation   │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 4: Interactive Planning                            │  │
│  │   ars-plan (Socratic dialog) → research_architect_agent  │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 4.5: Data & Figure Upload (Optional)               │  │
│  │   🛑 Upload real data/figures → analyze → cross-ref lit  │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 5: Writing with Citations                          │  │
│  │   ars-outline → annotated bib → draft → source tracing   │  │
│  │   → citation insertion → ars-citation-check → format     │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               ↓                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PHASE 6: Revision & Refinement                           │  │
│  │   ars-revision → peer-review → Zotero sync               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                │
│                               ↓                                │
│  Output: Research plan + Draft manuscript + Zotero collection │
└─────────────────────────────────────────────────────────────────┘
```

## Trigger

This workflow is triggered when the user:
- Provides a research topic / direction (e.g., "I want to explore X in the context of Y")
- Asks to "start a research project on [TOPIC]"
- Says "help me find a research gap in [FIELD]"
- Invokes any phase-specific command

## Human-in-the-Loop Gates (CRITICAL)

**Every phase MUST pause and wait for user confirmation before proceeding to the next phase.** No automatic pass-through. Each gate is marked with 🛑.

```
Phase 0 ──🛑[user inputs credentials + confirms all systems green]──→ Phase 1
Phase 1 ──🛑[user selects papers]──→ Phase 2
Phase 2 ──🛑[user picks notebook + reviews sources]──→ Phase 3
Phase 3 ──🛑[user selects gap]──→ Phase 4
Phase 4 ──🛑[user approves plan]──→ Phase 4.5
Phase 4.5 ──🛑[user uploads data OR skips]──→ Phase 5
Phase 5 ──🛑[user reviews each section]──→ Phase 6
Phase 6 ──🛑[user approves final version]──→ Done
```

## Phase-by-Phase Execution

### PHASE 0: Preparation & Credential Setup

**Goal**: Ensure all three engines (Zotero, NotebookLM, Gemini) are connected before any research begins. Let the user input missing credentials interactively.

This phase runs automatically when the workflow is triggered. It checks each component, prompts for missing credentials, saves them to config, and verifies — only proceeding to Phase 1 when everything is green.

#### Step 0.1: Auto-detect current state

```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python scripts/env_setup.py
```

Parse the output to check: Zotero SQLite, Zotero API key + library ID, NotebookLM MCP install + auth, Gemini API key, Google account identity, Python packages.

#### Step 0.2: Present credential dashboard

```
╔══════════════════════════════════════════════════════════╗
║              RESEARCH CLOSED-LOOP · SETUP                ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Zotero                                                  ║
║    Local SQLite:  ✅ Found (X items) / ⚠️ Not found      ║
║    API Key:       ✅ Configured (XXXX...) / ⚠️ Missing   ║
║    Library ID:    ✅ XXXXXXXX / ⚠️ Missing               ║
║                                                          ║
║  NotebookLM MCP                                          ║
║    nlm CLI:       ✅ vX.X.X installed / ⚠️ Not installed ║
║    Google Login:  ✅ you@gmail.com / ⚠️ Not authenticated ║
║                                                          ║
║  Gemini API (fallback)                                   ║
║    API Key:       ✅ Configured / ⚠️ Missing              ║
║    Model:         gemini-2.5-pro / gemini-2.5-flash       ║
║                                                          ║
║  Python Packages                                         ║
║    pyzotero / fitz / markitdown / chromadb: ✅ / ⚠️       ║
║    google-genai:  ✅ OK / ⚠️ Missing                      ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  Overall: ✅ ALL CLEAR / ⚠️ [N] issues to fix            ║
╚══════════════════════════════════════════════════════════╝
```

#### Step 0.3: Interactive fix for each missing component

For each ⚠️ item, present the fix option in order. NEVER skip a critical component without user consent.

**If Zotero API Key is missing:**
```
⚠️ Zotero API Key not configured.

Get one at: https://www.zotero.org/settings/keys
  → "Create New Private Key"
  → Check "Allow library access" and "Allow notes access"

Paste your Zotero API Key here (or type SKIP to use local SQLite only):
```
On input: save to `config/zotero_config.json` → re-verify.

**If Zotero Library ID is missing:**
```
⚠️ Zotero Library ID not configured.

Find it at: https://www.zotero.org/settings/keys
Look for "Your userID for use in API calls".

Paste your Zotero User ID here (or type SKIP):
```
On input: save to config → re-verify.

**If nlm CLI is not installed:**
```
⚠️ NotebookLM MCP CLI not installed.

Run: pip install notebooklm-mcp-cli
After installation, tell me "done" and I'll continue the check.
```
Wait for confirmation, then re-check.

**If nlm is not authenticated:**
```
⚠️ NotebookLM not connected to your Google account.

Running 'nlm login' — it will open your browser.
Log in with the Google account that has NotebookLM access.

Which Google account should I use?
  (If you have multiple, tell me which one to log into)
```
Run `nlm login`. Wait for completion. Show the logged-in account and re-verify.
```
✅ Logged in as: you@gmail.com
```

**If Gemini API Key is missing:**
```
⚠️ Gemini API Key (fallback channel) not configured.

Get your key at: https://aistudio.google.com/apikey
(Free, included with your Google account — same login as NotebookLM)

Paste your Gemini API Key here (or type SKIP to rely on NotebookLM MCP only):
```
On input: save to config → re-verify.

**If Python packages are missing:**
```
⚠️ Missing: [package names]

Installing now: pip install [packages]
```
Run install, re-verify.

#### Step 0.4: Skill availability check

After credentials are configured, verify ALL skills that the writing phase will need.

**Check ARS plugin skills**:
```
Try: Skill("academic-research-skills:ars-outline")
→ If launches successfully: ✅ ARS plugin available
→ If fails: ⚠️ ARS plugin may need reinstallation
```

List the 8 ARS skills to verify:
- `ars-outline` — outline + evidence map
- `ars-lit-review` — annotated bibliography
- `ars-plan` — Socratic planning (Phase 4)
- `ars-citation-check` — citation error scan
- `ars-abstract` — bilingual abstract
- `ars-format-convert` — LaTeX/DOCX/PDF output
- `ars-revision` — revised draft
- `ars-revision-coach` — reviewer response

**Check writing-related OpenClaw skills**:
```
List the most important ones:
  scientific-writing, scientific-manuscript, literature-review,
  peer-review, hypothesis-generation, scientific-critical-thinking,
  scientific-problem-selection, knowledge-synthesis, citation-management

→ Count how many of the 9 are found in OpenClaw skills directory
→ Report: ✅ [N]/9 OpenClaw writing skills available
```

**Check Python environment**:
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python scripts/env_setup.py
```

#### Step 0.5: Final dashboard + Skill report

```
╔══════════════════════════════════════════════════════════╗
║              ✅ ALL SYSTEMS READY                         ║
║                                                          ║
║  Primary channel:   NotebookLM MCP (you@gmail.com)       ║
║  Fallback channel:  Gemini API (configured)              ║
║  Zotero:            API connected + Local SQLite OK      ║
║                                                          ║
║  ARS Plugin:    ✅ [N/8] skills verified                 ║
║  OpenClaw:      ✅ [N/9] writing skills found            ║
║  Python Env:    ✅ all packages OK                       ║
║                                                          ║
║  Writing modes supported:                                ║
║    📝 Original Article (IMRaD)                          ║
║    📚 Systematic Review (PRISMA 2020)                   ║
║    📖 Narrative Review                                 ║
║    📊 Meta-Analysis (if applicable)                     ║
║    📋 Case Report (CARE)                                ║
║    🔬 Protocol/Methods Paper                            ║
║                                                          ║
║  Ready to start research.                                ║
╚══════════════════════════════════════════════════════════╝
```

#### 🛑 GATE 0: Confirmation to proceed

If any CRITICAL component is still missing (Zotero API + at least one of NotebookLM/Gemini), DO NOT proceed. Mark the workflow as blocked and tell the user what's needed.

Non-critical warnings can be SKIPped — the workflow degrades gracefully.

```
Your options:
  A) All green — start Phase 1 (tell me your research topic!)
  B) Fix remaining issues (tell me which to address)
  C) Skip non-critical warnings and proceed
  D) Save config and exit (resume later)

Which would you like?
```
**DO NOT proceed until user responds.**

**Output**: Fully configured environment, all credentials in `config/zotero_config.json`, authenticated sessions active, skills verified, ready for research.

---

### PHASE 1: Literature Discovery & Import

**Goal**: Build a comprehensive, curated literature base by combining automated multi-source search with user-provided exports from proprietary databases (Embase, Web of Science, Scopus, etc.).

#### Step 1.1: Database Source Selection

Parse the user's topic into structured search queries, then present source options:

```
Before I start searching, let's decide which databases to cover.

=== Automated Search (I handle these) ===
  A) PubMed — biomedical, free, good coverage
  B) arXiv / bioRxiv / medRxiv — preprints, cutting-edge
  C) Semantic Scholar — cross-disciplinary, citation graph
  D) OpenAlex — open catalog, good for CS/engineering
  E) All of the above (recommended)

=== Manual Import (you export from these, I parse the file) ===
  F) Embase — export as .ris / .bib / .txt
  G) Web of Science — export as .ris / .bib / .txt
  H) Scopus — export as .ris / .bib / .csv
  I) Cochrane Library — export as .ris / .txt
  J) CNKI (中国知网) — export as .txt (EndNote format)
  K) WanFang (万方) — export as .txt
  L) Other database (tell me which, I'll guide you on export format)

Which automated sources? (A/B/C/D/E)
Any manual imports to add? (F/G/H/I/J/K/L, or NONE)
```
**DO NOT proceed until user responds with choices.**

#### Step 1.2: Automated Search

Execute selected automated sources in parallel using `lit-search` skill.

#### Step 1.3: Manual Import (if user chose any of F-L)

For each database the user selected:

```
=== Import from [Database Name] ===

Export instructions:
  1. Go to [database URL] and run your search
  2. Select the papers you want to include
  3. Export as: [recommended format, e.g., "RIS format (.ris)" or "BibTeX (.bib)"]
     [Database-specific instructions:
       - Embase: ☰ → Export → RIS format → select fields: Author, Title, Year, DOI, Abstract
       - Web of Science: Export → RIS → select "Full Record and Cited References"
       - Scopus: Export → RIS → select all citation fields
       - CNKI: 导出 → EndNote → 全选字段
       - ...]

  4. Save the exported file
  5. Drag & drop the file here, or paste the file path

File path (or drag here):
```
After receiving the file:
- Parse .ris / .bib / .csv / .txt with `bibliography_agent` or manual parsing
- Extract: title, authors, year, DOI, abstract, journal
- Normalize to the same format as automated results

```
✅ Parsed [N] references from [database name]:
  1. [Title] ([Year]) — [DOI or "no DOI"]
  2. ...
  
Any issues with the parsing? (missing DOIs, garbled characters, wrong encoding)
  A) Looks good — continue
  B) Fix specific entries (tell me which numbers)
```

#### Step 1.4: Merge, Deduplicate & Rank

Combine automated search results + manually imported references into a unified list.

Deduplication priority:
1. By DOI (exact match) → automatic merge
2. By title similarity (>90%) → flag for user review
3. Manual check: show suspected duplicates side-by-side

Final ranking: relevance × citation count × recency.

#### 🛑 GATE 1: Final Paper Selection (MUST pause here)

```
=== Complete Literature Pool ===

Automated search: [N] papers from [sources used]
Manual imports:   [M] papers from [databases used]
After dedup:      [X] unique papers total
Duplicates found & merged: [Y]

=== Top 15 by relevance ===
  1. [Title] ([Year]) — [1-line relevance] — DOI: [xxx] — Cited: [N] — Source: [PubMed / Embase / WoS / ...]
  2. [Title] ([Year]) — [1-line relevance] — DOI: [xxx] — Cited: [N] — Source: [...]
  ...

=== Your options ===
  A) Import ALL [X] papers to Zotero
  B) Import top [N] papers only (tell me how many)
  C) Select specific papers (tell me which numbers)
  D) Show me abstracts of specific papers first
  E) Refine — add more from another database or re-run with adjusted keywords
  F) Remove some papers (tell me which numbers to exclude)

Which would you like?
```
**DO NOT proceed until user responds with a choice.**

5. After user selection, import chosen papers to Zotero:
   - Create collection: `[TOPIC] Literature`
   - Auto-import with metadata + PDF attachments via pyzotero
   - Tag each paper with its source database for traceability
6. Run `zotero-lit-index` to build/update metadata index
7. Run PDF extraction for imported papers
8. Confirm to user:
   ```
   ✅ Phase 1 Complete
   Imported: [X] papers → Zotero collection "[TOPIC] Literature"
   Sources:  PubMed [N] | arXiv [N] | Embase [N] | WoS [N] | ...
   PDFs extracted: [Y]/[X]
   Ready for Phase 2: Deep Reading.
   ```

**Output**: Curated Zotero collection with full-text extracted and indexed, traceable to original databases.

---

### PHASE 2: Deep Reading & Understanding

**Goal**: Achieve a thorough, source-grounded understanding of the literature using real NotebookLM.

#### 🛑 GATE 2a: Notebook Selection (MUST pause here)
List existing NotebookLM notebooks AND the option to create new:

```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python -c "
from scripts.notebooklm_bridge import NotebookLMBridge
b = NotebookLMBridge()
r = b._run_nlm('notebook', 'list', timeout=30)
import json
nbs = json.loads(r.stdout)
for nb in nbs:
    print(f'  [{nb[\"id\"][:8]}...] {nb[\"title\"]} ({nb[\"source_count\"]} sources)')
"
```

Present to user:
```
Your NotebookLM notebooks:

Existing notebooks that may be relevant:
  1. "[Notebook Title]" (X sources, updated YYYY-MM-DD)
  2. "[Notebook Title]" (X sources, updated YYYY-MM-DD)
  ...

Your options:
  A) Create a NEW notebook: "Research-[topic]"
  B) Use existing notebook #N (specify which)
  C) Create new AND merge with existing #N

Which would you like?
```
**DO NOT proceed until user responds.**

#### 🛑 GATE 2b: Source Review (MUST pause here)
After uploading sources to the chosen notebook:

```
Uploaded [X] PDFs to notebook "[notebook name]":
  1. [Title] — [page count] pages — [citation key]
  2. [Title] — [page count] pages — [citation key]
  ...

Total sources in notebook: [X+existing]

Before I start Q&A, do you want to:
  A) Proceed — run systematic Q&A on all sources
  B) Remove some sources first (tell me which numbers)
  C) Add more sources (search for additional papers)
  D) Ask a specific question first instead of systematic Q&A

Your choice?
```
**DO NOT proceed until user responds.**

4. After user approval, run systematic source-grounded Q&A:
   - "Summarize the key findings across all papers."
   - "What methods are most commonly used? What are their limitations?"
   - "What theoretical frameworks are cited?"
   - "What datasets are used? Are they publicly available?"
   - "What future work do the authors suggest?"
5. Store all answers in project state for gap analysis

**Output**: Comprehensive, source-grounded understanding of the literature landscape.

---

### PHASE 3: Gap Analysis & Hypothesis Generation

**Goal**: Identify feasible, high-impact research gaps and formulate testable hypotheses.

**Actions**:
1. Execute `gap-finder` skill:
   - Cross-source synthesis via ARS `synthesis_agent`
   - Build contradiction & gap matrix
   - Feasibility scoring (5 dimensions: data availability, method maturity, time, novelty, publication potential)

#### 🛑 GATE 3: Gap Selection (MUST pause here)
```
Top Research Gaps (ranked by feasibility × impact):

1. [Gap Title] (Score: 8.2/10)
   - Type: [Contradiction / Replication / Methodology / Population / Cross-domain]
   - What's missing: [detailed description]
   - Why it matters: [significance to field]
   - Suggested method: [approach]
   - Estimated time: [X months]
   - Main risk: [challenge]
   - Key papers to cite: [3-5 citation keys]

2. [Gap Title] (Score: 7.5/10)
   ...

3. [Gap Title] (Score: 6.9/10)
   ...

Your options:
  A) Pursue gap #1 (top recommendation)
  B) Pursue gap #N (tell me which)
  C) Combine gaps #X and #Y (explain your thinking)
  D) Show me more gaps (beyond top 3)
  E) I have my own gap idea (describe it)

Which would you like?
```
**DO NOT proceed until user responds.**

3. For the selected gap, use `hypothesis-generation` to formulate and present:
   - H0 / H1
   - Test strategy with specific methods
   - Expected effect size / sample size estimate
   - Potential confounding factors

4. Ask user: "Do these hypotheses capture your research intent? Any refinements?"

**Output**: Selected research gap + testable hypothesis + method approach.

---

### PHASE 4: Interactive Planning

**Goal**: Co-design a rigorous research plan through Socratic dialog.

**Actions**:
1. Initiate `ars-plan` (Socratic chapter-by-chapter planning):
   - Chapter 1: Problem statement & significance
   - Chapter 2: Literature review scope
   - Chapter 3: Methodology blueprint (use `research_architect_agent`)
   - Chapter 4: Expected results & validation strategy

2. For each chapter, ask clarifying questions:
   - "The method assumes [X]. Do you have access to [required resource]?"
   - "What would be the minimal publishable unit for this project?"
   - "What's your timeline? Conference deadline / thesis submission?"

#### 🛑 GATE 4: Plan Approval (MUST pause here)
```
Research Plan Summary:

  Research Question: [...]
  Hypothesis: H0=[...], H1=[...]
  Method: [summary]
  Data Requirements: [...]
  Timeline: [X months]
  Expected Contributions:
    1. [...]
    2. [...]
  Key Risks:
    1. [...] — Mitigation: [...]

Your options:
  A) Approve — proceed to writing
  B) Revise a specific part (tell me which)
  C) Save plan and pause (resume later)

Which would you like?
```
**DO NOT proceed until user responds.**

3. Save finalized research plan to project state

**Output**: User-approved research plan with timeline and resource requirements.

---

### PHASE 4.5: Data & Figure Upload (Optional but Recommended)

**Goal**: If the user has real experimental data, figures, tables, or results, upload them now. This transforms the writing from "hypothetical/planned" to "evidence-driven" — the subsequent draft will describe and interpret actual findings instead of placeholder language.

#### 🛑 GATE 4.5: Data Availability Check (MUST pause here)

```
Before we start writing, I need to know:

Do you have any of the following to upload?

  A) Experimental data (CSV, Excel, SPSS, etc.)
  B) Figures / charts (PNG, PDF, SVG, etc.)
  C) Tables (Excel, CSV, Word, etc.)
  D) Images / microscopy / radiology (PNG, DICOM, etc.)
  E) Preliminary results / notes (text, Markdown, Word, etc.)
  F) Combination of the above
  G) None yet — write based on the research plan (hypothetical draft)

What do you have?
```
**DO NOT proceed until user responds.**

#### If user uploads data (options A-F):

1. **Ingest and analyze the data:**
   - For tabular data (CSV/Excel): run descriptive statistics, identify key patterns
   - For figures/charts: extract visual patterns, read axis labels and legends
   - For images: describe key features visible in the image
   - Use `xlsx` skill (OpenClaw) for spreadsheets, `pdf` for PDF figures, `image-analysis` for biomedical images

2. **Cross-reference with literature via NotebookLM:**
   - "Given the uploaded data showing [key finding], how does this compare with the existing literature?"
   - "Do any of the uploaded papers report similar or conflicting results?"
   - "What theoretical mechanism from the literature explains the observed pattern?"

3. **Structure the findings for writing:**
   ```
   Data Summary:
   
   Key Finding 1: [description from real data]
     - Supporting literature: [cite:key1], [cite:key2]
     - Contradicting literature: [cite:key3]
   
   Key Finding 2: [description from real data]
     - Supporting literature: [cite:key4]
   
   Figures to include:
     - Fig 1: [description] — shows [pattern] — compare with [cite:key5 Fig.3]
     - Fig 2: [description]
   
   Tables to include:
     - Table 1: [summary statistics]
   ```
4. **Show the data interpretation to user for confirmation:**
   ```
   Here's what I found from your data:
   
   Key Finding 1: [interpretation]
     Literature alignment: [consistent with / extends / contradicts] [Author, Year]
     Suggested figure: [description]
     Suggested table: [description]
   
   Does this interpretation match your understanding?
     A) Yes — incorporate into writing
     B) Partially — let me correct (explain)
     C) No — let me re-analyze (describe what to look for)
   ```

5. After user confirms the data interpretation, store it in project state and pass to Phase 5.

#### If user has no data yet (option G):
- Write the draft in **hypothetical/future-tense style**:
  - Method: "We will recruit N participants..." (future tense, planned)
  - Results: "We expect to observe..." (placeholder figures/tables marked `[Figure 1 placeholder]`)
  - Discussion: "If results confirm H1, this would suggest..." (conditional)
- Mark all result-related sections with `⚠️ NEEDS REAL DATA` for easy identification later
- User can upload data later and re-run Phase 5-6 to replace placeholders

**Output**: 
- If data uploaded: structured data interpretation + literature cross-reference, ready for evidence-driven writing
- If no data: hypothetical draft template with placeholder markers

---

### PHASE 5: Writing with Citations

**Goal**: Produce a draft manuscript where every claim is source-grounded and properly cited. If real data was uploaded in Phase 4.5, the Results describe actual findings. If not, the draft uses hypothetical/planned language.

**Actions**:

#### 🛑 GATE 5d: Writing Type Selection (MUST pause here BEFORE outline)
```
Before I generate the outline, confirm the writing type:

  Your research plan is for a [prospective cohort study / systematic review / etc.]
  Your target journal is: [journal name]

  Writing type:
    A) Original Article (IMRaD) — confirmed
    B) Systematic Review (PRISMA 2020)
    C) Narrative Review
    D) Meta-Analysis
    E) Case Report (CARE guidelines)
    F) Protocol/Methods Paper
    G) Other: [describe]

  If Original Article and no real data yet (Phase 4.5 skipped):
    → Introduction + Methods: written as complete, real sections
    → Results: written as [TEMPLATE with expected analysis placeholder tables/figures]
    → Discussion: written as conditional ("If findings confirm H1...")

  Citation quality rule:
    ℹ️ Every reference must be from Phase 1 (actually retrieved and verified)
    ℹ️ Every claim must be traceable to a real paper in the Zotero library
    🔴 NO fabricated or hallucinated references allowed
```
**DO NOT proceed until user responds.**

1. **Invoke `academic-research-skills:ars-outline`** for detailed outline + evidence map.
   Pass: [research_topic] + [target_journal] + [writing_type] + [key_papers_from_Phase1]
   Wait for the skill to produce the full outline, then present to user.

#### 🛑 GATE 5a: Outline Approval (MUST pause here)
```
Proposed manuscript outline:

1. Introduction
   - [Key points with planned citations from Zotero]
2. Methods
   - Study Design: [...]
   - Participants: [...]
   - Equipment & Protocol: [...]
   - Statistical Analysis: [...]
3. Results (TEMPLATE — real data pending)
   - [Table 1 placeholder: demographic characteristics]
   - [Table 2 placeholder: device metrics comparison]
   - [Figure 1 placeholder: ML model AUC]
4. Discussion
   - [Key comparison points with literature]
   - [Limitations]
   - [Clinical implications]

Citation map: [N] unique Zotero references planned

Your options:
  A) Approve outline — draft all sections
  B) Draft only one section (tell me which)
  C) Revise outline (tell me what to change)
```
**DO NOT proceed until user responds.**

2. **Invoke `academic-research-skills:ars-lit-review`** for annotated bibliography of key papers.

3. **Draft each section by invoking the relevant skill**:
   - Introduction → `academic-research-skills:ars-outline` (evidence map mode) or `scientific-writing` (OpenClaw)
   - Methods → `academic-research-skills:research_architect_agent` (uses Phase 4 plan)
   - Literature context within Discussion → `literature-review` or `scientific-writing` (OpenClaw)

4. **Citation quality guard (run after each section)**:
   - Every citation key must resolve to a real Zotero item with DOI/PMID
   - Use `metadata_indexer.py` to verify: `python scripts/metadata_indexer.py` → `idx.lookup_by_citekey("key")`
   - If any citation fails lookup → flag it 🔴, do NOT include
   - If unsure about a factual claim → verify via `notebooklm-qa` (source-grounded check)

#### 🛑 GATE 5b: Section Review (MUST pause after EACH section)
After drafting each section:

```
=== [Section Name] — Draft ===

[section text with {cite:key} placeholders]

Verification Report:
  ✅ Verified claims: [N] — source found in uploaded PDFs
  🟡 Partial support: [M] — topic mentioned but exact claim needs checking
  🔴 No source found: [K] — these need your review

Your options:
  A) Approve this section — move to next
  B) Revise (tell me what to change)
  C) Show me the source passages for 🟡 claims
  D) Remove 🔴 claims and continue
```
**DO NOT proceed until user responds for EACH section.**

3. After all sections approved, run `ars-citation-check` for error scanning
4. Generate bilingual abstract (`ars-abstract`)

#### 🛑 GATE 5c: Final Draft Approval (MUST pause here)
5. Present the complete manuscript with verification stats before format conversion.
6. Convert to target format (`ars-format-convert`) only after user approval.
7. Sync all citations back to Zotero

**Output**: Draft manuscript with verified citations + formatted output files.

---

### PHASE 6: Revision & Refinement

**Goal**: Iteratively improve the manuscript based on feedback.

**Actions**:
1. User reviews draft, provides comments

#### 🛑 GATE 6: Revision Approval (MUST pause after EACH revision round)
```
Revision Round [N]:

Changes made:
  1. [Change description] — affected citations: [keys]
  2. [Change description] — affected citations: [keys]

Re-verification: [X]/[Y] claims still verified.

Your options:
  A) Accept all changes
  B) Revert change #N
  C) Make additional changes (describe)
  D) Finalize — this draft is ready

Which would you like?
```
**DO NOT proceed until user responds.**

2. For each revision, re-verify affected claims against sources
3. Zotero sync after each revision cycle
4. Use `peer-review` (OpenClaw) for pre-submission simulation if user desires
5. If handling real reviewer comments: use `ars-revision-coach` → `ars-revision`

**Output**: Polished manuscript ready for submission.

## Quick Commands

Users can jump to any phase directly:

| Command | Phase | Action |
|---------|-------|--------|
| `/research search [topic]` | 1 | Literature search + import |
| `/research read` | 2 | Deep reading + Q&A |
| `/research gap` | 3 | Gap analysis |
| `/research plan` | 4 | Interactive planning |
| `/research write` | 5 | Writing + citations |
| `/research revise` | 6 | Revision loop |
| `/research full [topic]` | 1→6 | Complete pipeline |

## Project State Management

Each research project maintains a state file at `data/projects/{project_name}/state.json`:
```json
{
  "project_name": "...",
  "topic": "...",
  "created_at": "...",
  "phases_completed": [1, 2],
  "current_phase": 3,
  "zotero_collection": "...",
  "notebooklm_notebook": "...",
  "search_results": { "...": "..." },
  "selected_papers": ["key1", "key2"],
  "gap_analysis": { "...": "..." },
  "selected_gap": { "...": "..." },
  "research_plan": { "...": "..." },
  "draft_sections": { "...": "..." },
  "citation_verification": { "verified": 45, "partial": 3, "none": 0 }
}
```

This enables:
- Resuming work across sessions (Claude reads state.json on startup)
- Auditing: every claim → source mapping is recorded
- Reproducibility: the full research trail is preserved

## Hallucination Prevention Protocol

This is the core invariant of the entire system:

1. **Every factual claim MUST be traceable to a source document in Zotero**
2. **NotebookLM/Gemini answers are source-grounded by design** — they only use uploaded sources
3. **During writing, every sentence with a factual claim runs through source verification**
4. **Unverifiable claims are NEVER included in the final output** — they are flagged for user review
5. **Zotero is the single source of truth** — all citation metadata comes from Zotero, nowhere else

If source grounding is unavailable (no MCP, no Gemini API key), Claude MUST:
- Only make claims that are directly visible in the extracted text
- Cite specific papers by [Author, Year] and note the limitation
- Explicitly tell the user: "Source grounding is not active. Claims below are based on my training data, not your literature. Please verify."

## Environment Setup Summary

```bash
# Python packages
pip install pyzotero PyMuPDF markitdown chromadb google-genai

# Node.js (NotebookLM MCP)
pip install notebooklm-mcp-cli

# Zotero
# - Install Zotero + Better BibTeX plugin
# - Generate API key: https://www.zotero.org/settings/keys
# - Add to config/zotero_config.json

# Gemini API (fallback)
# - Get key: https://aistudio.google.com/apikey
# - Add to config/zotero_config.json or set GEMINI_API_KEY env var

# Verify
cd "D:\AI-tool\Project\Smart_Brace_Project"
python scripts/zotero_connector.py
python scripts/notebooklm_bridge.py
python scripts/metadata_indexer.py
```
