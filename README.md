# Sociology Prize Dataset

An original dataset of sociology article prizes and their winning articles, built to study what the discipline of sociology recognizes as innovative work.

## Contents

- **1,262 prize-winning articles**, spanning 1980-2026
- **62 distinct awards**, drawn from more than fifty American Sociological Association (ASA) sections plus major European prizes (European Sociological Review Prize, BSA/SAGE Prizes, SASE/Socio-Economic Review Best Article Prize)
- 54 unique subfields represented
- 1,148 ASA-sponsored awards, 114 non-ASA (European/other) awards

## Files

| File | Description |
|---|---|
| `data/articles.csv` | One row per prize-winning article: title, authors, gender codes, year, journal, DOI, and award linkage |
| `data/awards.csv` | One row per award/prize: name, sponsoring body, subfield, level, and history |
| `data/data_dictionary.md` | Column-by-column description of both tables |

## Schema notes

- The two tables join on `Award_ID`.
- `articles.csv` also carries `Award_Name` and `Subfield` directly, so the article-level table can be used on its own without a join for most purposes.
- Author names and (heuristically coded) genders are split into positional columns `Author_1`...`Author_9` / `Author_1_Gender`...`Author_9_Gender` rather than combined semicolon-delimited strings.
- `ASA` is a binary flag: `1` if the award is an ASA section award, `0` otherwise (European/SASE prizes).
- Gender codes (`m`/`f`/`u`) were assigned through manual, unvalidated first-name judgment calls and have not yet been cross-checked against a systematic name-based gender API.

## Visualizations

- **[Economic sociology co-authorship network](https://lydiagcamp.github.io/sociology-prize-dataset/viz/)** — an interactive graph of prize-winning economic sociology authors and their broader co-authorship networks, built from OpenAlex data.

## Citation

If you use this dataset, please cite it as an in-progress research project by Lydia Camp (2026).
