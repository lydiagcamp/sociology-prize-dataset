# Data Dictionary

## `articles.csv` (1,227 rows — one per article-prize pair; 1,059 unique articles)

| Column | Description |
|---|---|
| `Award_ID` | Slug identifying the award; joins to `awards.csv` |
| `Award_Name` | Full name of the award/prize |
| `Subfield` | ASA section or subfield the award belongs to |
| `Title` | Article title |
| `Author_1`...`Author_9` | Author names in order; blank if the article has fewer authors |
| `Author_1_Gender`...`Author_9_Gender` | Gender code for the corresponding author: `male`, `female`, `nonbinary`, `unknown` (researched but undeterminable), or blank |
| `Year_Won` | Year the prize was awarded |
| `Year_Published` | Year the article was first published, online or in print (the earlier of the publisher's dates) |
| `Journal` | Journal of publication, with one spelling per journal (162 distinct journals) |
| `DOI` | Digital Object Identifier, where available |
| `Prize_Type` | Award category/type as named on the award's own page (e.g. "Winner", "Best Article Award") |
| `Prize_Rank` | `Prize_Type` collapsed into three categories: `Winner`, `Honorable Mention`, `Runner-up` |
| `Author_Count` | Number of authors on the article |
| `Primary_Method` | Primary methodological approach (not yet coded; currently blank for all rows) |
| `Source_Award_Page` | URL or citation for the source used to identify the winner |
| `Notes` | Free-text notes, e.g. disambiguation or edge cases |
| `ASA` | `1` if an ASA section award, `0` otherwise (European/other) |

## `awards.csv` (59 rows — one per award/prize)

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

## `dropped_rows.csv` (35 rows — one per winner removed in data review)

Has the same columns as `articles.csv`, plus:

| Column | Description |
|---|---|
| `Drop_Category` | Why the row is out of scope: `book`, `book_chapter`, `report`, or `student_paper_award` |
| `Drop_Reason` | Why the row was removed |
| `Drop_Evidence` | Source used to establish the reason |
| `Drop_Date` | Date the row was removed |

## `dropped_awards.csv` (1 row — one per prize removed from the sample)

Has the same columns as `awards.csv`, plus `Drop_Reason` and `Drop_Date`.

## Gender coding

Gender codes (`male`/`female`/`nonbinary`/`unknown`) were assigned via a genderize.io + manual-review process. See [`docs/methodology.md`](../docs/methodology.md) for the full methodology and its limitations.

## `genderize/genderize_rerun.csv` (852 rows — one per first name)

Scores from the November 2026 genderize.io rerun. `articles.csv` was not changed by it. Fourteen first names are no longer used in `articles.csv` after later name corrections.

| Column | Description |
|---|---|
| `First_Name` | First word of the author name, letters and hyphens only |
| `Gender` | Gender predicted by genderize.io; blank if no prediction |
| `Probability` | Probability of the prediction |
| `Count` | Number of records supporting the prediction |
| `Needs_Review` | `True` if probability is below 0.90, count is below 20, or there is no prediction |

## `genderize/genderize_comparison.csv` (1,454 rows — one per author name)

Compares the code in `articles.csv` with the rerun and the original run.

| Column | Description |
|---|---|
| `Author` | Author name as written in `articles.csv` |
| `First_Name` | First name submitted to genderize.io |
| `Author_Slots` | Number of times the name appears across rows of `articles.csv` |
| `Main_Code` | Gender code in `articles.csv` |
| `Rerun_Gender`, `Rerun_Probability`, `Rerun_Count`, `Rerun_Needs_Review` | Rerun result for the first name |
| `Original_Gender`, `Original_Probability`, `Original_Count`, `Original_Needs_Review` | Original run's result for the first name; blank if the name was not in that run |
| `Original_Manual_Code` | Code from the original manual review, where the person was reviewed |
| `Corrected_In_Review` | `True` if the code was corrected in the November 2026 data review |
| `Main_Matches_Rerun` | `True` if `Main_Code` equals `Rerun_Gender` |

## Known limitations

- `Primary_Method` is not yet populated.
- Book prizes and student-paper awards (e.g. ASA Ronald Burt Outstanding Student Paper Award) are intentionally excluded; article prizes are otherwise not restricted by career stage. Where a single prize alternated between honoring a book and an article across different years, only article years were retained.
- The sample covers journal articles only. Books found in review, book chapters (including chapters in recurring book series), and reports are logged in `dropped_rows.csv`.
- Book winners excluded when the dataset was built were not stored as rows; `dropped_rows.csv` holds only the one book found later. A percentage of books dropped therefore cannot yet be computed. It requires counting book winners from the award pages of mixed prizes.
- The Reinhard Bendix Prize was removed as a graduate student paper award (24 rows). Eligibility rules for the other prizes have not all been checked, and `Selection_Criteria_Text` is blank in `awards.csv`.
- Author name variants were merged in the November 2026 data review, with each change recorded in `Notes`. The 1,454 names approximate people: a name change with no similar spelling would not have been detected, and two people sharing one exact name would be counted once.
- A few journal names are short forms of the official title (e.g. Socius, Labor), and titles and journal names generally omit commas.
