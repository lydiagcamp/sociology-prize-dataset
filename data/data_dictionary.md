# Data Dictionary

## `articles.csv` (1,262 rows — one per prize-winning article)

| Column | Description |
|---|---|
| `Award_ID` | Slug identifying the award; joins to `awards.csv` |
| `Award_Name` | Full name of the award/prize |
| `Subfield` | ASA section or subfield the award belongs to |
| `Title` | Article title |
| `Author_1`...`Author_9` | Author names in order; blank if the article has fewer authors |
| `Author_1_Gender`...`Author_9_Gender` | Gender code for the corresponding author: `male`, `female`, `nonbinary`, `unknown` (researched but undeterminable), or blank |
| `Year_Won` | Year the prize was awarded |
| `Year_Published` | Year the article was originally published |
| `Journal` | Journal of publication |
| `DOI` | Digital Object Identifier, where available |
| `Prize_Type` | Award category/type as named on the award's own page (e.g. "Winner", "Best Article Award") |
| `Author_Count` | Number of authors on the article |
| `Primary_Method` | Primary methodological approach (not yet coded; currently blank for all rows) |
| `Source_Award_Page` | URL or citation for the source used to identify the winner |
| `Notes` | Free-text notes, e.g. disambiguation or edge cases |
| `ASA` | `1` if an ASA section award, `0` otherwise (European/other) |

## `awards.csv` (62 rows — one per award/prize)

| Column | Description |
|---|---|
| `Award_ID` | Slug identifying the award; primary key |
| `Award_Name` | Full name of the award/prize |
| `Sponsoring_Body` | Organization that sponsors the award |
| `Subfield` | ASA section or subfield the award belongs to |
| `Level` | Award level/scope (e.g. section-level, association-level) |
| `First_Year_Given` | First year the award was given |
| `Frequency` | How often the award is given (e.g. annual, biennial) |
| `Source_URL` | URL for the award's official page |
| `Selection_Criteria_Text` | Free text describing selection criteria, where available |
| `Notes` | Free-text notes |
| `ASA` | `1` if an ASA section award, `0` otherwise (European/other) |

## Gender coding

Gender codes (`male`/`female`/`nonbinary`/`unknown`) were assigned via a genderize.io + manual-review process. See [`docs/methodology.md`](../docs/methodology.md) for the full methodology and its limitations.

## Known limitations

- `Primary_Method` is not yet populated.
- Book prizes and student-paper awards (e.g. ASA Ronald Burt Outstanding Student Paper Award) are intentionally excluded — this dataset covers article prizes for established scholars only. Where a single prize alternated between honoring a book and an article across different years, only article years were retained.
