---
name: gap-finder
description: Research gap identification, contradiction detection, and hypothesis generation. Powered by ARS synthesis_agent + OpenClaw scientific reasoning skills.
metadata:
  type: skill
  tags: [research, gap-analysis, hypothesis, contradiction, feasibility]
---

# Research Gap Finder

## Purpose
Given a set of literature, identify feasible research gaps through contradiction detection, trend analysis, and systematic evaluation. Generates ranked, actionable hypotheses for the user to explore.

## When to Use
- User has a collection of papers and wants to find what's NOT been studied
- User needs to validate that a research idea is novel
- User wants a ranked list of feasible projects with cost/benefit analysis

## Pipeline

```
Literature Set (from Zotero collection / lit-search)
       │
       ↓
[1] Cross-Source Synthesis (synthesis_agent / knowledge-synthesis)
       │
       ↓
[2] Contradiction & Gap Matrix
       │
       ↓
[3] Feasibility Scoring
       │
       ↓
[4] Hypothesis Generation
       │
       ↓
[5] Interactive Dialog (ars-plan Socratic mode)
       │
       ↓
Research Plan: question → hypothesis → method → expected contribution
```

## Workflow Steps

### Step 1: Prepare literature input
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python -c "
from scripts.metadata_indexer import MetadataIndexer
idx = MetadataIndexer()
items = idx.search('YOUR_KEYWORD', field='title')
for i in items[:20]:
    print(f'[{i[\"year\"]}] {i[\"title\"][:80]} — {i[\"citation_key\"]}')
idx.close()
"
```
Select the most relevant papers (10-30) for gap analysis.

### Step 2: Cross-Source Synthesis
Use ARS `synthesis_agent` to extract key claims, methods, and findings across the paper set.

For each paper, extract:
- **Claim**: What does this paper assert?
- **Method**: How was the claim tested? (dataset, approach, metrics)
- **Scope**: What domain/condition/population does it apply to?
- **Limitation**: What does the paper explicitly identify as limitations?
- **Open Question**: What future work does it suggest?

Then use `synthesis_agent` to cross-compare:
- Which claims are **consistent** across multiple papers? → Consensus findings
- Which claims **contradict** each other? → Active debate areas
- Which claims are **isolated** (only one paper)? → Need replication

Also use OpenClaw `knowledge-synthesis` skill for alternative aggregation.

### Step 3: Build Contradiction & Gap Matrix

Produce a structured matrix:

| Dimension | Covered by | Coverage density | Gap quality |
|-----------|-----------|-----------------|-------------|
| Population X | Paper A, B | High (5+ papers) | Low (saturated) |
| Method Y | Paper C only | Low (1 paper) | High (under-explored) |
| Condition Z | None | Zero | Very High (untouched) |
| Cross: X×Z | None | Zero | Very High (novel combination) |

Gap types to identify:
1. **Contradiction gap**: Papers disagree → needs resolution study
2. **Replication gap**: Single study claims X → needs independent replication
3. **Methodology gap**: All papers use method A → opportunity for method B
4. **Population gap**: Studied in population X but not Y → generalization study
5. **Temporal gap**: Last studied in 2018 → needs update with current methods
6. **Cross-domain gap**: Two fields have adjacent findings → integration opportunity
7. **Scale gap**: Lab-scale only → real-world / large-scale study needed

### Step 4: Feasibility Scoring

Score each gap on 5 dimensions (1-10 each):

| Dimension | 1-3 (Hard) | 4-7 (Moderate) | 8-10 (Easy) |
|-----------|-----------|----------------|-------------|
| **Data Availability** | No public data | Some data, needs collection | Rich public datasets |
| **Method Maturity** | New method needed | Adapt existing method | Standard pipeline exists |
| **Time to Completion** | 2+ years | 1-2 years | < 1 year |
| **Novelty Impact** | Incremental | Significant advance | Paradigm-shifting |
| **Publication Potential** | Niche venue | Mid-tier journal | Top-tier venue likely |

Final score = weighted sum. Recommend weights:
- For PhD students: Data×0.3 + Method×0.2 + Time×0.2 + Novelty×0.15 + Publication×0.15
- For established researchers: Novelty×0.35 + Publication×0.30 + Data×0.15 + Method×0.10 + Time×0.10

### Step 5: Hypothesis Generation

For each top-scoring gap, use OpenClaw `hypothesis-generation` skill to generate:
- **H0** (null hypothesis): precise, falsifiable
- **H1** (alternative hypothesis): the expected finding
- **Test strategy**: what experiment/analysis would test H0 vs H1
- **Expected effect size**: if prior data exists, estimate
- **Sample size estimate**: power analysis (use OpenClaw `bio-experimental-design-power-analysis` for quantitative studies)
- **Confounding factors**: what could explain away a positive result

### Step 6: Interactive Socratic Planning

Use ARS `ars-plan` mode for chapter-by-chapter research planning.

Conduct a Socratic dialog with the user:
1. "Here are the top 3 gaps. Which interests you most?"
2. "For gap #X, here's my proposed research question. Does this match your intuition?"
3. "The hypothesis would be: [H0/H1]. Can you think of boundary conditions where this wouldn't hold?"
4. "The method I suggest is [method]. What resources/data do you have access to?"
5. "The expected contribution is [X]. Is this sufficient for your goals (thesis chapter / paper / grant proposal)?"

After each answer, refine the plan. Iterate until user confirms.

### Step 7: Output Research Plan

Save a structured research plan to the project state:
```json
{
  "research_question": "...",
  "hypotheses": {"H0": "...", "H1": "..."},
  "methodology_blueprint": "...",
  "data_requirements": ["...", "..."],
  "expected_contributions": ["...", "..."],
  "feasibility_score": 8.2,
  "selected_from_gaps": ["gap_id_1", "gap_id_2"],
  "literature_base": ["cite_key_1", "cite_key_2"],
  "plan_timestamp": "2026-05-26T..."
}
```

## Key Skills to Leverage
| Skill | Source | Role |
|-------|--------|------|
| `synthesis_agent` | ARS plugin | Cross-source contradiction detection & gap identification |
| `ars-plan` | ARS plugin | Socratic chapter-by-chapter planning |
| `research_architect_agent` | ARS plugin | Methodology blueprint |
| `knowledge-synthesis` | OpenClaw | Multi-source knowledge aggregation |
| `hypothesis-generation` | OpenClaw | Hypothesis formulation |
| `scientific-problem-selection` | OpenClaw | Feasibility & impact ranking |
| `scientific-critical-thinking` | OpenClaw | Bias detection, logical validity |
| `notebooklm-qa` | This project | Source-grounded verification of claims |
