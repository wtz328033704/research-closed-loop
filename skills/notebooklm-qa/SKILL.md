---
name: notebooklm-qa
description: Source-grounded Q&A via real Google NotebookLM (MCP) or Gemini Files API (fallback). Every answer is grounded in uploaded sources with inline citations — zero hallucination.
metadata:
  type: skill
  tags: [notebooklm, rag, qa, citation, grounding]
---

# NotebookLM Source-Grounded Q&A

## Purpose
Provide hallucination-free answers grounded exclusively in the user's uploaded literature. Uses real Google NotebookLM via MCP as the primary channel, with Gemini Files API as official fallback.

## Architecture
```
Sources (PDFs) ──→ NotebookLM Notebook (MCP channel)
                ──→ Gemini Files API (fallback channel)
                       │
                       ↓
              Source-grounded answer with inline citations
              [Author, Year, p.X] format
```

## When to Use
- User asks a question that must be answered from specific papers
- User wants to verify whether a claim is supported by their literature
- User needs source-grounded summaries, contradictions, or gap analysis
- As the "engine" behind `gap-finder` and `citation-writer` skills

## Setup (one-time)

### Primary Channel: NotebookLM MCP
```bash
pip install notebooklm-mcp-cli
nlm login    # Opens Chrome, log into your Google account
```

Verify:
```bash
nlm --version
nlm notebook list
```

### Fallback Channel: Gemini Files API
Set in `config/zotero_config.json`:
```json
{
  "notebooklm": {
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }
}
```
Or set environment variable: `$env:GEMINI_API_KEY = "YOUR_KEY"`

## Workflow

### Step 1: Check availability
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python -c "
from scripts.notebooklm_bridge import NotebookLMBridge
b = NotebookLMBridge()
print(b.status())
"
```

### Step 2: List existing notebooks & let user choose
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

🛑 **MUST pause here**: Present notebooks to user. Options:
- Create NEW notebook for this topic
- Use EXISTING notebook (user picks)
- Create new AND merge with existing

### Step 3: Prepare sources
Use `zotero-lit-index` skill to extract PDFs from Zotero.

🛑 **MUST pause here**: After uploading, show the source list and let user confirm before Q&A.

### Step 3: Query
```bash
cd "D:\AI-tool\Project\Smart_Brace_Project" && python -c "
from scripts.notebooklm_bridge import NotebookLMBridge
b = NotebookLMBridge()
result = b.research_query(
    topic='your-research-topic',
    pdf_paths=['path/to/paper1.pdf', 'path/to/paper2.pdf'],
    question='What are the key research gaps in this literature?'
)
print(result['answer'])
print(f'Channel used: {result[\"channel\"]}')
"
```

### Step 4: Extract and store answer
The answer includes inline citations. Save to project state for downstream use.

## Important Constraints
- NotebookLM MCP: max 50 sources per notebook, 500K words per source
- Gemini Files API: max 2GB per file, files expire after 48 hours
- Always verify citations against source text before using in writing
- The `primary_channel` auto-selects: MCP if available, else Gemini if configured

## Key Files
| File | Purpose |
|------|---------|
| `scripts/notebooklm_bridge.py` | Unified MCP + Gemini interface |
| `config/zotero_config.json` | API keys and NotebookLM settings |
