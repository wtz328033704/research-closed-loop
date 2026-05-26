"""
Reference importer: parse exported files from Embase, Web of Science, Scopus,
CNKI, WanFang, Cochrane, and other databases into a unified format.

Supports: RIS, BibTeX (.bib), CSV, and CNKI/WanFang EndNote-format .txt
"""
import json, os, re, csv, io, sys
from pathlib import Path
from typing import Optional
import bibtexparser


def parse_refs(file_path: str) -> list[dict]:
    """Auto-detect format and parse. Returns unified list of reference dicts."""
    ext = Path(file_path).suffix.lower()
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()

    if ext == ".ris" or content.strip().startswith("TY  "):
        return _parse_ris(content)
    elif ext == ".bib" or content.strip().startswith("@"):
        return _parse_bibtex(content)
    elif ext in (".csv", ".tsv"):
        return _parse_csv(content)
    elif ext == ".txt":
        if "TY  -" in content[:500]:
            return _parse_ris(content)
        if content.strip().startswith("@"):
            return _parse_bibtex(content)
        return _parse_cnki_txt(content)
    else:
        raise ValueError(f"Unsupported format: {ext}")


def _parse_ris(content: str) -> list[dict]:
    """Parse RIS format (used by Embase, WoS, Scopus, Cochrane)."""
    refs = []
    current = {}
    for line in content.splitlines():
        line = line.rstrip()
        if len(line) < 6:
            if current:
                refs.append(_ris_to_unified(current))
                current = {}
            continue
        tag = line[:2].strip()
        value = line[6:].strip()
        if tag == "ER":
            if current:
                refs.append(_ris_to_unified(current))
            current = {}
            continue
        if tag not in current:
            current[tag] = []
        current[tag].append(value)
    if current:
        refs.append(_ris_to_unified(current))
    return [r for r in refs if r.get("title") and r["title"] != "Untitled"]


def _ris_to_unified(ris: dict) -> dict:
    def first(tag):
        vals = ris.get(tag, [])
        return vals[0] if vals else ""

    def all_vals(tag):
        return ris.get(tag, [])

    authors = all_vals("AU") or all_vals("A1") or all_vals("A2")
    if not authors:
        authors = all_vals("A3") or all_vals("A4")

    doi = first("DO") or first("DI")
    # Sometimes DOI is embedded in UR or M3
    if not doi:
        for tag in ("UR", "M3", "C7", "ID"):
            val = first(tag)
            if val and ("10." in val or "doi" in val.lower()):
                doi = re.sub(r'^.*?(10\.\d{4,}/[^\s]+).*$', r'\1', val)
                break

    return {
        "title": first("TI") or first("T1") or first("CT") or first("BT") or "Untitled",
        "authors": [a.strip() for a in authors if a.strip()],
        "year": (first("PY") or first("Y1") or "")[:4],
        "doi": doi,
        "abstract": first("AB") or first("N2") or "",
        "journal": first("JO") or first("JF") or first("T2") or first("JA") or "",
        "volume": first("VL") or first("VO") or "",
        "issue": first("IS") or first("IP") or "",
        "pages": first("SP") + ("-" + first("EP") if first("EP") else ""),
        "type": first("TY") or "",
        "keywords": ", ".join(all_vals("KW")),
        "url": first("UR") or first("LK") or "",
        "source_db": first("DB") or "",
    }


def _parse_bibtex(content: str) -> list[dict]:
    """Parse BibTeX format."""
    try:
        lib = bibtexparser.loads(content)
    except Exception:
        lib = bibtexparser.parse_string(content)

    refs = []
    for entry in lib.entries:
        refs.append({
            "title": entry.get("title", "Untitled").strip("{}"),
            "authors": [a.strip() for a in entry.get("author", "").split(" and ") if a.strip()],
            "year": (entry.get("year", ""))[:4],
            "doi": entry.get("doi", ""),
            "abstract": entry.get("abstract", ""),
            "journal": entry.get("journal", "") or entry.get("booktitle", ""),
            "volume": entry.get("volume", ""),
            "issue": entry.get("number", ""),
            "pages": entry.get("pages", ""),
            "type": entry.get("ENTRYTYPE", ""),
            "keywords": entry.get("keywords", ""),
            "url": entry.get("url", ""),
            "source_db": entry.get("note", ""),
        })
    return [r for r in refs if r.get("title") and r["title"] != "Untitled"]


def _parse_csv(content: str) -> list[dict]:
    """Parse CSV/TSV (Scopus export, generic)."""
    delimiter = "\t" if "\t" in content[:200] else ","
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    refs = []
    for row in reader:
        title = (row.get("Title") or row.get("title") or row.get("Item Title") or "").strip()
        if not title:
            continue
        authors = (row.get("Authors") or row.get("Author(s)") or row.get("Author") or
                   row.get("Creator") or "").strip()
        refs.append({
            "title": title,
            "authors": [a.strip() for a in re.split(r'[;,]\s*', authors) if a.strip()],
            "year": (row.get("Year") or row.get("Publication Year") or
                     row.get("Date") or "")[:4],
            "doi": row.get("DOI") or row.get("doi") or "",
            "abstract": row.get("Abstract") or row.get("abstract") or "",
            "journal": (row.get("Journal") or row.get("Source Title") or
                       row.get("Publication Title") or "").strip(),
            "volume": row.get("Volume") or "",
            "issue": row.get("Issue") or "",
            "pages": row.get("Pages") or "",
            "type": row.get("Document Type") or "",
            "keywords": row.get("Keywords") or "",
            "url": row.get("URL") or row.get("Link") or "",
            "source_db": "",
        })
    return refs


