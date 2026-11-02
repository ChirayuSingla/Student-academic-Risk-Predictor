"""Presentation helpers; the original UCI feature encoding is preserved."""
from html import escape

import pandas as pd
import streamlit as st

from .config import CATEGORIES, CODE_LABELS, FEATURE_LABELS, RANGES

STEPS = [
    ("Student", "Student & school", "Start with the student's background and school.",
     ["school", "age", "sex", "address", "reason", "traveltime"]),
    ("Family", "Family & home", "Describe the student's home environment and family support.",
     ["famsize", "Pstatus", "guardian", "Medu", "Fedu", "Mjob", "Fjob", "famsup", "nursery", "internet", "famrel"]),
    ("Study", "Study & support", "Add study habits, previous failures, and attendance information.",
     ["studytime", "failures", "schoolsup", "paid", "activities", "higher", "absences"]),
    ("Wellbeing", "Lifestyle & wellbeing", "Use the student's own responses for these sensitive research fields.",
     ["freetime", "goout", "romantic", "Dalc", "Walc", "health"]),
]
LABELS = {**FEATURE_LABELS, "failures": "Previous class failures", "absences": "Recorded school absences",
          "Dalc": "Workday alcohol use", "Walc": "Weekend alcohol use"}
DISPLAY = {
    **CODE_LABELS,
    "Mjob": {"teacher": "Teaching", "health": "Health care", "services": "Public services", "at_home": "At home", "other": "Other"},
    "Fjob": {"teacher": "Teaching", "health": "Health care", "services": "Public services", "at_home": "At home", "other": "Other"},
    "reason": {"home": "Close to home", "reputation": "School reputation", "course": "Course preference", "other": "Other"},
    "famrel": {1: "Very poor", 2: "Poor", 3: "Average", 4: "Good", 5: "Excellent"},
    "health": {1: "Very poor", 2: "Poor", 3: "Fair", 4: "Good", 5: "Very good"},
    "failures": {0: "No previous failures", 1: "1 previous failure", 2: "2 previous failures", 3: "3 previous failures", 4: "Other UCI code (4)"},
    **{name: {1: "Very low", 2: "Low", 3: "Moderate", 4: "High", 5: "Very high"}
       for name in ["freetime", "goout", "Dalc", "Walc"]},
}
HELP = {
    "school": "Trained on these two Portuguese schools only. Applicability to other schools is not established.",
    "age": "The source cohort includes ages 15–22.",
    "sex": "Original UCI categories. Fairness across groups has not been validated.",
    "Medu": "Highest completed level in the original UCI categories.",
    "Fedu": "Highest completed level in the original UCI categories.",
    "failures": "Past class failures, not current-course grades. The CSV observes 0–3; the source documentation also describes code 4.",
    "absences": "Total recorded absences (0–93). Early-cutoff availability is not established; a year-to-date count changes this field's meaning.",
    "Dalc": "Self-reported UCI rating from very low to very high; not a drink count.",
    "Walc": "Self-reported UCI rating from very low to very high; not a drink count.",
    "freetime": "Self-reported amount of free time after school.",
    "goout": "Self-reported frequency of going out with friends.",
}


def display_value(name, value):
    if value is None:
        return "Not entered"
    return str(DISPLAY.get(name, {}).get(value, str(value).replace("_", " ").capitalize()))


