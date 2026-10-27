"""Dataset loading and the train/test split, shared by train_model.py and evaluate.py.

train_model.py and evaluate.py each used to clean the CSV their own way (drop incomplete
rows vs. median-fill), so evaluate.py's "same split as train_model.py" was not actually
the same split. Both now go through the functions below.
"""
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split

from .. import config
from .features import FEATURES, TARGET

RANDOM_STATE = 42


def load_dataset(path=None):
    """Return (X, y): the 11 model features as floats and the Biopsy target as ints."""
    df = pd.read_csv(path or config.DATASET_PATH)
    df.replace("?", float("nan"), inplace=True)
    # Drop rows with too many missing values, then rows missing any selected column.
    df.dropna(thresh=len(df.columns) - 3, inplace=True)
    df = df[FEATURES + [TARGET]].dropna()
    return df[FEATURES].astype(float), df[TARGET].astype(int)


def make_splits(X, y):
    """80/20 stratified split; SMOTE is applied to the training part only.

    Returns X_train_resampled, y_train_resampled, X_test, y_test.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    X_train_res, y_train_res = SMOTE(random_state=RANDOM_STATE).fit_resample(X_train, y_train)
    return X_train_res, y_train_res, X_test, y_test
