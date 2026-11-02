import json
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.base import clone
from streamlit.testing.v1 import AppTest

from src.config import CATEGORICAL, EXCLUDED, FEATURES, NUMERIC, ROOT
from src.data import load_data, split_data, validate_inputs
from src.evaluation import positive_probability
from src.ui import STEPS
from src.verify import verify


def test_saved_experiment_audit():
    assert all(verify().values())


def test_input_contract_rejects_grades():
    frame, X, _ = load_data()
    with pytest.raises(ValueError, match="exactly"):
        validate_inputs(frame)
    assert not set(EXCLUDED) & set(validate_inputs(X).columns)


def test_fold_preprocessor_does_not_learn_heldout_categories():
    _, X, y = load_data()
    X_train, _, _, _ = split_data(X, y)
    model = joblib.load(ROOT / "models" / "logistic_regression.joblib")
    # Real UCI rows only: hold out one school's rows and fit preprocessing on the other.
    fit_rows = X_train[X_train.school == "GP"]
    heldout = X_train[X_train.school == "MS"]
    assert len(heldout) > 0
    preprocess = clone(model.named_steps["preprocess"]).fit(fit_rows)
    encoder = preprocess.named_transformers_["categorical"].named_steps["onehot"]
    assert encoder.categories_[CATEGORICAL.index("school")].tolist() == ["GP"]
    # sklearn emits a truthful warning for an unknown category; transform remains valid.
    with pytest.warns(UserWarning, match="unknown categories"):
        transformed = preprocess.transform(heldout)
    assert np.isfinite(transformed).all()
    np.testing.assert_allclose(preprocess.named_transformers_["numeric"].named_steps["scale"].mean_,
                               fit_rows[NUMERIC].mean())


@pytest.mark.parametrize("name", ["logistic_regression", "decision_tree"])
def test_streamlit_real_student_prediction_and_explanation(name):
    _, X, y = load_data()
    _, X_test, _, _ = split_data(X, y)
    row = X_test.iloc[0]
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not app.exception
    app.radio(key="model").set_value(name).run()
    app.text_input(key="student_name_input").set_value("Aarav Sharma")
    rendered_features = set()
    for i, (_, _, _, features) in enumerate(STEPS):
        assert app.session_state["step"] == i
        assert not app.selectbox
        rendered_features.update(widget.key for widget in list(app.radio) + list(app.number_input) + list(app.text_input))
        for feature in features:
            if feature == "school":
                rendered_features.add("school")
                app.text_input(key="school_input").set_value(row[feature])
            elif feature in NUMERIC:
                app.number_input(key=feature).set_value(int(row[feature]))
            else:
                app.radio(key=feature).set_value(row[feature])
        if i == 3:
            app.checkbox(key="review_confirmed").check()
        app.button(key="continue").click().run()
        assert not app.exception
    assert not app.exception
    model = joblib.load(ROOT / "models" / f"{name}.joblib")
    probability = float(positive_probability(model, X_test.iloc[[0]])[0])
    assert app.metric[0].value == ("At Risk" if probability >= 0.5 else "Not At Risk")
    assert app.metric[1].value == f"{probability:.1%}"
    assert app.session_state["result"]["student_name"] == "Aarav Sharma"
    assert "student_name" not in app.session_state["result"]["values"]
    assert any(text.value == "Student: Aarav Sharma" for text in app.text)
    assert not set(EXCLUDED) & rendered_features
    assert set(FEATURES).issubset(rendered_features)
    assert any("uncalibrated" in caption.value for caption in app.caption)
    # The local explanation table and results table are both rendered.
    assert len(app.dataframe) >= 2
    # A settings change must not relabel an already submitted estimate.
    other = "decision_tree" if name == "logistic_regression" else "logistic_regression"
    app.radio(key="model").set_value(other).run()
    assert app.session_state["result"]["model"] == name
    assert app.metric[1].value == f"{probability:.1%}"
    app.button(key="edit_profile").click().run()
    assert app.session_state["step"] == 0
    assert app.number_input(key="age").value == int(row.age)
    assert app.text_input(key="student_name_input").value == "Aarav Sharma"
    assert not app.metric


