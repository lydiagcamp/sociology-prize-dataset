"""Pull OpenAlex records for matched articles and write them as tables.

Reads data/openalex/article_matches.csv (from match_openalex.py). An article
is linked if Confirmed_DOI is filled in (and not "none"), or if Match_Status
is "auto". Works are fetched 50 DOIs per request (1 OpenAlex credit each).

Outputs in data/openalex/:
  works.csv              one row per work: bibliographic info, citation counts, FWCI, primary topic
  authorships.csv        one row per work x author: OpenAlex author ID, ORCID, institutions
  citations_by_year.csv  one row per work x year: citations received that year
  references.csv         one row per work x referenced work
  topics.csv             one row per work x topic, with subfield/field/domain
  keywords.csv           one row per work x keyword
  abstracts.csv          reconstructed abstracts (git-ignored: publisher text)
  cache/works.jsonl      raw OpenAlex records, for any field not tabulated here

Also adds an OpenAlex_ID column to data/articles.csv and fills blank DOIs.

Usage: python code/pull_openalex.py
"""

import csv
import io
import json
import re
import urllib.parse
from pathlib import Path

from match_openalex import ARTICLES, CACHE, MAILTO, MATCHES, OUT_DIR, ROOT, get_json, title_key


def linked_dois():
    """Title_Key -> DOI, or OpenAlex work ID (W...) for works without a DOI."""
    out = {}
    for r in csv.DictReader(open(MATCHES, newline="", encoding="utf-8")):
        conf = r["Confirmed_DOI"].strip()
        if conf:
            if conf.lower() != "none":
                out[r["Title_Key"]] = conf if re.fullmatch(r"W\d+", conf) else conf.lower()
        elif r["Match_Status"] == "auto":
            if r["Candidate_DOI"]:
                out[r["Title_Key"]] = r["Candidate_DOI"].lower()
            elif r["Candidate_OpenAlex_ID"]:
                out[r["Title_Key"]] = r["Candidate_OpenAlex_ID"]
    return out


def fetch_works(keys):
    """Fetch works by DOI (50 per request) and by OpenAlex ID (free single lookups).
    Returns {doi or OpenAlex ID: work}."""
    works = {}
    for wid in sorted(k for k in set(keys) if re.fullmatch(r"W\d+", k)):
        w = get_json(f"https://api.openalex.org/works/{wid}?mailto={MAILTO}", "oa_work")
        if w:
            works[wid] = w
    dois = sorted(k for k in set(keys) if not re.fullmatch(r"W\d+", k))
    for i in range(0, len(dois), 50):
        chunk = dois[i:i + 50]
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "filter": "doi:" + "|".join(chunk), "per-page": 50, "mailto": MAILTO,
        })
        for w in (get_json(url, "oa_works") or {}).get("results", []):
            doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            works[doi] = w
    return works


def abstract(inv):
    if not inv:
        return ""
    pos = {p: word for word, ps in inv.items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))


def short(oa_id):
    return (oa_id or "").replace("https://openalex.org/", "")


