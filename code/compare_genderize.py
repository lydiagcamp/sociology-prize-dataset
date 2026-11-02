"""
compare_genderize.py
Compare the gender codes in data/articles.csv with the genderize.io rerun and,
where supplied, the original lookup and manual-review files. Read-only with
respect to articles.csv.

Set GENDER_ORIGINAL_DIR to the folder holding gender_lookup.csv and
gender_review_needed.csv.

Output: data/genderize/genderize_comparison.csv
    One row per author name in articles.csv.
"""

import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_CSV = ROOT / "data" / "articles.csv"
RERUN_CSV = ROOT / "data" / "genderize" / "genderize_rerun.csv"
OUTPUT_CSV = ROOT / "data" / "genderize" / "genderize_comparison.csv"
ORIG_DIR = Path(os.environ["GENDER_ORIGINAL_DIR"])


def token(author):
    return re.sub(r"[^A-Za-z\-]", "", author.split()[0])


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


rerun = {r["First_Name"]: r for r in read(RERUN_CSV)}
orig = {r["First_Name"]: r for r in read(ORIG_DIR / "gender_lookup.csv")}
review = {}
for r in read(ORIG_DIR / "gender_review_needed.csv"):
    review[(r["_Anchor_First_Name"], r["Last_Name"])] = r["Confirmed_Gender"].strip()

code, rows, corrected = {}, Counter(), set()
for r in read(ARTICLES_CSV):
    for i in range(1, 10):
        a = r[f"Author_{i}"].strip()
        if a:
            code[a] = r[f"Author_{i}_Gender"].strip()
            rows[a] += 1
            if f"{a} gender code corrected" in r["Notes"]:
                corrected.add(a)

out = []
for a, c in sorted(code.items()):
    t = token(a)
    rr = rerun.get(t, {})
    oo = orig.get(t, {})
    conf = review.get((t, a.split()[-1]), "")
    out.append(
        {
            "Author": a,
            "First_Name": t,
            "Author_Slots": rows[a],
            "Main_Code": c,
            "Rerun_Gender": rr.get("Gender", ""),
            "Rerun_Probability": rr.get("Probability", ""),
            "Rerun_Count": rr.get("Count", ""),
            "Rerun_Needs_Review": rr.get("Needs_Review", ""),
            "Original_Gender": oo.get("Gender", ""),
            "Original_Probability": oo.get("Probability", ""),
            "Original_Count": oo.get("Count", ""),
            "Original_Needs_Review": oo.get("Needs_Review", ""),
            "Original_Manual_Code": conf,
            "Corrected_In_Review": a in corrected,
            "Main_Matches_Rerun": c == rr.get("Gender", ""),
        }
    )
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)


def pct(rs, weight=False):
    n = sum(int(r["Author_Slots"]) if weight else 1 for r in rs)
    m = sum((int(r["Author_Slots"]) if weight else 1) for r in rs if r["Main_Matches_Rerun"])
    return f"{m}/{n} = {100 * m / n:.1f}%" if n else "0"


ok = [r for r in out if r["Rerun_Needs_Review"] == "False"]
flag = [r for r in out if r["Rerun_Needs_Review"] != "False"]
print("names", len(out), "| all:", pct(out), "| by author slot:", pct(out, True))
print("above thresholds:", pct(ok), "| by slot:", pct(ok, True))
print("flagged:", pct(flag), "| by slot:", pct(flag, True))
print("main codes", Counter(r["Main_Code"] for r in out))
print("no rerun token", [r["Author"] for r in out if not r["First_Name"] or r["First_Name"] not in rerun])

both = [n for n in rerun if n in orig]
print("first names rerun", len(rerun), "orig", len(orig), "both", len(both), "new", sorted(set(rerun) - set(orig)))
print("rerun==orig gender", sum(rerun[n]["Gender"] == orig[n]["Gender"] for n in both), "| same review status", sum(rerun[n]["Needs_Review"] == orig[n]["Needs_Review"] for n in both))
print("gender differs", [(n, orig[n]["Gender"], orig[n]["Probability"], rerun[n]["Gender"], rerun[n]["Probability"]) for n in both if rerun[n]["Gender"] != orig[n]["Gender"]])
print("status differs", [(n, orig[n]["Probability"], orig[n]["Count"], rerun[n]["Probability"], rerun[n]["Count"]) for n in both if rerun[n]["Needs_Review"] != orig[n]["Needs_Review"]])

print("\n--- ABOVE THRESHOLDS, main != rerun")
cat = defaultdict(list)
for r in ok:
    if not r["Main_Matches_Rerun"]:
        k = "corrected_in_review" if r["Corrected_In_Review"] else "manual_in_original" if r["Original_Manual_Code"] else "unexplained"
        cat[k].append((r["Author"], r["Main_Code"], r["Rerun_Gender"], r["Rerun_Probability"], r["Rerun_Count"], r["Original_Probability"], r["Original_Manual_Code"], r["Original_Needs_Review"]))
for k, v in cat.items():
    print(k, len(v))
    for x in v:
        print("  ", x)
print("\n--- FLAGGED, main != rerun")
for r in flag:
    if not r["Main_Matches_Rerun"]:
        print("  ", r["Author"], r["Main_Code"], r["Rerun_Gender"], r["Rerun_Probability"], r["Rerun_Count"], "| manual:", r["Original_Manual_Code"], "| corrected:", r["Corrected_In_Review"])
print("\nflagged with no manual record", sum(1 for r in flag if not r["Original_Manual_Code"] and not r["Corrected_In_Review"]))
print([ (r["Author"],r["Main_Code"]) for r in flag if not r["Original_Manual_Code"] and not r["Corrected_In_Review"]])
