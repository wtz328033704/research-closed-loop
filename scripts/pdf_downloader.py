"""
PDF auto-downloader by DOI.
Tries: Unpaywall → Sci-Hub → PMC → Google Scholar.
Attaches downloaded PDF to Zotero item.
"""
import json, os, sys, shutil, time
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))
from zotero_connector import ZoteroConnector


class PDFDownloader:
    """Download PDFs from multiple sources by DOI."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "zotero_config.json"
        with open(config_path) as f:
            self.config = json.load(f)
        self.zotero = ZoteroConnector(config_path)
        self.storage_dir = self.config["zotero"]["storage_dir"]
        self.scidb_domains = ["sci-hub.ru", "sci-hub.st", "sci-hub.su", "sci-hub.ee"]

    def download_by_doi(self, doi: str, item_key: str = None,
                        output_dir: str = None) -> Optional[str]:
        """Download a PDF by DOI. Returns path to downloaded file or None."""
        doi = doi.strip()
        if not doi.startswith("10."):
            return None

        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "data" / "pdfs"
        os.makedirs(output_dir, exist_ok=True)

        for method in [self._try_unpaywall, self._try_scidb, self._try_pmc]:
            try:
                result = method(doi, output_dir)
                if result:
                    return result
            except Exception:
                continue
        return None

    def download_and_attach(self, doi: str, item_key: str) -> bool:
        """Download PDF and attach to Zotero item. Returns success."""
        item = self.zotero.get_item_by_key(item_key)
        title = item.get("title", "paper")[:50].replace("/", "_")
        out_dir = os.path.join(self.storage_dir, item_key[:2], item_key)
        os.makedirs(out_dir, exist_ok=True)

        pdf_path = self.download_by_doi(doi, item_key, out_dir)
        if not pdf_path:
            return False

        # Rename to match Zotero convention
        dest = os.path.join(out_dir, f"{title}.pdf")
        shutil.move(pdf_path, dest)
        print(f"  PDF saved: {dest}")
        return True

    def batch_download(self, dois: list[str], item_keys: list[str] = None) -> dict:
        """Download PDFs for a list of DOIs. Shows progress."""
        if item_keys is None:
            item_keys = [None] * len(dois)
        ok, fail = 0, 0
        total = len(dois)
        for i, (doi, key) in enumerate(zip(dois, item_keys)):
            title = ""
            if key:
                item = self.zotero.get_item_by_key(key)
                title = item.get("title", "")[:60]
            status = "✓" if self.download_and_attach(doi, key) else "✗"
            if status == "✓":
                ok += 1
            else:
                fail += 1
            bar = "█" * ((i + 1) * 20 // total) + "░" * (20 - (i + 1) * 20 // total)
            print(f"\r  [{bar}] {i+1}/{total} {status} {title[:50]}", end="", flush=True)
        print()
        return {"downloaded": ok, "failed": fail, "total": total}

    # ── Internal methods ─────────────────────────────────────

    def _try_unpaywall(self, doi: str, out_dir: str) -> Optional[str]:
        """Try Unpaywall for open-access PDF link."""
        url = f"https://api.unpaywall.org/v2/{quote(doi)}?email=research-closed-loop@example.com"
        try:
            req = Request(url, headers={"User-Agent": "ResearchClosedLoop/1.0"})
            data = json.loads(urlopen(req, timeout=15).read())
            oa_url = data.get("best_oa_location", {}).get("url_for_pdf", "")
            if oa_url:
                return self._download_url(oa_url, doi, out_dir)
        except Exception:
            pass
        return None

    def _try_scidb(self, doi: str, out_dir: str) -> Optional[str]:
        """Try Sci-Hub mirrors."""
        for domain in self.scidb_domains:
            for prefix in ["https://", "http://"]:
                try:
                    url = f"{prefix}{domain}/{doi}"
                    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    html = urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")

                    # Look for embedded PDF URL
                    import re
                    m = re.search(r'(?:iframe|embed)\s+src\s*=\s*["\'](.*?\.pdf)["\']', html, re.I)
                    if m:
                        pdf_url = m.group(1)
                        if pdf_url.startswith("//"):
                            pdf_url = "https:" + pdf_url
                        elif pdf_url.startswith("/"):
                            pdf_url = f"{prefix}{domain}{pdf_url}"
                        result = self._download_url(pdf_url, doi, out_dir)
                        if result:
                            return result

                    # Some mirrors embed PDF as data or via button
                    m2 = re.search(r'(?:href|src)\s*=\s*["\']([^"\']*?/downloads/[^"\']*?\.pdf)["\']', html, re.I)
                    if m2:
                        result = self._download_url(m2.group(1), doi, out_dir)
                        if result:
                            return result
                except Exception:
                    continue
        return None

    def _try_pmc(self, doi: str, out_dir: str) -> Optional[str]:
        """Try PubMed Central."""
        pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/?term={quote(doi)}&report=classic"
        try:
            req = Request(pmc_url, headers={"User-Agent": "ResearchClosedLoop/1.0"})
            html = urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
            import re
            m = re.search(r'(?:href|src)\s*=\s*["\']([^"\']*?/pmc/articles/PMC\d+/pdf/[^"\']*?\.pdf)["\']', html, re.I)
            if m:
                pdf_url = "https://www.ncbi.nlm.nih.gov" + m.group(1)
                return self._download_url(pdf_url, doi, out_dir)
        except Exception:
            pass
        return None

    def _download_url(self, url: str, doi: str, out_dir: str) -> Optional[str]:
        """Download a PDF from a URL."""
        safe_name = doi.replace("/", "_").replace(":", "_")[:80] + ".pdf"
        path = os.path.join(out_dir, safe_name)
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=30) as resp, open(path, "wb") as f:
                f.write(resp.read())
            if os.path.getsize(path) > 1024:  # > 1KB = real PDF
                return path
            os.remove(path)
        except Exception:
            pass
        return None

    def close(self):
        self.zotero.close()


if __name__ == "__main__":
    d = PDFDownloader()
    # Test with a known open-access DOI
    result = d.download_by_doi("10.3390/s24113652")
    print(f"Test download: {result or 'FAILED'}")
    d.close()
