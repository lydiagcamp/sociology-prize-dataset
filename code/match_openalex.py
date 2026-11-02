"""Match each unique article in data/articles.csv to a DOI and OpenAlex work.

Matching order:
  1. Existing DOI in articles.csv
  2. Crossref bibliographic search (free, no rate cap)
  3. OpenAlex title search, only for articles Crossref could not match
     (OpenAlex charges 10 credits per search, so this is the fallback)

Each candidate is scored on title similarity, year difference, first-author
surname, and journal. Output: data/openalex/article_matches.csv, one row per
unique article, with Match_Status = auto | review | none. To accept or fix a
"review" row, fill in Confirmed_DOI with a DOI or an OpenAlex work ID (W...),
or write "none" to reject it, and rerun; confirmed values are kept across reruns.

Usage: python code/match_openalex.py
"""

import csv
import difflib
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "data" / "articles.csv"
OUT_DIR = ROOT / "data" / "openalex"
CACHE = OUT_DIR / "cache"
MATCHES = OUT_DIR / "article_matches.csv"
MAILTO = "lydia.cp02@gmail.com"

FIELDS = [
    "Title_Key", "Title", "Author_1", "Year_Published", "Journal", "N_Prize_Rows",
    "Match_Status", "Match_Source", "Title_Sim", "Year_Diff", "Author_Match", "Journal_Sim",
    "Candidate_DOI", "Candidate_OpenAlex_ID", "Candidate_Title", "Candidate_Year", "Candidate_Journal",
    "Confirmed_DOI",
]


