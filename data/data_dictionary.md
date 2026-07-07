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

## Gender Coding Process

Author gender was coded using a combination of algorithmic prediction and manual verification. Author first names were submitted to the genderize.io API, which returns a predicted gender, a probability, and a supporting count from historical name registries. Out of 1,569 unique authors, there were 862 unique first-name tokens in the dataset. Using these first name tokens, names with probability below 0.90 or count below 20 was flagged for manual review, since low-probability or low-count predictions aren't reliable enough to code automatically. This flagged 197 individuals.

For each flagged person, gender was determined through manual research rather than the algorithmic guess: searching for personal or faculty websites, Google Scholar profiles, published bios, and third-party writing (interviews, news coverage, profiles), coding gender based on self-identified pronouns or third-person description by others rather than inferring from the name alone. When multiple pronouns appeared together (e.g., "they/she"), the first-listed pronoun was used to assign gender. Where no reliable identifying information could be found after this search — 7 individuals — gender was coded as unknown rather than guessed. For simplicity's sake, gender was coded as `male`, `female`, `nonbinary`, and `unknown`.

This process should be read with some caution. Predicting or coding gender from names risks the imposition of a binary, essentialist category onto individuals whose gender identity may not be legible from public records. Similarly, genderize.io's training data can reproduce cultural and linguistic biases about which names "count" as male or female. Prioritizing third-person description and self-identified pronouns over name-based guessing for uncertain names was an attempt to mitigate this bias, but doesn't eliminate the underlying problem that gender is being inferred by an outside observer rather than reported by the subject.

## Known limitations

- `Primary_Method` is not yet populated.
- Book prizes and student-paper awards (e.g. ASA Ronald Burt Outstanding Student Paper Award) are intentionally excluded — this dataset covers article prizes for established scholars only. Where a single prize alternated between honoring a book and an article across different years, only article years were retained.
