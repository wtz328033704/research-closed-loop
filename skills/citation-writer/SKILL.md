---
name: citation-writer
description: Hallucination-free academic writing with automated citation insertion, sentence-level source tracing, and Zotero sync. Powered by ARS writing pipeline + NotebookLM source grounding.
metadata:
  type: skill
  tags: [writing, citation, manuscript, zotero, hallucination-prevention]
---

# Citation-Aware Academic Writer

## Purpose
Generate academic text where every factual claim is traceable to a source in the user's Zotero library. Automatically inserts citation keys, detects unsupported claims, and formats output in the target citation style. Two writing modes: **Review Mode** (literature-only, top-journal review standard) and **Data-Driven Mode** (with real experimental data, customized to target journal).

## Core Principle: Zero Hallucination
```
Claim → NotebookLM/Gemini source check → Source found?
  ├─ YES → Insert {cite:zotero_key} → Verified ✓
  └─ NO  → Flag as 🟡 "needs verification" → User must approve or remove
```

## When to Use
- Drafting a literature review / introduction / discussion section
- Writing with proper academic citations
- Verifying that a manuscript's claims are all source-grounded
- Writing a high-quality review paper for top journals (Review Mode)
- Writing a data-driven original research paper targeted at a specific journal (Data-Driven Mode)

## Skill Invocation Protocol (CRITICAL)

**During Phase 5 writing, you MUST actually invoke (not just describe) the following skills using the Skill tool:**

| Step | Skill to Call | Arguments |
|------|--------------|-----------|
| Outline | `academic-research-skills:ars-outline` | topic + journal + structure type |
| Annotated Bib | `academic-research-skills:ars-lit-review` | paper list + citation style |
| Introduction | `academic-research-skills:ars-outline` (evidence map) or `scientific-writing` | gap + lit context |
| Literature Review | `scientific-writing` or `literature-review` (OpenClaw) | thematic synthesis |
| Methods | `academic-research-skills:research_architect_agent` | study design + equipment |
| Citation Check | `academic-research-skills:ars-citation-check` | draft text |
| Format Output | `academic-research-skills:ars-format-convert` | target format |
| Abstract | `academic-research-skills:ars-abstract` | paper + language pair |

**For each claim in the draft:**
- Must be traceable to a Zotero item with real DOI/PMID
- ℹ️ Every citation must reference a paper that was actually retrieved in Phase 1 and uploaded to NotebookLM in Phase 2
- 🔴 No hallucinated references — if unsure, verify via `notebooklm-qa`
- Generating a formatted paper (LaTeX / DOCX / PDF) with citations from Zotero

## Writing Pipeline

```
Research Plan (from gap-finder)
       │
       ↓
[1] Outline + Evidence Map (ars-outline)
       │
       ↓
[2] Annotated Bibliography (ars-lit-review)
       │
       ↓
[3] Section Drafting (report_compiler_agent / scientific-writing)
       │
       ↓
[4] Sentence-Level Source Tracing (notebooklm-qa)
       │
       ↓
[5] Citation Key Insertion + Zotero Sync
       │
       ↓
[6] Citation Error Check (ars-citation-check)
       │
       ↓
[7] Format Output (ars-format-convert)
       │
       ↓
[8] Bilingual Abstract (ars-abstract)
```

## Workflow Steps

### Step 0: Determine Writing Mode & Journal Target

🛑 **MUST pause here to let user choose writing mode and journal target.**

Check project state for uploaded data from Phase 4.5. Then present:

```
Writing Configuration:

Mode: [auto-detected from Phase 4.5 data status]

  A) REVIEW MODE (no real data — literature synthesis only)
     → Written as a high-quality systematic/narrative review
     → Suitable for top-tier review journals or thesis chapters
     → Follows PRISMA 2020 checklist (if systematic review)
     → Target journals: [list relevant top review journals in the field]

  B) DATA-DRIVEN MODE (real experimental data uploaded)
     → Written as an original research article
     → Structure follows target journal's author guidelines
     → Real figures, tables, and statistical results included

Which mode? (A/B)

If DATA-DRIVEN, also specify:
  Target journal: [name] (e.g., Nature Communications, JBJS, AJSM, The Lancet, ...)
  OR
  Experiment type: [RCT / cohort study / case-control / in vitro / animal model / ...]
  OR
  I'll let you suggest the best fit based on my data and field.
```

#### MODE A: REVIEW MODE (Literature-Only)

When user has no real data — only literature from Phase 1:

**Quality Standards:**
- Follow the structure and depth of reviews published in top-tier journals:
  - Clinical: *The Lancet*, *BMJ*, *JAMA*, *NEJM*
  - Orthopedic/Sports Med: *AJSM*, *JBJS*, *BJJ*, *KSSTA*
  - Basic Science: *Nature Reviews X*, *Physiological Reviews*
  - General: *Annual Review of X*, *Trends in X*
- If systematic review: follow **PRISMA 2020** guidelines (27-item checklist + flow diagram)
- If narrative review: follow journal-specific author guidelines for review articles
- If scoping review: follow **PRISMA-ScR** guidelines

