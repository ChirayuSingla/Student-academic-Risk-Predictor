"""Guided Streamlit assessment using the saved, grade-free research models."""
import json
import joblib
import pandas as pd
import streamlit as st

from src.config import FEATURES, NUMERIC, ROOT
from src.data import validate_inputs
from src.evaluation import positive_probability
from src.explainability import logistic_local_explanation, tree_local_explanation
from src.ui import LABELS, STEPS, context_card, field, friendly_tree_feature, header, review_table, stepper, styles
from src.utils import sha256

st.set_page_config(page_title="StudentLens · Academic Risk Research", page_icon="📘", layout="wide")
styles()


@st.cache_resource
def load_artifacts(metadata_digest):
    metadata = json.loads((ROOT / "models" / "metadata.json").read_text(encoding="utf-8"))
    models = {}
    for name, expected_hash in metadata["model_sha256"].items():
        path = ROOT / "models" / f"{name}.joblib"
        if sha256(path) != expected_hash:
            raise ValueError(f"Saved model integrity check failed: {name}")
        models[name] = joblib.load(path)
    return models, metadata


def initialize_profile():
    st.session_state["profile"] = {name: None for name in FEATURES}
    st.session_state["step"] = 0
    st.session_state["result"] = None
    st.session_state["page"] = "profile"
    st.session_state["form_error"] = None
    for name in FEATURES + ["review_confirmed"]:
        st.session_state.pop(name, None)


def edit_profile():
    st.session_state["page"] = "profile"
    st.session_state["step"] = 0
    st.session_state.pop("review_confirmed", None)
    st.session_state["form_error"] = None


def estimate(values, model_name, models, metadata):
    student = validate_inputs(pd.DataFrame([values], columns=FEATURES))
    unsupported = []
    for name, value in values.items():
        if name in NUMERIC:
            lower, upper = metadata["training_numeric_ranges"][name]
            if value < lower or value > upper:
                unsupported.append(LABELS[name])
        elif value not in metadata["training_categories"][name]:
            unsupported.append(LABELS[name])
    probability = float(positive_probability(models[model_name], student)[0])
    return {"values": values.copy(), "model": model_name, "probability": probability,
            "unsupported": unsupported, "run_id": metadata["run_id"]}


def submit_step(backwards, names, models, metadata):
    """Commit form values before the next page render, retaining non-widget draft state."""
    saved = st.session_state["profile"]
    values = {name: st.session_state.get(name) for name in names}
    saved.update(values)
    st.session_state["form_error"] = None
    if backwards:
        st.session_state["step"] -= 1
        return
    missing = [LABELS[name] for name in names if values[name] is None]
    if missing:
        st.session_state["form_error"] = "Complete these fields to continue: " + ", ".join(missing) + "."
    elif st.session_state["step"] < 3:
        st.session_state["step"] += 1
    elif not st.session_state.get("review_confirmed", False):
        st.session_state["form_error"] = "Review your entries and check the confirmation before requesting an estimate."
    else:
        try:
            st.session_state["result"] = estimate(saved, st.session_state["model"], models, metadata)
            st.session_state["page"] = "result"
        except (ValueError, TypeError) as error:
            st.session_state["form_error"] = f"Check the student information: {error}"


