"""Model construction and persistence."""
import pickle

from sklearn.ensemble import RandomForestClassifier

from .. import config
from .features import FEATURES
from .dataset import RANDOM_STATE


def build_model():
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )


def save_model(model, path=None):
    """Persist the model together with its feature list (the format app.py expects)."""
    with open(path or config.MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "features": FEATURES}, f)


def load_saved_model(path=None):
    with open(path or config.MODEL_PATH, "rb") as f:
        return pickle.load(f)
