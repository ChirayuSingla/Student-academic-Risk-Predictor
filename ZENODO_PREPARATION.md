# Zenodo archival preparation

No deposit, public release or DOI was created. The intended version is v1.0.0. `publication/final/zenodo-metadata-preparation.json` is a preparation file, not an automatically consumed `.zenodo.json`: it intentionally omits an unapproved licence and DOI. `CITATION.cff` is the citation source; no competing root `.zenodo.json` is installed.

After author approval: (1) approve the code licence and confirm author names/ORCIDs, manuscript declarations and third-party template rights; (2) approve and publish the v1.0.0 tag/release from the reviewed commit using Repository_Release_Notes.md; (3) sign into Zenodo with GitHub, open Settings > GitHub and enable ChirayuSingla/Student-academic-Risk-Predictor before publishing the release; (4) wait for Zenodo processing, inspect its metadata and archival result; (5) copy only the DOI actually issued to CITATION.cff, README and the manuscript availability statement, distinguishing the version DOI from the concept DOI. If the GitHub release predates integration, use Zenodo's supported manual upload route rather than assuming automatic archival.

Validate CFF using `cffconvert --validate` in a separate tools environment. Assign the approved licence before archival. Do not add a date-released or released version until publication occurs. This task's local validation record is in publication/final/citation_validation.json.

Official instructions checked 2 November 2026: https://help.zenodo.org/docs/github/ ; https://help.zenodo.org/docs/github/describe-software/citation-file/ ; https://help.zenodo.org/docs/github/archive-software/github-upload/ . IEEE submission checklist: https://ieeeaccess.ieee.org/authors/submission-guidelines/ .