def test_guided_form_validation_and_back_preserves_entries():
    _, X, _ = load_data()
    row = X.iloc[0]
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert app.number_input(key="age").value is None
    assert app.text_input(key="school_input").value == ""
    assert app.text_input(key="student_name_input").value == ""
    assert not app.selectbox
    app.button(key="continue").click().run()
    assert app.session_state["step"] == 0
    assert app.error and "Complete these fields" in app.error[0].value
    assert "Student name" in app.error[0].value
    app.text_input(key="student_name_input").set_value("  Meera Singh  ")
    for feature in STEPS[0][3]:
        if feature == "school":
            app.text_input(key="school_input").set_value(row[feature])
        elif feature in NUMERIC:
            app.number_input(key=feature).set_value(int(row[feature]))
        else:
            app.radio(key=feature).set_value(row[feature])
    app.button(key="continue").click().run()
    assert app.session_state["step"] == 1
    assert app.session_state["student_name"] == "Meera Singh"
    app.radio(key="guardian").set_value(row.guardian)
    app.button(key="back").click().run()
    assert app.number_input(key="age").value == int(row.age)
    assert app.session_state["profile"]["school"] == row.school
    assert app.text_input(key="school_input").value in ("Gabriel Pereira", "Mousinho da Silveira")
    assert app.text_input(key="student_name_input").value == "Meera Singh"
    app.button(key="continue").click().run()
    assert app.radio(key="guardian").value == row.guardian


def test_start_new_assessment_clears_student_profile():
    # Complete a real profile, then test the deliberate reset path.
    _, X, _ = load_data()
    row = X.iloc[0]
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.text_input(key="student_name_input").set_value("Riya Patel")
    for step, (_, _, _, features) in enumerate(STEPS):
        for feature in features:
            if feature == "school":
                app.text_input(key="school_input").set_value(row[feature])
            elif feature in NUMERIC:
                app.number_input(key=feature).set_value(int(row[feature]))
            else:
                app.radio(key=feature).set_value(row[feature])
        if step == 3:
            app.button(key="continue").click().run()
            assert app.session_state["page"] == "profile"
            assert app.session_state["result"] is None
            assert "Review your entries" in app.error[0].value
            app.checkbox(key="review_confirmed").check()
        app.button(key="continue").click().run()
    app.button(key="new_profile").click().run()
    assert not app.exception
    assert app.session_state["result"] is None
    assert all(value is None for value in app.session_state["profile"].values())
    assert app.number_input(key="age").value is None
    assert app.text_input(key="student_name_input").value == ""
    assert app.session_state["student_name"] == ""


def test_ui_preserves_experiment_results():
    baseline = json.loads((ROOT / "results" / "ui-change-baseline.json").read_text(encoding="utf-8"))
    actual = json.loads((ROOT / "results" / "metrics.json").read_text(encoding="utf-8"))
    assert actual == baseline["metrics"]


@pytest.mark.parametrize("typed,expected", [
    ("  gabriel   pereira  ", "GP"),
    ("MOUSINHO DA SILVEIRA", "MS"),
])
def test_typed_school_names_are_normalized_and_preserved(typed, expected):
    _, X, _ = load_data()
    row = X.iloc[0]
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.text_input(key="student_name_input").set_value("Test Student")
    for feature in STEPS[0][3]:
        if feature == "school":
            app.text_input(key="school_input").set_value(typed)
        elif feature in NUMERIC:
            app.number_input(key=feature).set_value(int(row[feature]))
        else:
            app.radio(key=feature).set_value(row[feature])
    app.button(key="continue").click().run()
    assert not app.exception
    assert app.session_state["step"] == 1
    assert app.session_state["profile"]["school"] == expected
    app.button(key="back").click().run()
    assert app.text_input(key="school_input").value in ("Gabriel Pereira", "Mousinho da Silveira")
    assert not any(widget.key == "school" for widget in app.radio)


def test_unsupported_typed_school_has_clear_validation():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.text_input(key="school_input").set_value("Unknown School")
    app.button(key="continue").click().run()
    assert not app.exception
    assert app.session_state["step"] == 0
    assert "two schools supported" in app.error[0].value
    assert app.session_state["profile"]["school"] is None
    assert app.text_input(key="school_input").value == "Unknown School"