def write(name, fields, rows):
    with open(OUT_DIR / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def tables(works):
    W, A, C, R, T, K, AB = [], [], [], [], [], [], []
    for w in works:
        wid = short(w["id"])
        src = ((w.get("primary_location") or {}).get("source") or {})
        pt = w.get("primary_topic") or {}
        cnp = w.get("citation_normalized_percentile") or {}
        W.append({
            "OpenAlex_ID": wid, "DOI": (w.get("doi") or "").replace("https://doi.org/", ""),
            "Title": w.get("title"), "Publication_Year": w.get("publication_year"),
            "Publication_Date": w.get("publication_date"), "Type": w.get("type"),
            "Language": w.get("language"), "Journal": src.get("display_name"),
            "Journal_OpenAlex_ID": short(src.get("id")), "ISSN_L": src.get("issn_l"),
            "Volume": (w.get("biblio") or {}).get("volume"), "Issue": (w.get("biblio") or {}).get("issue"),
            "Cited_By_Count": w.get("cited_by_count"), "FWCI": w.get("fwci"),
            "Citation_Percentile": cnp.get("value"), "Is_Top_1pct": cnp.get("is_in_top_1_percent"),
            "Is_Top_10pct": cnp.get("is_in_top_10_percent"),
            "Referenced_Works_Count": w.get("referenced_works_count"),
            "Author_Count": len(w.get("authorships") or []),
            "Countries_Distinct_Count": w.get("countries_distinct_count"),
            "Institutions_Distinct_Count": w.get("institutions_distinct_count"),
            "Primary_Topic": pt.get("display_name"),
            "Primary_Subfield": (pt.get("subfield") or {}).get("display_name"),
            "Primary_Field": (pt.get("field") or {}).get("display_name"),
            "Primary_Domain": (pt.get("domain") or {}).get("display_name"),
            "OA_Status": (w.get("open_access") or {}).get("oa_status"),
            "Has_Abstract": int(bool(w.get("abstract_inverted_index"))),
            "Is_Retracted": w.get("is_retracted"), "Updated_Date": w.get("updated_date"),
        })
        for n, a in enumerate(w.get("authorships") or [], 1):
            insts = a.get("institutions") or []
            A.append({
                "OpenAlex_ID": wid, "Author_Order": n, "Author_Position": a.get("author_position"),
                "Author_OpenAlex_ID": short((a.get("author") or {}).get("id")),
                "Author_Name": (a.get("author") or {}).get("display_name"),
                "Raw_Author_Name": a.get("raw_author_name"),
                "ORCID": ((a.get("author") or {}).get("orcid") or "").replace("https://orcid.org/", ""),
                "Is_Corresponding": a.get("is_corresponding"),
                "Institutions": "; ".join(i.get("display_name") or "" for i in insts),
                "Institution_IDs": "; ".join(short(i.get("id")) for i in insts),
                "Countries": "; ".join(a.get("countries") or []),
            })
        for c in w.get("counts_by_year") or []:
            C.append({"OpenAlex_ID": wid, "Year": c["year"], "Cited_By_Count": c["cited_by_count"]})
        for ref in w.get("referenced_works") or []:
            R.append({"OpenAlex_ID": wid, "Referenced_Work": short(ref)})
        for t in w.get("topics") or []:
            T.append({
                "OpenAlex_ID": wid, "Topic": t.get("display_name"), "Score": t.get("score"),
                "Subfield": (t.get("subfield") or {}).get("display_name"),
                "Field": (t.get("field") or {}).get("display_name"),
                "Domain": (t.get("domain") or {}).get("display_name"),
            })
        for k in w.get("keywords") or []:
            K.append({"OpenAlex_ID": wid, "Keyword": k.get("display_name"), "Score": k.get("score")})
        AB.append({"OpenAlex_ID": wid, "Abstract": abstract(w.get("abstract_inverted_index"))})

    write("works.csv", list(W[0]), W)
    write("authorships.csv", list(A[0]), A)
    write("citations_by_year.csv", ["OpenAlex_ID", "Year", "Cited_By_Count"], C)
    write("references.csv", ["OpenAlex_ID", "Referenced_Work"], R)
    write("topics.csv", ["OpenAlex_ID", "Topic", "Score", "Subfield", "Field", "Domain"], T)
    write("keywords.csv", ["OpenAlex_ID", "Keyword", "Score"], K)
    write("abstracts.csv", ["OpenAlex_ID", "Abstract"], AB)


def update_articles(key_to_doi, works):
    """Add OpenAlex_ID after DOI and fill blank DOIs, editing only those cells."""
    raw = open(ARTICLES, newline="", encoding="utf-8").read()
    rows = list(csv.reader(io.StringIO(raw)))
    header = rows[0]
    if "OpenAlex_ID" not in header:
        at = header.index("DOI") + 1
        for r in rows:
            r.insert(at, "")
        header[at] = "OpenAlex_ID"
    ix = {c: i for i, c in enumerate(header)}
    linked = filled = 0
    for r in rows[1:]:
        doi = key_to_doi.get(title_key(r[ix["Title"]]))
        w = works.get(doi) if doi else None
        r[ix["OpenAlex_ID"]] = short(w["id"]) if w else ""
        if doi and not doi.startswith("W") and not r[ix["DOI"]].strip():
            r[ix["DOI"]] = doi
            filled += 1
        linked += bool(w)
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n" if "\r\n" in raw else "\n").writerows(rows)
    open(ARTICLES, "w", newline="", encoding="utf-8").write(buf.getvalue())
    print(f"  articles.csv: {linked}/{len(rows) - 1} rows linked to OpenAlex; {filled} DOIs filled")


def main():
    key_to_doi = linked_dois()
    print(f"{len(key_to_doi)} article titles linked; fetching from OpenAlex...")
    works = fetch_works(key_to_doi.values())
    missing = sorted(set(key_to_doi.values()) - set(works))
    print(f"  {len(works)} found in OpenAlex; {len(missing)} DOIs not in OpenAlex")
    unique = {w["id"]: w for w in works.values()}
    with open(CACHE / "works.jsonl", "w", encoding="utf-8") as f:
        for w in unique.values():
            f.write(json.dumps(w) + "\n")
    tables(list(unique.values()))
    update_articles(key_to_doi, works)
    if missing:
        (OUT_DIR / "dois_not_in_openalex.txt").write_text("\n".join(missing) + "\n")


if __name__ == "__main__":
    main()