def render_profile(models, metadata):
    step = st.session_state["step"]
    stepper(step)
    saved = st.session_state["profile"]
    completed = sum(value is not None for value in saved.values())
    with st.container(key="assessment-layout"):
        main, guide = st.columns([2, 1], gap="large")
        with guide:
            context_card(completed)
        with main:
            _, title, description, names = STEPS[step]
            with st.form(f"profile_step_{step}", border=True):
                st.caption(f"STEP {step+1} OF 4")
                st.header(title)
                st.caption(description + " All fields are required.")
                if step == 2:
                    st.info("Attendance note: UCI records total absences. Its early-cutoff availability has not been established.")
                for start in range(0, len(names), 2):
                    columns = st.columns(2, gap="medium")
                    for column, name in zip(columns, names[start:start+2]):
                        with column:
                            field(name, saved[name])
                if step == 3:
                    st.divider()
                    with st.expander("Review your earlier entries"):
                        st.dataframe(review_table(saved), hide_index=True, width="stretch")
                    st.checkbox("I have reviewed the entries for this student.", key="review_confirmed")
                st.divider()
                back_column, next_column = st.columns([1, 2])
                with back_column:
                    st.form_submit_button("Back", key="back", disabled=step == 0, width="stretch",
                                          on_click=submit_step, args=(True, names, models, metadata))
                with next_column:
                    st.form_submit_button("Get risk estimate" if step == 3 else "Continue",
                                          key="continue", type="primary", width="stretch",
                                          on_click=submit_step, args=(False, names, models, metadata))
                if st.session_state.get("form_error"):
                    st.error(st.session_state["form_error"])


def render_result(models, metadata):
    result = st.session_state["result"]
    name, probability = result["model"], result["probability"]
    category = "At Risk" if probability >= metadata["threshold"] else "Not At Risk"
    student = pd.DataFrame([result["values"]], columns=FEATURES)
    st.html('<div class="eyebrow">Assessment complete</div>')
    st.header("Your research estimate")
    st.caption(f"Based on your submitted profile · {name.replace('_', ' ').title()}")
    with st.container(border=True, key="result-card"):
        left, right = st.columns(2)
        left.metric("Predicted risk category", category)
        right.metric("Estimated probability of At Risk", f"{probability:.1%}")
        st.caption(f"At Risk means a predicted final mathematics grade below 10/20. The category uses a {metadata['threshold']:.0%} threshold.")
        css = " attention" if category == "At Risk" else ""
        text = ("The model flags this profile for a support conversation. Discuss the student's situation with an educator before taking action."
                if category == "At Risk" else
                "The model does not flag this profile at its threshold. This does not rule out academic difficulty or a need for support.")
        st.html(f'<div class="result-strip{css}">{text}</div>')
        st.caption("This percentage is an uncalibrated model estimate, not a verified individual likelihood. The model has no prospective or external validation.")
    if result["unsupported"]:
        st.warning("Outside the model's training range: " + ", ".join(result["unsupported"]) + ". This estimate may be less reliable.")
    left, right = st.columns(2)
    left.button("Edit student profile", on_click=edit_profile, width="stretch", type="primary", key="edit_profile")
    right.button("Start a new assessment", on_click=initialize_profile, width="stretch", key="new_profile")
    if result["run_id"] != metadata["run_id"]:
        st.warning("The trained artifacts have changed since this estimate. Edit and resubmit the profile to update it.")
        return
    st.subheader("What shaped this estimate?")
    st.caption("These are associations in the fitted model. They do not identify causes or show which interventions will help.")
    if name == "logistic_regression":
        contributions, reference = logistic_local_explanation(models[name], student, metadata)
        table = contributions.rename("Contribution").reset_index().rename(columns={"feature": "Feature"})
        table["Feature"] = table["Feature"].map(LABELS)
        shown = table.head(6).copy()
        shown["Direction"] = shown.Contribution.map(lambda value: "Raises estimate" if value > 0 else "Lowers estimate" if value < 0 else "No change")
        st.write("The largest contributions compare this profile with the average transformed training profile.")
        st.dataframe(shown[["Feature", "Direction", "Contribution"]], hide_index=True, width="stretch",
                     column_config={"Contribution": st.column_config.NumberColumn("Log-odds contribution", format="%+.3f")})
        with st.expander("See all contributions and the calculation"):
            st.dataframe(table, hide_index=True, width="stretch",
                         column_config={"Contribution": st.column_config.NumberColumn(format="%+.4f")})
            st.caption(f"Reference log-odds: {reference:.3f}. Add all contributions to reconstruct the model's log-odds. "
                       "Positive contributions raise modeled risk; negative contributions lower it. The reference is a mathematical average, not an actual student.")
    else:
        path, samples = tree_local_explanation(models[name], student)
        if path:
            friendly = pd.DataFrame([{"Step": i+1, "Model condition": friendly_tree_feature(item["feature"]),
                                       "Observed value": item["value"], "Rule followed": f"{item['comparison']} {item['threshold']:g}"}
                                      for i, item in enumerate(path)])
            st.write("The decision tree followed these conditions for the submitted profile.")
            st.dataframe(friendly, hide_index=True, width="stretch")
        else:
            st.write("The fitted tree makes no splits; all profiles reach the same leaf.")
        st.caption(f"The final leaf contains {samples} training students. Category indicators are 0 (absent) or 1 (present). "
                   "The estimated probability may use class-weighted proportions, rather than an observed risk rate.")
    with st.expander("View the submitted student profile"):
        st.dataframe(review_table(result["values"]), hide_index=True, width="stretch")


