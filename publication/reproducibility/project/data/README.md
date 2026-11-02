# Original UCI source data

`student-mat.csv` is the primary experiment. `student-por.csv` is not used for modeling.
The supplied `student+performance.zip` wraps the original `student.zip`; extraction preserves
original bytes, delimiters, grade values and UCI documentation. No synthetic records are added.

Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository.
[DOI: 10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T).
[Official dataset](https://archive.ics.uci.edu/dataset/320/student+performance).
[CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).

See `provenance.json` for hashes and official byte-comparison status; `student.txt` contains
the source feature definitions. The cohort has no feature timestamps, so early availability
of total absences and other fields cannot be assumed from grade exclusion alone.
