---
name: r
description: Start research closed-loop. Shortcut: /r [topic]
metadata:
  type: alias
  target: research-closed-loop
---

When invoked, execute the `research-closed-loop` workflow starting from Phase 0 (environment check + credential setup), then proceed through all phases with HITL gates. If the user provides a topic, use it as the research topic for Phase 1.