def _parse_cnki_txt(content: str) -> list[dict]:
    """
    Parse CNKI/WanFang EndNote-format .txt export.
    Chinese databases use a line-based format: field label followed by value.
    """
    refs = []
    current = {}
    # Split by the record separator: two+ newlines, or lines starting with typical markers
    records = re.split(r'\n\s*\n(?=RT|Title|题名|标题|TI)', content)

    for record in records:
        current = {"raw": record}
        lines = record.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # CNKI format: "Field: value" or "Field value"
            m = re.match(r'^(RT|Title|TI|题名|标题|Author|AU|作者|Year|YR|PY|年份|DOI|Abstract|AB|摘要|Journal|JO|期刊|Source|SO|出处|Volume|VO|卷|Issue|NO|期|Pages|SP|页码|Keywords|KW|关键词)\s*[:：]?\s*(.*)', line, re.I)
            if m:
                field = m.group(1).lower()
                value = m.group(2).strip()
                if field in ("rt", "title", "ti", "题名", "标题"):
                    current["title"] = value
                elif field in ("author", "au", "作者"):
                    authors = current.get("authors", [])
                    authors.extend(a.strip() for a in re.split(r'[;,；，]\s*', value) if a.strip())
                    current["authors"] = authors
                elif field in ("year", "yr", "py", "年份"):
                    current["year"] = value[:4] if value else ""
                elif field in ("doi",):
                    current["doi"] = value
                elif field in ("abstract", "ab", "摘要"):
                    current["abstract"] = value
                elif field in ("journal", "jo", "期刊", "source", "so", "出处"):
                    current["journal"] = value
                elif field in ("volume", "vo", "卷"):
                    current["volume"] = value
                elif field in ("issue", "no", "期"):
                    current["issue"] = value
                elif field in ("pages", "sp", "页码"):
                    current["pages"] = value
                elif field in ("keywords", "kw", "关键词"):
                    current["keywords"] = value

        if current.get("title") and current["title"] != "Untitled":
            current.setdefault("authors", [])
            current.setdefault("year", "")
            current.setdefault("doi", "")
            current.setdefault("abstract", "")
            current.setdefault("journal", "")
            current.setdefault("volume", "")
            current.setdefault("issue", "")
            current.setdefault("pages", "")
            current.setdefault("type", "")
            current.setdefault("keywords", "")
            current.setdefault("url", "")
            current.setdefault("source_db", "CNKI/WanFang")
            refs.append({k: v for k, v in current.items() if k != "raw"})

    return refs


def merge_and_dedup(auto_results: list[dict], manual_results: list[dict],
                    manual_source: str = "") -> dict:
    """Merge automated + manual results, deduplicate by DOI and title similarity."""
    all_refs = []
    for r in auto_results:
        r["source"] = r.get("source", "automated")
        all_refs.append(r)
    for r in manual_results:
        r["source"] = f"manual:{manual_source}"
        all_refs.append(r)

    # Dedup by DOI
    seen_doi = {}
    deduped = []
    dupes = []
    for r in all_refs:
        doi = (r.get("doi") or "").lower().strip()
        if doi and doi in seen_doi:
            dupes.append({"kept": seen_doi[doi]["title"], "removed": r["title"]})
            continue
        if doi:
            seen_doi[doi] = r
        deduped.append(r)

    # Dedup by title similarity
    titles_seen = []
    final = []
    for r in deduped:
        t = _normalize_title(r.get("title", ""))
        is_dupe = False
        for seen_t, seen_r in titles_seen:
            if _title_similarity(t, seen_t) > 0.90:
                dupes.append({"kept": seen_r["title"], "removed": r["title"],
                               "match_type": "title_similarity"})
                is_dupe = True
                break
        if not is_dupe:
            titles_seen.append((t, r))
            final.append(r)

    return {"unique": final, "duplicates": dupes,
            "total_before_dedup": len(all_refs), "total_after_dedup": len(final)}


def _normalize_title(t: str) -> str:
    return re.sub(r'[^a-z0-9]', '', t.lower())


def _title_similarity(a: str, b: str) -> float:
    """Simple bigram Jaccard similarity for dedup."""
    def bigrams(s):
        return set(s[i:i+2] for i in range(len(s)-1))
    ba, bb = bigrams(a), bigrams(b)
    if not ba or not bb:
        return 0.0
    return len(ba & bb) / len(ba | bb)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ref_importer.py <file.ris|.bib|.csv|.txt>")
        print("Parses an exported reference file and prints unified JSON.")
        sys.exit(1)

    file_path = sys.argv[1]
    refs = parse_refs(file_path)
    print(f"Parsed {len(refs)} references from {file_path}")
    for i, r in enumerate(refs[:5]):
        print(f"  [{i+1}] [{r.get('year', '?')}] {r['title'][:80]}")
    if len(refs) > 5:
        print(f"  ... and {len(refs)-5} more")