def ascii_lower(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def title_key(t):
    t = ascii_lower(t).replace("&", " and ")
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def surname(name):
    parts = [p for p in re.split(r"\s+", ascii_lower(name).replace(".", " ").replace(",", " ")) if p]
    while parts and parts[-1] in {"jr", "sr", "ii", "iii", "iv"}:
        parts.pop()
    return parts[-1] if parts else ""


def main_title_sim(a, b):
    ma, mb = title_key(a.split(":")[0]), title_key(b.split(":")[0])
    return difflib.SequenceMatcher(None, ma, mb).ratio() if ma and mb else 0.0


def title_sim(a, b):
    full = difflib.SequenceMatcher(None, title_key(a), title_key(b)).ratio()
    # Award pages often drop subtitles; count a strong main-title match, slightly discounted.
    return max(full, 0.95 * main_title_sim(a, b))


def get_json(url, tag):
    """GET with an on-disk cache so reruns cost nothing."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{tag}_{hashlib.sha1(url.encode()).hexdigest()}.json"
    if f.exists():
        return json.loads(f.read_text())
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"sociology-prize-dataset (mailto:{MAILTO})"})
            data = json.load(urllib.request.urlopen(req, timeout=30))
            f.write_text(json.dumps(data))
            time.sleep(0.25)  # stay under Crossref's public rate limit
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", "60"))
                print(f"  rate limited; waiting {wait}s", file=sys.stderr)
                time.sleep(min(wait, 600))
            elif e.code == 404:
                return None
            else:
                print(f"  HTTP {e.code} (attempt {attempt + 1}): {url[:120]}", file=sys.stderr, flush=True)
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"  {type(e).__name__} (attempt {attempt + 1}): {url[:120]}", file=sys.stderr, flush=True)
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed: {url}")


def load_articles():
    rows = list(csv.DictReader(open(ARTICLES, newline="", encoding="utf-8")))
    groups = defaultdict(list)
    for r in rows:
        groups[title_key(r["Title"])].append(r)
    arts = []
    for k, rs in groups.items():
        years = Counter(r["Year_Published"].split(".")[0] for r in rs if r["Year_Published"])
        journals = Counter(r["Journal"] for r in rs if r["Journal"])
        dois = [r["DOI"].strip() for r in rs if r["DOI"].strip()]
        arts.append({
            "Title_Key": k, "Title": rs[0]["Title"], "Author_1": rs[0]["Author_1"],
            "Year_Published": years.most_common(1)[0][0] if years else "",
            "Journal": journals.most_common(1)[0][0] if journals else "",
            "N_Prize_Rows": len(rs), "DOI": dois[0] if dois else "",
        })
    return arts


def score(art, cand):
    ts = title_sim(art["Title"], cand["title"])
    yd = ""
    if art["Year_Published"] and cand["years"]:
        yd = min(abs(int(art["Year_Published"]) - y) for y in cand["years"])
    am = surname(art["Author_1"]) in {surname(n) for n in cand["authors"]} if art["Author_1"] else False
    js = difflib.SequenceMatcher(None, title_key(art["Journal"]), title_key(cand["journal"])).ratio() \
        if art["Journal"] and cand["journal"] else ""
    return ts, yd, am, js


def status(ts, yd, am, js):
    year_ok = yd == "" or yd <= 2
    if ts >= 0.93 and am and year_ok:
        return "auto"
    if ts >= 0.85 and am and year_ok and (js == "" or js >= 0.6):
        return "auto"
    if ts >= 0.6:
        return "review"
    return "none"


def crossref_candidates(art):
    q = f"{art['Title']} {surname(art['Author_1'])}"
    url = ("https://api.crossref.org/works?" + urllib.parse.urlencode({
        "query.bibliographic": q, "rows": 5, "mailto": MAILTO,
        "select": "DOI,title,issued,published-print,published-online,container-title,author,type",
    }))
    data = get_json(url, "crossref")
    out = []
    for it in (data or {}).get("message", {}).get("items", []):
        if it.get("type") not in {"journal-article", "proceedings-article", "book-chapter"}:
            continue
        years = {d["date-parts"][0][0] for k in ("issued", "published-print", "published-online")
                 if (d := it.get(k)) and d.get("date-parts") and d["date-parts"][0] and d["date-parts"][0][0]}
        out.append({
            "doi": it["DOI"].lower(), "title": (it.get("title") or [""])[0],
            "years": years, "journal": (it.get("container-title") or [""])[0],
            "authors": [f"{a.get('given', '')} {a.get('family', '')}" for a in it.get("author", [])],
        })
    return out


def openalex_candidates(art):
    url = ("https://api.openalex.org/works?" + urllib.parse.urlencode({
        "search": title_key(art["Title"])[:250], "per-page": 5, "mailto": MAILTO,
        "select": "id,doi,title,publication_year,primary_location,authorships",
    }))
    data = get_json(url, "oa_search")
    out = []
    for w in (data or {}).get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {})
        out.append({
            "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
            "openalex_id": w["id"], "title": w.get("title") or "",
            "years": {w["publication_year"]} if w.get("publication_year") else set(),
            "journal": src.get("display_name") or "",
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
        })
    return out


def best(art, cands, source):
    scored = []
    for c in cands:
        ts, yd, am, js = score(art, c)
        rank = ts + 0.1 * am - 0.02 * (yd if yd != "" else 0)
        scored.append((rank, ts, yd, am, js, c))
    if not scored:
        return None
    rank, ts, yd, am, js, c = max(scored, key=lambda x: x[0])
    return {
        "Match_Status": status(ts, yd, am, js), "Match_Source": source,
        "Title_Sim": round(ts, 3), "Year_Diff": yd, "Author_Match": int(am),
        "Journal_Sim": round(js, 3) if js != "" else "",
        "Candidate_DOI": c["doi"], "Candidate_OpenAlex_ID": c.get("openalex_id", "").replace("https://openalex.org/", ""),
        "Candidate_Title": c["title"],
        "Candidate_Year": "/".join(map(str, sorted(c["years"]))), "Candidate_Journal": c["journal"],
    }


_done = [0]


def match_one(art):
    _done[0] += 1
    if _done[0] % 100 == 0:
        print(f"  {_done[0]} done", flush=True)
    if art["DOI"]:
        return {"Match_Status": "auto", "Match_Source": "existing_doi", "Candidate_DOI": art["DOI"].lower()}
    return best(art, crossref_candidates(art), "crossref") or {"Match_Status": "none", "Match_Source": "crossref"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    confirmed = {}
    if MATCHES.exists():
        for r in csv.DictReader(open(MATCHES, newline="", encoding="utf-8")):
            if r.get("Confirmed_DOI", "").strip():
                confirmed[r["Title_Key"]] = r["Confirmed_DOI"].strip()

    arts = load_articles()
    print(f"{len(arts)} unique articles; matching via Crossref...")
    with ThreadPoolExecutor(max_workers=1) as ex:
        results = list(ex.map(match_one, arts))

    # OpenAlex search fallback for anything Crossref did not auto-match.
    weak = [i for i, r in enumerate(results) if r["Match_Status"] != "auto"]
    print(f"{len(weak)} not auto-matched by Crossref; trying OpenAlex search...")
    for n, i in enumerate(weak, 1):
        try:
            oa = best(arts[i], openalex_candidates(arts[i]), "openalex_search")
        except RuntimeError as e:
            print(f"  skipped OpenAlex search for article {n}/{len(weak)}: {e}", file=sys.stderr)
            continue
        rank = {"auto": 2, "review": 1, "none": 0}
        if oa and (rank[oa["Match_Status"]], oa["Title_Sim"]) > (rank[results[i]["Match_Status"]], results[i].get("Title_Sim", 0)):
            results[i] = oa

    out = []
    for art, res in zip(arts, results):
        row = {k: art.get(k, "") for k in FIELDS} | res
        row["Confirmed_DOI"] = confirmed.get(art["Title_Key"], "")
        out.append(row)
    out.sort(key=lambda r: ({"review": 0, "none": 1, "auto": 2}[r["Match_Status"]], r["Title_Key"]))
    with open(MATCHES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print(Counter(r["Match_Status"] for r in out), "->", MATCHES.relative_to(ROOT))


if __name__ == "__main__":
    main()