def research_details(metadata):
    with st.expander("Research details & model performance"):
        st.markdown("**Scope and limitations**")
        st.write("This is a retrospective, grade-free prototype based on 395 students from two Portuguese schools. "
                 "Feature timestamps are unavailable; total absences and other fields may span the year. "
                 "Excluding grades alone does not establish early-warning validity. Sensitive attributes and subgroup fairness require assessment before any use in decisions.")
        summary_path = ROOT / "results" / "metrics_summary.csv"
        if summary_path.exists():
            summary = pd.read_csv(summary_path)
            summary["model"] = summary.model.replace({"logistic_regression": "Logistic Regression", "decision_tree": "Decision Tree",
                "dummy_majority": "Majority-class baseline", "dummy_always_at_risk": "Always At Risk baseline"})
            summary = summary[["model", "precision", "recall", "f1", "f2", "roc_auc", "accuracy"]]
            st.dataframe(summary, hide_index=True, width="stretch", column_config={
                "model": "Model", **{key: st.column_config.NumberColumn(label, format="%.3f") for key, label in
                [("precision", "At Risk precision"), ("recall", "At Risk recall"), ("f1", "At Risk F1"), ("f2", "At Risk F2"), ("roc_auc", "ROC-AUC"), ("accuracy", "Accuracy")]}})
            st.caption("Held-out test results. Both classifiers detected 18 of 26 At Risk students and missed eight. "
                       "The always-At-Risk baseline has higher F2 by flagging everyone. See the research report for the full comparison.")
        st.caption(f"{metadata['split']['train_size']} training / {metadata['split']['test_size']} test students. "
                   "Five-fold stratified training-only cross-validation. Default model selected by F2 to emphasize recall. "
                   f"Run: {metadata['run_id']}.")
        st.markdown("Dataset: [Cortez (2008), UCI Student Performance](https://doi.org/10.24432/C5TG7T). "
                    "Conceptual reference: [Ewais et al. (2026)](https://doi.org/10.1038/s41598-026-48426-1). "
                    "The paper's separate institutional dataset was not used.")


header()
metadata_path = ROOT / "models" / "metadata.json"
if not metadata_path.exists():
    st.error("The trained models are not available yet. Run python -m src.run_pipeline, then reload this page.")
    st.stop()
try:
    models, metadata = load_artifacts(sha256(metadata_path))
except Exception as error:
    st.error(f"Could not load the trained models: {error}")
    st.stop()
if "profile" not in st.session_state:
    initialize_profile()

with st.expander("Model settings"):
    names = list(models)
    selected = st.selectbox("Prediction model", names, index=names.index(metadata["selected_model"]),
                            format_func=lambda name: name.replace("_", " ").title(), key="model")
    st.caption("The default was chosen using training-only cross-validation. Model changes apply to your next estimate; an existing result keeps its original model.")

if st.session_state["page"] == "result":
    render_result(models, metadata)
else:
    render_profile(models, metadata)
research_details(metadata)
st.html('<footer class="footer">StudentLens · UCI mathematics research<br>Support conversations, informed by context. Research prototype — never the sole basis for academic decisions.</footer>')
