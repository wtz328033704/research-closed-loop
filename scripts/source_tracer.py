"""
Source tracer: verify every factual claim in a draft against uploaded literature.
Uses NotebookLM MCP to check each claim, then produces a verification report.
"""
import json, os, re, sys, subprocess, shutil, time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from notebooklm_bridge import NotebookLMBridge


class SourceTracer:
    """Automated sentence-level source verification using NotebookLM."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "zotero_config.json"
        self.bridge = NotebookLMBridge(config_path)
        with open(config_path) as f:
            self.config = json.load(f)

    def extract_claims(self, text: str) -> list[dict]:
        """Extract factual claims from text. Each sentence or citation-linked statement."""
        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claims = []
        for i, s in enumerate(sentences):
            s = s.strip()
            if not s or len(s) < 20:
                continue
            # Skip purely structural sentences
            if re.match(r'^(Figure|Table|See|As shown|Notably|Interestingly)', s):
                claims.append({"index": i, "text": s, "type": "structural", "status": "skipped"})
                continue
            claims.append({"index": i, "text": s, "type": "factual", "status": "pending"})
        return claims

    def verify_claims(self, claims: list[dict], notebook_name: str,
                      topic: str) -> list[dict]:
        """Verify each claim against NotebookLM sources. Shows progress."""
        factual = [c for c in claims if c["type"] == "factual"]
        total = len(factual)
        verified, partial, failed = 0, 0, 0

        for i, claim in enumerate(factual):
            bar = "█" * ((i + 1) * 20 // max(total, 1)) + "░" * (20 - (i + 1) * 20 // max(total, 1))
            print(f"\r  [{bar}] {i+1}/{total} checking...", end="", flush=True)

            result = self._check_single_claim(claim["text"], notebook_name, topic)
            claim["status"] = result["status"]
            claim["source"] = result.get("source", "")
            claim["explanation"] = result.get("explanation", "")

            if result["status"] == "verified":
                verified += 1
            elif result["status"] == "partial":
                partial += 1
            else:
                failed += 1

            time.sleep(0.5)  # rate limit

        print(f"\n  Done: ✅{verified} 🟡{partial} 🔴{failed}")
        return claims

    def _check_single_claim(self, claim: str, notebook_name: str,
                            topic: str) -> dict:
        """Check one claim against NotebookLM."""
        question = (
            f"Does the uploaded literature support the following claim? "
            f"Answer with YES (with source citation), PARTIALLY (with explanation), "
            f"or NO (with explanation). Claim: \"{claim}\""
        )
        try:
            resp = self.bridge.research_query(topic, [], question, notebook_name)
            answer = resp.get("answer", "")

            if not answer or "cannot answer" in answer.lower():
                return {"status": "unverified", "source": "", "explanation": "Bridge unavailable"}

            answer_lower = answer.lower()
            if answer_lower.startswith("yes") or "yes" in answer_lower[:20]:
                # Extract source info
                source = ""
                cite_match = re.search(r'\[([^\]]+)\]', answer)
                if cite_match:
                    source = cite_match.group(1)
                return {"status": "verified", "source": source, "explanation": answer[:200]}
            elif "partial" in answer_lower[:30]:
                return {"status": "partial", "source": "", "explanation": answer[:200]}
            else:
                return {"status": "unverified", "source": "", "explanation": answer[:200]}
        except Exception as e:
            return {"status": "unverified", "source": "", "explanation": str(e)[:200]}

    def trace_document(self, text: str, notebook_name: str,
                       topic: str) -> dict:
        """Full verification of a document. Returns report."""
        print(f"\n=== Source Tracing ===")
        print(f"Notebook: {notebook_name}")
        print(f"Sections: {len(re.split(r'(?<=[.!?])\s+', text))} sentences")

        claims = self.extract_claims(text)
        claims = self.verify_claims(claims, notebook_name, topic)

        factual_claims = [c for c in claims if c["type"] == "factual"]
        verified = sum(1 for c in factual_claims if c["status"] == "verified")
        partial = sum(1 for c in factual_claims if c["status"] == "partial")
        unverified = sum(1 for c in factual_claims if c["status"] == "unverified")

        report = {
            "total_claims": len(factual_claims),
            "verified": verified,
            "partial": partial,
            "unverified": unverified,
            "verification_rate": round(verified / max(len(factual_claims), 1) * 100, 1),
            "claims": claims,
            "unverified_details": [c for c in factual_claims if c["status"] == "unverified"],
            "partial_details": [c for c in factual_claims if c["status"] == "partial"],
        }

        print(f"\n=== Verification Report ===")
        print(f"  ✅ Verified:  {verified}/{len(factual_claims)} ({report['verification_rate']}%)")
        print(f"  🟡 Partial:   {partial}")
        print(f"  🔴 Unverified: {unverified}")

        if unverified > 0:
            print(f"\n  ⚠️ Unverified claims:")
            for c in factual_claims:
                if c["status"] == "unverified":
                    print(f"    🔴 {c['text'][:100]}...")

        return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python source_tracer.py <draft_file.txt> [notebook_name]")
        print("Verifies every factual claim in the draft against NotebookLM sources.")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    notebook = sys.argv[2] if len(sys.argv) > 2 else "ACL-RTS-Biomechanics"
    tracer = SourceTracer()
    report = tracer.trace_document(text, notebook, "ACL RTS")

    # Save report
    out_path = sys.argv[1].replace(".txt", "_trace_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport saved: {out_path}")
