"""
rerun_genderize.py
Re-query genderize.io for every first name in data/articles.csv and write the
scores to data/genderize/. Read-only with respect to articles.csv.

The first name is extracted the same way as the original coding run: the first
word of the author name, keeping only letters and hyphens. Raw responses are
cached so a re-run does not spend quota on a name already looked up.

Requires GENDERIZE_API_KEY in the environment or in the .env named by GENDERIZE_ENV.

Output: data/genderize/genderize_rerun.csv
    First_Name, Gender, Probability, Count, Needs_Review
    Needs_Review is True when probability < 0.90 or count < 20, or when the name
    returned no result.
"""

import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_CSV = ROOT / "data" / "articles.csv"
OUT_DIR = ROOT / "data" / "genderize"
CACHE_DIR = OUT_DIR / "cache"
OUTPUT_CSV = OUT_DIR / "genderize_rerun.csv"

BATCH_SIZE = 10
PROBABILITY_THRESHOLD = 0.90
COUNT_THRESHOLD = 20


def load_api_key():
    key = os.environ.get("GENDERIZE_API_KEY")
    if key:
        return key
    for line in Path(os.environ["GENDERIZE_ENV"]).read_text().splitlines():
        if line.startswith("GENDERIZE_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("GENDERIZE_API_KEY not found")


def first_name_token(author):
    return re.sub(r"[^A-Za-z\-]", "", author.split()[0])


def first_names():
    names = set()
    with open(ARTICLES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for i in range(1, 10):
                author = (row.get(f"Author_{i}") or "").strip()
                if author and first_name_token(author):
                    names.add(first_name_token(author))
    return names


def cache_path(name):
    return CACHE_DIR / f"{name}.json"


def fetch_batch(names, key):
    params = [("apikey", key)] + [("name[]", n) for n in names]
    url = "https://api.genderize.io?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        remaining = resp.headers.get("x-rate-limit-remaining")
        return json.load(resp), remaining


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    names = sorted(first_names())
    todo = [n for n in names if not cache_path(n).exists()]
    print(f"{len(names)} first names, {len(todo)} to fetch")
    if todo:
        key = load_api_key()
        for i in range(0, len(todo), BATCH_SIZE):
            batch = todo[i : i + BATCH_SIZE]
            results, remaining = fetch_batch(batch, key)
            for name, result in zip(batch, results):
                cache_path(name).write_text(json.dumps(result))
            print(f"fetched {i + len(batch)}/{len(todo)}, quota remaining {remaining}", flush=True)
            time.sleep(0.25)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["First_Name", "Gender", "Probability", "Count", "Needs_Review"])
        for name in names:
            r = json.loads(cache_path(name).read_text())
            needs = (
                r.get("gender") is None
                or (r.get("probability") or 0) < PROBABILITY_THRESHOLD
                or (r.get("count") or 0) < COUNT_THRESHOLD
            )
            w.writerow([name, r.get("gender") or "", r.get("probability"), r.get("count"), needs])


if __name__ == "__main__":
    main()
