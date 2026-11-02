# Reference verification record

Checked 1 November 2026. The update is a focused literature search, not a systematic review. DOI registration metadata and official publisher/repository pages were used; no bibliographic field was inferred from an AI-generated citation. Full returned DOI metadata are in review/reference_metadata.json. An HTTP 429 denotes registry throttling, not an invalid DOI; UCI uses DataCite rather than Crossref.

## New literature used

- Boujmiraz, Darhmaoui and Drissi el maliani, 2026: DOI 10.1016/j.caeai.2026.100548; publisher abstract and Crossref agree on title, authors, year, volume 10 and article 100548. Supports the established breadth of ML and XAI work, not a claim of superiority for our models.
- Santos and Henriques, 2023: DOI 10.1016/j.caeai.2023.100175; publisher abstract and Crossref verified. Supports evaluation at course-completion cutoffs.
- Kleter, Matzat and Conijn, 2024: DOI 10.1109/TLT.2024.3443079; official author-institution page and Crossref verified. Page ranges conflict: the author portal reports 2183-2194 while registry metadata report 2129-2140. Pagination is deliberately omitted from the manuscript citation rather than guessed.
- Gunasekara and Saarela, 2025: DOI 10.1109/ACCESS.2025.3643645; IEEE publication metadata and Crossref verified, volume 13, pages 214387-214408. The review identifies a shortage of quantified explanation evaluation.
- Idowu, 2024: DOI 10.1007/s40593-023-00389-4; Springer official article and Crossref verified. The DOI year 2023 differs from the final volume publication year 2024; citation uses the final volume year.
- Pham, Pham Ngoc and Nguyen-Duc, 2025: DOI 10.1016/j.jss.2024.112244; official publisher search record and Crossref verified, volume 219, article 112244. DOI year 2024 is not the issue year.

## Original references audited

The original numbering below refers to the supplied PDF; the revised bibliography is renumbered by first appearance. Foundational citations were not labeled obsolete solely because they are old. Removed references are generally valid but no longer necessary for the focused manuscript.

| Original | Verification and decision |

|---|---|

| [1] Romero and Ventura | Crossref metadata matched; Valid survey; replaced with more recent focused reviews. |

| [2] Cortez dataset | Verified on UCI official page, CC BY 4.0; retained. |

| [3] Ewais et al. | Verified on Scientific Reports official page, 24 April 2026, vol. 16, article 19944; retained. Six regression models, not our binary task. |

| [4] Kapoor and Narayanan | Crossref metadata matched; Retained leakage reference. |

| [5] Cortez and Silva | Title/authors/year and conference verified through UCI source attribution. Repository link retained. No claimed fresh full-text review; page range retained from supplied bibliography. |

| [6] Marbouti et al. | Crossref metadata matched; Valid; replaced with recent explicitly cutoff-based work. |

| [7] Altman and Royston | Verified BMJ official PDF and author archive; not needed in focused bibliography. |

| [8] Rudin | Crossref metadata matched; Retained interpretability motivation. |

| [9] Khosravi et al. | Crossref metadata matched; Retained education stakeholder context. |

| [10] Cawley and Talbot | Verified on JMLR official page, vol. 11, pages 2079-2107; retained. |

| [11] Pedregosa et al. | Verified on JMLR official page, vol. 12, pages 2825-2830; retained. |

| [12] He and Garcia | Crossref metadata matched; Retained weighting/imbalance context; no claim that weighting improves fairness. |

| [13] Fawcett | Crossref metadata matched; Valid; removed to reduce redundant metric citations. |

| [14] Saito and Rehmsmeier | Crossref metadata matched; Retained precision-recall context. |

| [15] Brier | Crossref metadata matched; Retained original probability-error definition. |

| [16] Hosmer et al. | Crossref metadata matched; Verified title, authors and 2013 date; retained third-edition reference from supplied manuscript. |

| [17] Breiman et al. | 1984 book citation consistent with supplied source; not independently verified against a publisher copy here and not retained. This is not classified as fabricated. |

| [18] Harris et al. | Crossref metadata matched; Valid software citation; environment versions recorded separately instead. |

| [19] McKinney | Crossref metadata matched; Valid software citation; omitted to focus bibliography. |

| [20] Hunter | Crossref metadata matched; Valid software citation; omitted to focus bibliography. |

| [21] Strobl et al. | Crossref metadata matched; Retained importance-bias caution. |

| [22] Shmueli | Verified official Statistical Science PDF, title and author; retained prediction/causation distinction. |

| [23] Streamlit | Verified official https://docs.streamlit.io; retained and access date updated. |

| [24] Joblib | Software implementation inspected; documentation URL is plausible but not independently browsed; citation removed. |

| [25] Slade and Prinsloo | Crossref metadata matched; Valid; registry splits title and subtitle. Replaced with recent fairness sources. |

| [26] Drachsler and Greller | Crossref metadata matched; Valid; registry splits title/subtitle. Omitted in focused bibliography. |

| [27] Baker and Hawn | Crossref metadata matched; Verified final 2022 volume despite DOI 2021; retained. |

## Additional source checks

OULAD: official Scientific Data article/PDF, DOI 10.1038/sdata.2017.171, confirms J. Kuzilek, M. Hlosta and Z. Zdrahal, volume 4, article 170171, CC BY 4.0. It is proposed as a separate temporal benchmark, not used for an executed external validation. UCI repository is cited as the dataset authority. OpenAI is cited solely to disclose the assistance actually used in this revision.

## Search record

Queries combined student academic risk/performance, early warning, interpretable/explainable machine learning, fairness, and temporal/generalizability with 2023-2026. IEEE Xplore, Springer, Elsevier, ACM-related publisher material, Nature and official author-institution pages were prioritized. Not every publisher allowed full-page access; claims were restricted to verified abstracts/metadata. Several unrelated or low-relevance results were excluded. No number of screened papers is invented.

## Retraction and access limits

No retraction statement was observed in the official pages consulted. This is not an exhaustive Crossmark/retraction-database clearance. Authors should perform the journal-required final reference-status check immediately before submission. Network failures and registry throttling are retained in the metadata rather than presented as successful retrievals.

## Official sources

https://ieeeaccess.ieee.org/authors/submission-guidelines/
https://archive.ics.uci.edu/dataset/320/student+performance
https://www.nature.com/articles/s41598-026-48426-1
https://ieeexplore.ieee.org/document/11298693
https://link.springer.com/article/10.1007/s40593-023-00389-4
https://research.tue.nl/en/publications/boundary-conditions-of-generalizing-predictive-models-for-academi/
https://www.nature.com/articles/sdata2017171.pdf