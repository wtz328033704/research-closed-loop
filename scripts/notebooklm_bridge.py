"""
NotebookLM bridge: manages NotebookLM integration via MCP (primary) + Gemini API (fallback).

Requires:
  - notebooklm-mcp-cli (pip): primary channel, full NotebookLM features
  - google-genai (pip): fallback channel, Gemini Files API

Setup:
  pip install notebooklm-mcp-cli
  nlm login    (opens browser for Google OAuth)
  pip install google-genai
"""
import json, os, subprocess, sys, shutil
from pathlib import Path
from typing import Optional

# Ensure nlm CLI is on PATH
_NLM_PATHS = [
    os.path.expandvars(r"%APPDATA%\Python\Python314\Scripts"),
    os.path.expandvars(r"%APPDATA%\Python\Python313\Scripts"),
    os.path.expandvars(r"%APPDATA%\Python\Python312\Scripts"),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python314\Scripts"),
]
for _p in _NLM_PATHS:
    if os.path.isdir(_p) and _p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")


class NotebookLMBridge:
    """Unified interface to NotebookLM MCP + Gemini Files API fallback."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "zotero_config.json"
        with open(config_path) as f:
            self.config = json.load(f)
        self.nlm_config = self.config["notebooklm"]

    def _find_nlm(self) -> str:
        """Find the nlm executable. Raises FileNotFoundError if not found."""
        nlm_exe = shutil.which("nlm") or shutil.which("nlm.exe")
        if nlm_exe:
            return nlm_exe
        for p in _NLM_PATHS:
            candidate = os.path.join(p, "nlm.exe")
            if os.path.exists(candidate):
                return candidate
        raise FileNotFoundError("nlm CLI not found. Install with: pip install notebooklm-mcp-cli")

    def _run_nlm(self, *args, timeout: int = 120) -> subprocess.CompletedProcess:
        """Run nlm CLI command. Raises RuntimeError on auth expiry."""
        nlm_exe = self._find_nlm()
        result = subprocess.run([nlm_exe, *args], capture_output=True, text=True, timeout=timeout)
        # Detect auth expiry
        if result.returncode != 0 and "Authentication" in (result.stderr or ""):
            raise RuntimeError("NLM_AUTH_EXPIRED")
        return result

    def _is_auth_error(self, error_output: str) -> bool:
        return "Authentication" in error_output or "expired" in error_output.lower()

    # ── Status checks ──────────────────────────────────────────

    def check_mcp_installed(self) -> bool:
        """Check if notebooklm-mcp-cli is available."""
        try:
            result = self._run_nlm("--version", timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_mcp_authenticated(self) -> bool:
        """Check if we have valid NotebookLM credentials by actually trying a command."""
        # Fast check: credential files exist
        files_ok = False
        for candidate in [
            Path.home() / ".notebooklm-mcp-cli" / "profiles" / "default",
            Path.home() / ".notebooklm" / "session.json",
        ]:
            if candidate.exists():
                files_ok = True
                break
        if not files_ok:
            return False
        # Live check: can we actually run a command?
        try:
            result = self._run_nlm("notebook", "list", timeout=15)
            return result.returncode == 0
        except Exception:
            return False

    def refresh_auth(self) -> bool:
        """Run nlm login to refresh expired credentials."""
        print("NotebookLM session expired. Running nlm login...")
        try:
            result = subprocess.run(
                [self._find_nlm(), "login"],
                capture_output=False, timeout=300  # no capture so user sees browser
            )
            return result.returncode == 0
        except Exception as e:
            print(f"nlm login failed: {e}")
            return False

    def check_gemini_available(self) -> bool:
        """Check if Gemini API key is configured AND importable."""
        key = self.nlm_config.get("gemini_api_key", "")
        if not key and not os.environ.get("GEMINI_API_KEY"):
            return False
        try:
            import google.genai  # noqa: F401
            return True
        except ImportError:
            return False

    def status(self) -> dict:
        mcp_installed = self.check_mcp_installed()
        mcp_auth = self.check_mcp_authenticated() if mcp_installed else False
        gemini_ok = self.check_gemini_available()
        if mcp_installed and mcp_auth:
            channel = "mcp"
        elif gemini_ok:
            channel = "gemini"
        else:
            channel = "none"
        return {
            "mcp_installed": mcp_installed,
            "mcp_authenticated": mcp_auth,
            "gemini_available": gemini_ok,
            "primary_channel": channel,
        }

    # ── Notebook management (via nlm CLI) ──────────────────────

    def create_notebook(self, topic: str) -> Optional[str]:
        """Create a NotebookLM notebook for a research topic. Returns notebook ID."""
        name = self.nlm_config["default_notebook_name"].format(topic=topic)
        try:
            result = self._run_nlm("notebook", "create", "--name", name, timeout=30)
            if result.returncode == 0:
                # Extract notebook ID from output
                for line in result.stdout.splitlines():
                    if "id" in line.lower() or "created" in line.lower():
                        return line.strip()
                return result.stdout.strip()
            else:
                print(f"MCP create error: {result.stderr}")
                return None
        except Exception as e:
            print(f"MCP create failed: {e}")
            return None

    def upload_source(self, notebook_name: str, source_path: str,
                      source_type: str = "pdf") -> bool:
        """Upload a PDF or URL source to a notebook."""
        try:
            result = self._run_nlm("source", "add", "--notebook", notebook_name,
                                   "--type", source_type, source_path, timeout=120)
            return result.returncode == 0
        except Exception as e:
            print(f"MCP upload failed: {e}")
            return False

    def upload_sources_batch(self, notebook_name: str, sources: list[str],
                             source_type: str = "pdf") -> dict:
        """Upload multiple sources. Returns success/failure counts."""
        ok, fail = 0, 0
        max_sources = self.nlm_config["max_sources_per_notebook"]
        for src in sources[:max_sources]:
            if self.upload_source(notebook_name, src, source_type):
                ok += 1
            else:
                fail += 1
        return {"uploaded": ok, "failed": fail, "total": len(sources[:max_sources])}

    def ask_notebook(self, notebook_name: str, question: str) -> Optional[str]:
        """Query a notebook and get a source-grounded answer with citations."""
        try:
            result = self._run_nlm("chat", "--notebook", notebook_name,
                                   "--prompt", question, timeout=120)
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"MCP chat error: {result.stderr}")
                return None
        except RuntimeError as e:
            if "NLM_AUTH_EXPIRED" in str(e):
                raise  # re-raise for caller to handle with refresh
            print(f"MCP chat failed: {e}")
            return None
        except Exception as e:
            print(f"MCP chat failed: {e}")
            return None

    # ── Gemini Files API fallback ───────────────────────────────

    def ask_gemini_with_files(self, pdf_paths: list[str], question: str) -> Optional[str]:
        """Upload PDFs to Gemini Files API and get source-grounded answer."""
        try:
            from google import genai
        except ImportError:
            return "ERROR: pip install google-genai required for Gemini fallback."

        api_key = self.nlm_config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "ERROR: Gemini API key not configured."

        client = genai.Client(api_key=api_key)
        model_name = self.nlm_config.get("gemini_model", "gemini-2.5-pro")

        uploaded = []
        for path in pdf_paths:
            try:
                file = client.files.upload(file=path)
                uploaded.append(file)
            except Exception as e:
                print(f"Gemini upload failed for {path}: {e}")

        if not uploaded:
            return "ERROR: No files could be uploaded to Gemini."

        grounding_prompt = f"""{question}