**Structure (Systematic Review):**
```
1. Abstract (structured: Background, Methods, Results, Conclusions)
2. Introduction (burden of disease, knowledge gap, review rationale)
3. Methods
   3.1 Search strategy (databases, date range, complete search strings)
   3.2 Eligibility criteria (PICOS framework)
   3.3 Study selection & data extraction (PRISMA flow diagram)
   3.4 Quality assessment (ROB-2 for RCTs, NOS for cohorts, QUADAS-2 for diagnostic)
   3.5 Data synthesis (meta-analysis methods if applicable, GRADE evidence grading)
4. Results
   4.1 Study selection (flow diagram)
   4.2 Study characteristics (evidence table)
   4.3 Quality assessment results
   4.4 Synthesis of findings (thematic organization, NOT paper-by-paper)
   4.5 Meta-analysis results (forest plots, heterogeneity, publication bias)
5. Discussion
   5.1 Summary of evidence (GRADE summary of findings table)
   5.2 Comparison with other reviews
   5.3 Strengths and limitations
   5.4 Clinical implications
   5.5 Future research directions
6. Conclusions
7. References (Zotero-generated, target journal style)
```

**Tone & Language:**
- Authoritative, critical synthesis — not a summary
- Use "The evidence suggests..." not "This paper found..."
- Compare/contrast: "While X et al. reported [finding], Y et al. found [conflicting finding], possibly due to [methodological difference]"
- Every paragraph synthesizes ≥3 sources
- GRADE evidence quality qualifiers: "high-quality evidence," "moderate certainty," "low-quality evidence"
- Avoid: "more research is needed" → instead: "Specifically, a randomized trial comparing X vs Y in population Z is warranted"

#### MODE B: DATA-DRIVEN MODE (With Real Experimental Data)

When user uploaded real data in Phase 4.5:

**Step B.1: Gather journal/format requirements**

🛑 **MUST ask user:**
```
To format your paper correctly, I need to know:

  1. Target journal: [name]
     OR
     Experiment type: [RCT / cohort / case-control / case series / 
                      in vitro / in vivo animal / computational / 
                      qualitative / mixed-methods]
     OR
     Let me suggest based on your data and field.

  2. Any specific formatting requirements?
     (word limit, abstract structure, figure limits, etc.)

  3. Preferred citation style:
     A) Same as target journal (I'll look it up)
     B) Specific style: [APA / Vancouver / Nature / Harvard / GB7714 / ...]
```

**Step B.2: Look up journal guidelines**

Once user specifies the target journal:
- Search for the journal's "Instructions for Authors" / "Author Guidelines"
- Extract: manuscript structure, word limits, abstract format, figure/table limits, citation style, required sections (e.g., ICMJE disclosure, data availability statement, CRediT author contributions)
- If the journal uses a specific CSL style, find the corresponding Zotero CSL file

**Step B.3: Structure according to experiment type**

| Experiment Type | Standard Structure | Reporting Guideline |
|-----------------|-------------------|---------------------|
| RCT | IMRaD + CONSORT flow diagram | CONSORT 2010 |
| Cohort / Case-Control | IMRaD + STROBE checklist | STROBE |
| Diagnostic Accuracy | IMRaD + STARD flow diagram | STARD 2015 |
| Animal Study | IMRaD + ARRIVE checklist | ARRIVE 2.0 |
| In Vitro / Bench | Introduction-Methods-Results-Discussion | Journal-specific |
| Case Report | Introduction-Case-Report-Discussion | CARE |
| Qualitative | Introduction-Methods-Findings-Discussion | SRQR / COREQ |
| Systematic Review / Meta-Analysis | PRISMA structure | PRISMA 2020 |
| Computational / ML | IMRaD + model card | Journal-specific + ML-checklist |

**Step B.4: Incorporate real data**

- **Results section**: Describe actual findings from uploaded data
  - Insert real figures/tables with captions written in target journal style
  - Report exact p-values, effect sizes (95% CI), not just "significant"
  - Use target journal's convention (e.g., NEJM: "P=0.003", BMJ: "P=0.003 (95% CI 1.2 to 3.4)")
- **Methods section**: Describe what was actually done (past tense)
  - Sample size with power analysis justification
  - Statistical methods with software versions
  - Data availability statement
- **Discussion**: Interpret real results in context of the literature reviewed in Phase 2
  - "Consistent with [cite:key]..." / "In contrast to [cite:key]..."
  - Clinical/biological significance, not just statistical significance
  - Limitations framed honestly but not self-defeatingly

### Step 1: Outline + Evidence Map
Use ARS `ars-outline` to generate a detailed section-by-section outline with evidence mapping.
```
ars-outline: given [research_question] and [literature_set], generate:
  - Section-level structure
  - Key claims per section
  - Evidence source mapping (which paper supports which claim)
  - If EVIDENCE-DRIVEN: mark which uploaded data/figures belong in which section
```