def styles():
    st.html("""<style>
    :root { --ink:#172b4d; --muted:#52657d; --blue:#2458d3; --line:#dce4ef; }
    .stApp { background:#f5f7fb; color:var(--ink); }
    [data-testid="stHeader"] { background:transparent; }
    .stMainBlockContainer { max-width:1120px; padding:2.6rem 2.1rem 2rem; }
    h1 { font-size:2.45rem !important; line-height:1.16 !important; letter-spacing:-.055rem; padding-top:.15rem !important; }
    h2 { font-size:1.55rem !important; letter-spacing:-.025rem; }
    h3 { font-size:1.08rem !important; }
    p, label, [data-testid="stCaptionContainer"] { line-height:1.55; }
    [data-testid="stCaptionContainer"] { color:var(--muted); }
    [data-testid="stCaptionContainer"] p { color:var(--muted) !important; }
    input::placeholder { color:var(--muted) !important; opacity:1; }
    [data-testid="stForm"] h2 { font-size:1.15rem !important; }
    [data-testid="stWidgetLabel"] p { font-size:.9rem; font-weight:550; }
    [data-testid="stForm"] { background:#fff; border:1px solid var(--line); border-radius:16px; padding:1.5rem; }
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] { gap:1.15rem; }
    [data-baseweb="select"] > div, [data-testid="stNumberInputContainer"] { border-radius:9px; min-height:44px; }
    button { min-height:44px; border-radius:9px !important; }
    button:focus-visible, input:focus-visible, [role="combobox"]:focus-visible { outline:3px solid #2458d3 !important; outline-offset:3px; }
    [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"], button[kind="primary"] { background:var(--blue); border-color:var(--blue); }
    [data-testid="stExpander"] { background:#fff; border-radius:12px; }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] { font-size:2.1rem; font-weight:650; }
    .brand { display:flex; align-items:center; gap:10px; margin-bottom:.65rem; font-size:.93rem; font-weight:700; letter-spacing:-.02rem; }
    .brand-mark { display:flex; align-items:center; justify-content:center; width:34px; height:34px; border-radius:10px; background:#2458d3; color:white; font-size:.79rem; letter-spacing:.01rem; }
    .brand-label { margin-left:auto; font-size:.7rem; letter-spacing:.075rem; text-transform:uppercase; color:var(--muted); font-weight:600; }
    .eyebrow { color:var(--blue); font-size:.72rem; font-weight:700; letter-spacing:.1rem; text-transform:uppercase; margin-bottom:.35rem; }
    .hero-description { color:var(--muted); font-size:1rem; max-width:660px; margin:.25rem 0 .45rem; }
    .research-note { display:flex; gap:11px; padding:.8rem 1rem; border:1px solid #cfdcf3; border-radius:10px; background:#edf3ff; font-size:.85rem; line-height:1.5; margin:.2rem 0 .4rem; }
    .research-note strong { white-space:nowrap; }
    .step-list { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); list-style:none; margin:0 0 .65rem; padding:0; gap:.5rem; }
    .step-list li { display:flex; align-items:center; gap:9px; color:#52657d; font-size:.83rem; padding:.65rem .6rem; border-radius:9px; border:1px solid transparent; }
    .step-list .active { color:#1745ad; background:#e8efff; border-color:#d0ddfb; font-weight:650; }
    .step-list .done { color:#276658; }
    .step-number { width:25px; height:25px; border-radius:50%; background:#e3e8f0; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:.76rem; font-weight:700; }
    .active .step-number { background:#2458d3; color:#fff; }
    .done .step-number { background:#dbede7; }
    .context-card { background:#fff; border:1px solid var(--line); border-radius:16px; padding:1.5rem; }
    .context-card h3 { margin:.3rem 0 .6rem; font-size:1rem; }
    .context-card p { font-size:.87rem; color:var(--muted); margin-bottom:.9rem; }
    .context-line { border-top:1px solid #e8edf4; padding-top:.95rem; margin-top:.95rem; }
    .small-tag { display:inline-block; border-radius:6px; padding:4px 8px; background:#edf2fa; color:#426183; font-size:.72rem; font-weight:600; }
    .result-strip { border-radius:12px; padding:1rem 1.15rem; background:#edf3ff; border:1px solid #cfdcf3; margin-bottom:1rem; font-size:.94rem; line-height:1.55; }
    .result-strip.attention { background:#fff5e8; border-color:#ecd8b6; color:#704511; }
    .footer { padding:1.1rem 0; border-top:1px solid var(--line); margin-top:1.5rem; font-size:.78rem; color:#52657d; line-height:1.6; }
    @media(max-width:900px) {
      .st-key-assessment-layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
      .st-key-assessment-layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { width:100% !important; flex:1 1 100% !important; min-width:100% !important; }
    }
    @media(max-width:600px) {
      .stMainBlockContainer { padding:1.65rem 1rem; }
      h1 { font-size:1.95rem !important; }
      [data-testid="stForm"] { padding:1rem; }
      .step-list { gap:.2rem; }
      .step-list li { flex-direction:column; gap:5px; padding:.6rem .15rem; font-size:.71rem; }
      .research-note { display:block; }
      .research-note strong { display:block; margin-bottom:.25rem; }
      .brand-label { font-size:.62rem; }
      .context-card { padding:1.1rem; }
    }
    </style>""")


