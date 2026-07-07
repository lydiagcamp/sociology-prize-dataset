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

## Gender coding methodology

Author gender was coded using a combination of algorithmic prediction and manual verification. First names were submitted to the [genderize.io](https://genderize.io) API, which returns a predicted gender, a probability, and a count of historical name-registry records the prediction is based on. Any name with a prediction probability below 0.90 or a supporting count below 20 (197 of 862 unique first-name tokens) was flagged for manual review rather than coded automatically.

For each flagged person, gender was determined through manual research — personal or faculty websites, Google Scholar profiles, published bios, and third-party writing (interviews, news coverage, profiles) — and coded based on self-identified pronouns or third-person description by others, rather than inferred from the name alone. Where a source used multiple pronouns together (e.g. "they/she"), the first one listed was used. A subset of flagged cases (22 individuals) were listed only by initials in the original award text and required identifying the person's full name before gender research could begin. Where no reliable identifying information could be found (7 individuals), gender was coded `unknown` rather than guessed.

This process should be read with some caution: predicting or coding gender from first names — whether by an algorithm or by a researcher inferring from a name, photo, or writing style — risks imposing a binary, essentialist category onto individuals whose gender identity may not be legible from public records, and both genderize.io's training data and manual inference can reproduce cultural and linguistic biases about which names "count" as male or female. Using third-person description and self-identified pronouns where available was an attempt to mitigate this, but does not eliminate the underlying problem that gender is being inferred by an outside observer rather than reported by the subject.

## Known limitations

- `Primary_Method` is not yet populated.
- Book prizes and student-paper awards (e.g. ASA Ronald Burt Outstanding Student Paper Award) are intentionally excluded — this dataset covers article prizes for established scholars only. Where a single prize alternated between honoring a book and an article across different years, only article years were retained.
