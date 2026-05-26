"""
Environment setup: ensures all CLI tools and Python packages are ready.
Run once per session: python scripts/env_setup.py
"""
import os, sys, subprocess, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def setup_path():
    """Add Python Scripts dirs to PATH so nlm and other CLIs are found."""
    scripts_dirs = [
        os.path.expandvars(r"%APPDATA%\Python\Python314\Scripts"),
        os.path.expandvars(r"%APPDATA%\Python\Python313\Scripts"),
        os.path.expandvars(r"%APPDATA%\Python\Python312\Scripts"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python314\Scripts"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python313\Scripts"),
    ]
    added = []
    for d in scripts_dirs:
        if os.path.isdir(d) and d not in os.environ.get("PATH", ""):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            added.append(d)
    return added


def check_imports():
    results = {}
    for mod in ["pyzotero", "fitz", "markitdown", "chromadb"]:
        try:
            __import__(mod)
            results[mod] = "OK"
        except ImportError:
            results[mod] = "MISSING (pip install)"
    return results


def check_nlm():
    nlm = shutil.which("nlm") or shutil.which("nlm.exe")
    if not nlm:
        return None, "NOT FOUND"
    try:
        r = subprocess.run([nlm, "--version"], capture_output=True, text=True, timeout=10)
        version = r.stdout.strip().split()[-1] if r.returncode == 0 else "ERROR"
        return nlm, version
    except Exception as e:
        return nlm, str(e)


def check_nlm_auth():
    profiles = list(Path.home().glob(".notebooklm-mcp-cli/profiles/*"))
    if profiles:
        return True, str(profiles[0])
    legacy = Path.home() / ".notebooklm" / "session.json"
    if legacy.exists():
        return True, str(legacy)
    return False, ""


def main():
    print("=== Research Closed-Loop Environment Setup ===\n")

    print("[1/4] PATH setup...")
    added = setup_path()
    print(f"  Added {len(added)} Python Scripts dirs" if added else "  PATH already configured")

    print("\n[2/4] Python packages...")
    for mod, status in check_imports().items():
        print(f"  {mod}: {status}")

    print("\n[3/4] NotebookLM MCP (nlm CLI)...")
    nlm_path, version = check_nlm()
    if nlm_path:
        print(f"  nlm: {version} ({nlm_path})")
        authed, loc = check_nlm_auth()
        print(f"  Auth: {'YES' if authed else 'NEED nlm login'} {f'({loc})' if loc else ''}")
    else:
        print(f"  nlm: {version}")

    print("\n[4/4] Zotero...")
    cfg_path = PROJECT_ROOT / "config" / "zotero_config.json"
    import json
    cfg = json.load(open(cfg_path))
    z = cfg["zotero"]
    sqlite_ok = os.path.exists(z["sqlite_path"])
    print(f"  SQLite: {'FOUND' if sqlite_ok else 'NOT FOUND'} ({z['sqlite_path']})")
    print(f"  API key: {'SET' if z.get('api_key') else 'NOT SET'}")
    gemini_key = cfg["notebooklm"].get("gemini_api_key", "")
    print(f"  Gemini key: {'SET' if gemini_key else 'NOT SET'}")

    print("\n=== Ready ===")


if __name__ == "__main__":
    main()