def header():
    st.html('<div class="brand"><span class="brand-mark" aria-hidden="true">SL</span>StudentLens<span class="brand-label">Academic risk research</span></div>')
    st.html('<div class="eyebrow">Student performance · Mathematics</div>')
    st.title("Understand academic risk")
    st.html('<p class="hero-description">Build a student profile and explore an interpretable estimate from our academic risk research models.</p>')
    st.html('<div class="research-note"><strong>Research prototype</strong><span>Use alongside an educator’s judgment, never as the sole basis for academic decisions. Probabilities are uncalibrated estimates.</span></div>')


def stepper(step):
    items = []
    for i, (label, _, _, _) in enumerate(STEPS):
        css = "active" if i == step else "done" if i < step else ""
        current = ' aria-current="step"' if i == step else ""
        status = "✓" if i < step else str(i+1)
        items.append(f'<li class="{css}"{current} aria-label="Step {i+1}: {escape(label)}"><span class="step-number" aria-hidden="true">{status}</span>'
                     f'<span>{escape(label)}</span></li>')
    st.html('<nav aria-label="Assessment progress"><ol class="step-list">' + "".join(items) + "</ol></nav>")


def field(name, saved):
    if name in CATEGORIES or name in DISPLAY:
        options = CATEGORIES[name] if name in CATEGORIES else list(DISPLAY[name])
        return st.selectbox(LABELS[name], options, index=options.index(saved) if saved is not None else None,
                            format_func=lambda value: display_value(name, value), key=name,
                            placeholder="Select an option", help=HELP.get(name))
    lower, upper = RANGES[name]
    return st.number_input(LABELS[name], min_value=lower, max_value=upper, value=saved,
                           step=1, key=name, placeholder="Enter age" if name == "age" else "Enter total absences",
                           help=HELP.get(name))


def review_table(values):
    return pd.DataFrame([{"Student information": LABELS[name], "Your entry": display_value(name, value)}
                         for _, _, _, names in STEPS for name in names if (value := values.get(name)) is not None])


def context_card(completed):
    st.html(f"""<aside class="context-card" aria-label="Assessment guide">
    <span class="small-tag">4 steps · 30 fields</span>
    <h3>A clearer view of the estimate</h3>
    <p>Complete the profile, then review a risk category, a probability estimate, and the model’s explanation.</p>
    <div class="context-line"><h3>Use the student's information</h3>
    <p>Every field starts blank. Back and Continue save your entries within this session.</p>
    <p><strong>{completed} of 30 fields saved</strong></p></div>
    <div class="context-line"><h3>Keep the context in mind</h3>
    <p>This model uses a historical sample from two Portuguese schools. An estimate does not explain what causes academic difficulty.</p>
    <p>Form entries stay in memory and are not saved as student records.</p></div>
    </aside>""")


def friendly_tree_feature(transformed):
    if transformed.startswith("numeric__"):
        return LABELS[transformed.removeprefix("numeric__")]
    encoded = transformed.removeprefix("categorical__")
    for name in sorted(CATEGORIES, key=len, reverse=True):
        if encoded.startswith(name + "_"):
            category = encoded[len(name)+1:]
            return f"{LABELS[name]}: {display_value(name, category)} (indicator)"
    return transformed
