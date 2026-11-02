import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import CATEGORIES, DATA_PATH, EXCLUDED, FEATURES, NUMERIC, RANGES, SEED


def validate_inputs(frame, allow_missing=False):
    if not frame.columns.is_unique or set(frame.columns) != set(FEATURES):
        raise ValueError("Inputs must contain exactly the 30 approved non-grade features.")
    frame = frame.loc[:, FEATURES].copy()
    if not allow_missing and frame.isna().any().any():
        raise ValueError("Student input contains missing values.")
    for name, categories in CATEGORIES.items():
        values = frame[name].dropna()
        if not values.isin(categories).all():
            raise ValueError(f"Invalid category for {name}.")
    for name in NUMERIC:
        if frame[name].dropna().map(lambda value: isinstance(value, (bool, np.bool_))).any():
            raise ValueError(f"{name} must be an integer, not a boolean.")
        try:
            converted = pd.to_numeric(frame[name], errors="raise")
        except (ValueError, TypeError) as error:
            raise ValueError(f"{name} must contain numeric integer values.") from error
        values = converted.dropna()
        lower, upper = RANGES[name]
        if not (np.isfinite(values).all() and values.between(lower, upper).all()
                and (values % 1 == 0).all()):
            raise ValueError(f"{name} must be an integer from {lower} to {upper}.")
        frame[name] = converted
    return frame.loc[:, FEATURES]


def load_data(path=DATA_PATH):
    frame = pd.read_csv(path, sep=";")
    if frame.shape != (395, 33) or set(frame.columns) != set(FEATURES + EXCLUDED):
        raise ValueError(f"Expected original UCI mathematics data (395 x 33); found {frame.shape}.")
    if frame.isna().any().any():
        raise ValueError("Original UCI mathematics data should have no missing values.")
    for name in EXCLUDED:
        if not (frame[name].between(0, 20).all() and (frame[name] % 1 == 0).all()):
            raise ValueError(f"Invalid grade values in {name}.")
    X = validate_inputs(frame[FEATURES]).copy()
    y = (frame["G3"] < 10).astype(int).rename("at_risk")
    assert not set(EXCLUDED) & set(X.columns)
    return frame, X, y


def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)
    assert set(X_train.index).isdisjoint(X_test.index)
    return X_train, X_test, y_train, y_test
