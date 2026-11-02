from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "student-mat.csv"
SEED = 42
THRESHOLD = 0.5
LABELS = {0: "Not At Risk", 1: "At Risk"}
EXCLUDED = ["G1", "G2", "G3"]
NUMERIC = ["age", "Medu", "Fedu", "traveltime", "studytime", "failures", "famrel",
           "freetime", "goout", "Dalc", "Walc", "health", "absences"]
CATEGORICAL = ["school", "sex", "address", "famsize", "Pstatus", "Mjob", "Fjob",
               "reason", "guardian", "schoolsup", "famsup", "paid", "activities",
               "nursery", "higher", "internet", "romantic"]
FEATURES = CATEGORICAL + NUMERIC
CATEGORIES = {
    "school": ["GP", "MS"], "sex": ["F", "M"], "address": ["U", "R"],
    "famsize": ["LE3", "GT3"], "Pstatus": ["T", "A"],
    "Mjob": ["teacher", "health", "services", "at_home", "other"],
    "Fjob": ["teacher", "health", "services", "at_home", "other"],
    "reason": ["home", "reputation", "course", "other"],
    "guardian": ["mother", "father", "other"],
    **{name: ["yes", "no"] for name in ["schoolsup", "famsup", "paid", "activities",
                                         "nursery", "higher", "internet", "romantic"]},
}
RANGES = {"age": (15, 22), "Medu": (0, 4), "Fedu": (0, 4), "traveltime": (1, 4),
          "studytime": (1, 4), "failures": (0, 4), "famrel": (1, 5),
          "freetime": (1, 5), "goout": (1, 5), "Dalc": (1, 5), "Walc": (1, 5),
          "health": (1, 5), "absences": (0, 93)}
FEATURE_LABELS = {
    "school": "School", "sex": "Recorded sex", "address": "Home address type",
    "famsize": "Family size", "Pstatus": "Parents' cohabitation status",
    "Mjob": "Mother's job", "Fjob": "Father's job", "reason": "Reason for choosing school",
    "guardian": "Guardian", "schoolsup": "Extra educational support",
    "famsup": "Family educational support", "paid": "Extra paid classes in mathematics",
    "activities": "Extracurricular activities", "nursery": "Attended nursery school",
    "higher": "Wants higher education", "internet": "Internet access at home",
    "romantic": "In a romantic relationship", "age": "Age", "Medu": "Mother's education",
    "Fedu": "Father's education", "traveltime": "Travel time to school",
    "studytime": "Weekly study time", "failures": "Past class failures (UCI code)",
    "famrel": "Quality of family relationships", "freetime": "Free time after school",
    "goout": "Going out with friends", "Dalc": "Workday alcohol consumption",
    "Walc": "Weekend alcohol consumption", "health": "Health status",
    "absences": "School absences (dataset total)",
}
CODE_LABELS = {
    "school": {"GP": "Gabriel Pereira", "MS": "Mousinho da Silveira"},
    "sex": {"F": "Female", "M": "Male"}, "address": {"U": "Urban", "R": "Rural"},
    "famsize": {"LE3": "3 or fewer", "GT3": "More than 3"},
    "Pstatus": {"T": "Together", "A": "Apart"},
    "traveltime": {1: "Under 15 min", 2: "15–30 min", 3: "30–60 min", 4: "Over 1 hour"},
    "studytime": {1: "Under 2 hours", 2: "2–5 hours", 3: "5–10 hours", 4: "Over 10 hours"},
    "Medu": {0: "None", 1: "Primary (4th grade)", 2: "5th–9th grade", 3: "Secondary", 4: "Higher"},
    "Fedu": {0: "None", 1: "Primary (4th grade)", 2: "5th–9th grade", 3: "Secondary", 4: "Higher"},
}