### Step 2: Annotated Bibliography
Use ARS `ars-lit-review` to generate annotated bibliography in paper-ready format.
```
ars-lit-review: for each key paper, generate:
  - Full citation (APA / target style)
  - 3-5 sentence summary
  - Key findings relevant to the research question
  - Method notes (sample size, design, limitations)
```

### Step 3: Section Drafting
For each section, generate a draft grounded in sources:

**Introduction** — Use `report_compiler_agent` or `scientific-writing`:
- Background context (3-5 key citations)
- Problem statement
- Research gap (from gap-finder output)
- Research question + contribution

**Literature Review** — Use `report_compiler_agent` or `literature-review`:
- Thematic organization (not paper-by-paper)
- Compare/contrast findings
- Identify consensus and debate
- Highlight the gap this work fills

**Method** — Use `research_architect_agent`:
- If EVIDENCE-DRIVEN: describe what was actually done (past tense, real procedures)
- If HYPOTHETICAL: describe planned procedures (future tense)
- Study design, data sources, analysis pipeline, validity considerations

**Results** (only in EVIDENCE-DRIVEN mode):
- Describe findings from uploaded real data
- Insert real figures/tables with captions
- Statistical results (p-values, effect sizes, CIs)
- Cross-reference each finding with literature: "Consistent with [cite:key], we observed..."

**Discussion** — Use `scientific-manuscript` or `report_compiler_agent`:
- If EVIDENCE-DRIVEN: interpret real results, compare with prior findings
- If HYPOTHETICAL: "If results confirm H1, this would suggest...", conditional language
- Limitations, implications, future work

### Step 4: Sentence-Level Source Tracing
For every factual claim in the draft, run source verification:

```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python -c "
from scripts.notebooklm_bridge import NotebookLMBridge
b = NotebookLMBridge()
# For each claim in the draft:
result = b.research_query(
    topic='YOUR_TOPIC',
    pdf_paths=[...],  # Source PDFs
    question='Does the following claim have support in the sources? Claim: [CLAIM_TEXT]'
)
print(result['answer'])
"
```

Marking scheme:
- ✅ **Verified**: Source found with supporting passage → insert `{cite:key}`
- 🟡 **Partial**: Source mentions topic but not exact claim → user reviews
- 🔴 **No source**: No supporting passage found → user must add source or remove claim

### Step 5: Citation Key Insertion
After verification, insert Zotero citation keys using Better BibTeX format:
```
LaTeX:   \cite{zotero_key}
Markdown: [@zotero_key]
Word:     {cite:zotero_key}  (processed by Zotero Word plugin)
```

Use `metadata_indexer.py` to resolve DOIs/authors to citation keys:
```python
from scripts.metadata_indexer import MetadataIndexer
idx = MetadataIndexer()
item = idx.lookup_by_doi("10.xxx/yyy")
print(item["citation_key"])  # e.g., "smith2024novel"
```

### Step 6: Citation Error Check
Use ARS `ars-citation-check` to scan for:
- Missing citations (claims without sources)
- Mismatched author/year
- Incorrect DOI
- Broken reference links
- Duplicate references
- Page number errors in direct quotes

### Step 7: Format Output
Use ARS `ars-format-convert` to produce the target format:
- **LaTeX** (for arXiv / journal submission)
- **DOCX** (for sharing / revision)
- **PDF** (for reading)
- **Markdown** (for further editing)

Citation style via Zotero CSL:
- APA 7.0, Nature, Vancouver, GB7714, etc.
- Zotero handles CSL formatting when generating bibliography

### Step 8: Bilingual Abstract
Use ARS `ars-abstract` to generate English + Chinese abstract with keywords.

## Post-Writing: Revision Loop

Use ARS `ars-revision` or `ars-full` for iterative improvement:
1. User provides feedback / peer review comments
2. Claude revises draft with source re-verification
3. Citations updated in Zotero (new notes, extra fields)
4. Repeat until user approves

For handling peer review:
Use `ars-revision-coach` to parse reviewer comments → Revision Roadmap + Response Letter.

## Key Skills to Leverage
| Skill | Source | Role |
|-------|--------|------|
| `ars-outline` | ARS | Outline + evidence map |
| `ars-lit-review` | ARS | Annotated bibliography |
| `report_compiler_agent` | ARS plugin | APA 7.0 section drafting |
| `research_architect_agent` | ARS plugin | Method section blueprint |
| `ars-citation-check` | ARS | Citation error scanning |
| `ars-format-convert` | ARS | Output format conversion |
| `ars-abstract` | ARS | Bilingual abstract |
| `ars-revision` | ARS | Revised draft |
| `ars-revision-coach` | ARS | Reviewer response |
| `ars-full` | ARS | Full pipeline (write→review→revise) |
| `scientific-writing` | OpenClaw | Scientific writing |
| `scientific-manuscript` | OpenClaw | Manuscript drafting |
| `peer-review` | OpenClaw | Review simulation |
| `notebooklm-qa` | This project | Source verification per claim |
| `zotero-lit-index` | This project | Citation key resolution |
