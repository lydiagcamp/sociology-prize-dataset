# Sociology Prize Dataset

An original dataset of sociology article prizes and their winning articles, built to study what the discipline of sociology recognizes as innovative work.

## Contents

- **1,227 article-prize records** covering **1,059 unique published articles**, spanning 1980-2026
- **1,454 unique author names**
- **59 distinct awards**, drawn from more than fifty American Sociological Association (ASA) sections plus major European prizes (European Sociological Review Prize, BSA/SAGE Prizes, SASE/Socio-Economic Review Best Article Prize)
- 54 unique subfields represented
- 1,113 records from ASA-sponsored awards, 114 from non-ASA (European/other) awards

## Files

| File | Description |
|---|---|
| [`data/articles.csv`](data/articles.csv) | One row per article-prize pair: title, authors, gender codes, year, journal, DOI, and award linkage |
| [`data/awards.csv`](data/awards.csv) | One row per award/prize: name, sponsoring body, subfield, level, and history |
| [`data/dropped_rows.csv`](data/dropped_rows.csv) | Winners removed in data review because they are not journal articles or won a student paper award, with reason and evidence |
| [`data/dropped_awards.csv`](data/dropped_awards.csv) | Prizes removed from the sample, with reason |
| [`data/genderize/`](data/genderize/) | genderize.io scores for each first name, and a comparison with the gender codes in `articles.csv` |
| [`data/data_dictionary.md`](data/data_dictionary.md) | Column-by-column description of the tables |
| [`docs/methodology.md`](docs/methodology.md) | Methodology and limitations |

## Citation

If you use this dataset, please cite it as an in-progress research project by [Lydia Camp](https://lydiagcamp.github.io) (2026).
