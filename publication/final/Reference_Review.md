# Final reference review

Checked 2 November 2026. `reference_verification.json` preserves current registry responses, full registered author lists, publication dates and journal metadata. All retrieved DOI-backed titles match the manuscript citations. DOI-year strings are not substituted for issue publication years; Idowu is 2024 and Pham et al. 2025. Kleter et al. pagination remains omitted because the earlier author portal and registration metadata disagree. No unverifiable pagination was added.

The original 2008 Cortez/Silva paper's handle host failed TLS certificate verification; no certificate bypass was used. The official UCI provider independently confirms its title, authors, year and conference: https://archive.ics.uci.edu/dataset/320/student+performance . The retained page range 5–12 comes from the existing bibliography and remains subject to author verification against the original paper. It is not described as newly independently verified.

The scripted OpenAI page request returned HTTP 403. Browser retrieval of https://openai.com/chatgpt/ succeeded and redirected to ChatGPT. This verifies the service page, not a particular historical model version. The AI assistance acknowledgment is retained because the paper has actually received AI assistance and IEEE requires disclosure; it is not a decorative watermark.

Primary guidance checked: https://ieeeaccess.ieee.org/authors/submission-guidelines/ . The official template download was byte-identical to the retained reference; see template_verification.json. Zenodo preparation follows https://help.zenodo.org/docs/github/describe-software/citation-file/ and https://help.zenodo.org/docs/github/archive-software/github-upload/ .

Registry responses do not guarantee that no correction or retraction exists. The records retain any returned update links, but final author review of publisher notices and full-text relevance is still required. This task did not perform a systematic literature review or claim that every bibliography field was independently confirmed from full text.
