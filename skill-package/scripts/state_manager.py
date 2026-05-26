"""
Project state persistence: save/load research project state to disk.
Enables resuming work across Claude Code sessions.
"""
import json, os
from pathlib import Path
from datetime import datetime
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "data" / "projects"


def ensure_state_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def project_exists(project_name: str) -> bool:
    return (STATE_DIR / _safe_name(project_name) / "state.json").exists()


def load_state(project_name: str) -> dict:
    path = STATE_DIR / _safe_name(project_name) / "state.json"
    if not path.exists():
        return _empty_state(project_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict):
    name = _safe_name(state.get("project_name", "unnamed"))
    proj_dir = STATE_DIR / name
    os.makedirs(proj_dir, exist_ok=True)
    state["updated_at"] = datetime.now().isoformat()
    with open(proj_dir / "state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def update_phase(state: dict, phase: int, status: str = "in_progress", details: dict = None):
    """Update a phase status and optionally store phase-specific data."""
    state["current_phase"] = phase
    phase_key = f"phase_{phase}"
    if phase_key not in state:
        state[phase_key] = {}
    state[phase_key]["status"] = status
    if details:
        state[phase_key].update(details)
    if status == "completed" and phase not in state.get("phases_completed", []):
        state.setdefault("phases_completed", []).append(phase)
    save_state(state)


def store_search_results(state: dict, results: list[dict]):
    state.setdefault("phase_1", {})["search_results"] = results
    save_state(state)


def store_notebook_info(state: dict, notebook_name: str, notebook_id: str, sources: list[str]):
    state.setdefault("phase_2", {}).update({
        "notebook_name": notebook_name,
        "notebook_id": notebook_id,
        "uploaded_sources": sources,
    })
    save_state(state)


def store_gap_analysis(state: dict, gaps: list[dict], selected_gap: int = None):
    state.setdefault("phase_3", {}).update({
        "gaps": gaps,
        "selected_gap_index": selected_gap,
        "selected_gap": gaps[selected_gap] if selected_gap is not None and selected_gap < len(gaps) else None,
    })
    save_state(state)


def store_research_plan(state: dict, plan: dict):
    state.setdefault("phase_4", {})["plan"] = plan
    save_state(state)


def store_uploaded_data(state: dict, data_files: list[str], data_interpretation: dict = None):
    state.setdefault("phase_4_5", {}).update({
        "has_real_data": len(data_files) > 0,
        "data_files": data_files,
        "interpretation": data_interpretation,
        "writing_mode": "evidence-driven" if data_files else "hypothetical",
    })
    save_state(state)


def store_draft_info(state: dict, sections: dict, verification_report: dict):
    state.setdefault("phase_5", {}).update({
        "sections": sections,
        "verification": verification_report,
    })
    save_state(state)


def store_target_journal(state: dict, journal_name: str, style: str, requirements: dict = None):
    state.setdefault("phase_5", {})["target_journal"] = {
        "name": journal_name,
        "citation_style": style,
        "requirements": requirements or {},
    }
    save_state(state)


def list_projects() -> list[dict]:
    ensure_state_dir()
    projects = []
    for d in sorted(STATE_DIR.iterdir(), reverse=True):
        if d.is_dir():
            sf = d / "state.json"
            if sf.exists():
                try:
                    s = json.load(open(sf, encoding="utf-8"))
                    projects.append({
                        "name": s.get("project_name", d.name),
                        "topic": s.get("topic", ""),
                        "current_phase": s.get("current_phase", 0),
                        "phases_completed": s.get("phases_completed", []),
                        "updated_at": s.get("updated_at", ""),
                    })
                except Exception:
                    pass
    return projects


def _empty_state(project_name: str) -> dict:
    return {
        "project_name": project_name,
        "topic": "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "current_phase": 0,
        "phases_completed": [],
        "phase_0": {"status": "pending"},
        "phase_1": {"status": "pending"},
        "phase_2": {"status": "pending"},
        "phase_3": {"status": "pending"},
        "phase_4": {"status": "pending"},
        "phase_4_5": {"status": "pending", "has_real_data": False},
        "phase_5": {"status": "pending"},
        "phase_6": {"status": "pending"},
    }


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "._- " else "_" for c in name).strip()[:80]


if __name__ == "__main__":
    ensure_state_dir()
    existing = list_projects()
    print(f"Saved projects: {len(existing)}")
    for p in existing:
        print(f"  {p['name']} — Phase {p['current_phase']} — {p['updated_at'][:19]}")
