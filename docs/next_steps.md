# Next Steps

Open items after the data review of November 2, 2026.

## Sample

- **Prize eligibility:** check the rules of the other 54 prizes for student-only awards. `Selection_Criteria_Text` is blank in `awards.csv`. This is the main remaining risk to the sample's definition.
- **Ethnomethodology prize:** look up the 2025 and 2026 winners.
- **Acosta/Braun:** settle whether the entry is a winner or an honorable mention.
- **Red Unions:** the political sociology page's 1992 "book award" entry was not added.
- **Books dropped:** the percentage cannot come from `dropped_rows.csv`, which holds one book. It requires counting book winners from the award pages of mixed prizes.

## Articles

- **Mueller, *Producing Colorblindness*:** `Year_Published` 2017 comes from the erratum (online April 2017). Check the article's Oxford Academic page, which would also give its DOI. Use the earlier year if it first appeared online in 2016.
- **Partly verified citations:** Silver (*Review* 1995) and Facio (*Global Development Studies* 1998) rest on limited sources, recorded in `Notes`.

## Documentation and outputs

- **`gender_dynamics_report.html`:** uses old numbers. Needs a full rerun before any figure is used. Not committed.
- **README:** reconsider the "major European prizes" wording. "Spanning 1980-2026" describes years won; years published run 1977-2025.
- **Title punctuation:** most titles omit commas and 45 still have them, some with a stray end period or long dash. Left as is by decision on November 2, 2026.
- **`genderize_rerun.csv`:** 14 first names are no longer used in `articles.csv`. Left in place and noted in the data dictionary.
- **`Primary_Method`:** not yet coded.
