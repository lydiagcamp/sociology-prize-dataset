# Sociology Prize Dataset

An original dataset of sociology article prizes and their winning articles, built to study what the discipline of sociology recognizes as innovative work.

[![View the economic sociology co-authorship network](https://img.shields.io/badge/View%20the%20co--authorship%20network-%E2%86%92-7b1e2b?style=for-the-badge)](https://lydiagcamp.github.io/sociology-prize-dataset/viz/)

## Contents

- **1,262 prize-winning articles**, spanning 1980-2026
- **1,569 unique authors**
- **62 distinct awards**, drawn from more than fifty American Sociological Association (ASA) sections plus major European prizes (European Sociological Review Prize, BSA/SAGE Prizes, SASE/Socio-Economic Review Best Article Prize)
- 54 unique subfields represented
- 1,148 ASA-sponsored awards, 114 non-ASA (European/other) awards

## Files

| File | Description |
|---|---|
| [`data/articles.csv`](data/articles.csv) | One row per prize-winning article: title, authors, gender codes, year, journal, DOI, and award linkage |
| [`data/awards.csv`](data/awards.csv) | One row per award/prize: name, sponsoring body, subfield, level, and history |
| [`data/data_dictionary.md`](data/data_dictionary.md) | Column-by-column description of both tables |
| [`docs/methodology.md`](docs/methodology.md) | Methodology and limitations |

## Visualizations

- **[Economic sociology co-authorship network](https://lydiagcamp.github.io/sociology-prize-dataset/viz/)** — an interactive graph of prize-winning economic sociology authors and their broader co-authorship networks, built from OpenAlex data. This currently covers only the ASA Economic Sociology Section as a worked example, not the full dataset.

## Citation

If you use this dataset, please cite it as an in-progress research project by [Lydia Camp](https://lydiagcamp.github.io) (2026).