Answer based ONLY on the uploaded documents. For every claim, cite the source document
and provide the relevant passage. If the documents don't contain enough information to
answer, say so explicitly."""

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[grounding_prompt] + uploaded,
            )
            return response.text
        except Exception as e:
            return f"Gemini API error: {e}"

    # ── High-level workflow ────────────────────────────────────

    def research_query(self, topic: str, pdf_paths: list[str],
                       question: str, notebook_name: str = None) -> dict:
        """
        Main entry point: answer a research question using source-grounded methods.
        Tries NotebookLM MCP first → retries with re-auth on expiry → falls back to Gemini.
        """
        if notebook_name is None:
            notebook_name = self.nlm_config["default_notebook_name"].format(topic=topic)

        status = self.status()
        answer = None
        channel = None
        errors = []

        # Try MCP
        if status["mcp_installed"] and status["mcp_authenticated"]:
            try:
                notebook_id = self.create_notebook(topic)
                if notebook_id:
                    self.upload_sources_batch(notebook_name, pdf_paths)
                    answer = self.ask_notebook(notebook_name, question)
                    channel = "notebooklm-mcp"
            except RuntimeError as e:
                if "NLM_AUTH_EXPIRED" in str(e):
                    errors.append("MCP auth expired")
                    # Try re-auth once
                    if self.refresh_auth():
                        try:
                            notebook_id = self.create_notebook(topic)
                            if notebook_id:
                                self.upload_sources_batch(notebook_name, pdf_paths)
                                answer = self.ask_notebook(notebook_name, question)
                                channel = "notebooklm-mcp (re-authed)"
                        except Exception as e2:
                            errors.append(f"MCP retry failed: {e2}")
                else:
                    errors.append(str(e))
            except Exception as e:
                errors.append(str(e))

        # Fallback to Gemini
        if answer is None and status["gemini_available"]:
            answer = self.ask_gemini_with_files(pdf_paths, question)
            channel = "gemini-files-api (fallback)" if errors else "gemini-files-api"

        if answer is None:
            answer = "Cannot answer: "
            if errors:
                answer += "; ".join(errors)
            else:
                answer += "no available channel. Install notebooklm-mcp-cli or set GEMINI_API_KEY."
            channel = "none"

        return {"question": question, "answer": answer, "channel": channel,
                "sources_used": len(pdf_paths), "notebook": notebook_name,
                "errors": errors}


if __name__ == "__main__":
    bridge = NotebookLMBridge()
    status = bridge.status()
    print(json.dumps(status, indent=2))
    if status["primary_channel"] == "none":
        print("\nTo enable NotebookLM integration:")
        print("  pip install notebooklm-mcp-cli")
        print("  nlm login")
        print("Or set GEMINI_API_KEY for Gemini fallback")
