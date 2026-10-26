"""Loading the trained model and turning a probability into a risk tier."""
import os
import pickle

import pandas as pd

from .. import config

_model_data = None  # {"model": RandomForestClassifier, "features": [...]} once loaded


def load_model(path=None):
    """Load model.pkl into memory. Safe to call when the file is missing."""
    global _model_data
    path = path or config.MODEL_PATH
    if os.path.exists(path):
        with open(path, "rb") as f:
            _model_data = pickle.load(f)
        print("Model loaded.")
    else:
        _model_data = None
        print("model.pkl not found. Run train_model.py first.")
    return _model_data


def get_model_data():
    return _model_data


def predict_probability(input_data):
    """Probability (0-1) that the person is at risk, given {feature: value}."""
    df = pd.DataFrame([input_data])
    return float(_model_data["model"].predict_proba(df)[0][1])


def classify_risk(prob):
    """Map a probability to (label, bootstrap class) using config.RISK_TIERS."""
    for label, css_class, minimum in config.RISK_TIERS:
        if prob >= minimum:
            return label, css_class
    return config.RISK_TIERS[-1][:2]
