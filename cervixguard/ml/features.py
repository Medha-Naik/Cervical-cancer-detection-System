"""The single source of truth for the model's input features.

Before this module existed, the feature list was copy-pasted into train_model.py,
evaluate.py and main.py, and the feature -> database-column mapping was written
out three separate times inside app.py.
"""

# (feature name in the dataset / model, column name in the `predictions` table)
FEATURE_COLUMNS = [
    ("Age", "age"),
    ("Number of sexual partners", "sexual_partners"),
    ("First sexual intercourse", "first_intercourse"),
    ("Num of pregnancies", "pregnancies"),
    ("Smokes", "smokes"),
    ("Smokes (years)", "smokes_years"),
    ("Hormonal Contraceptives", "hormonal_contraceptives"),
    ("IUD", "iud"),
    ("STDs", "stds"),
    ("STDs (number)", "stds_number"),
    ("STDs:HPV", "stds_hpv"),
]

FEATURES = [feature for feature, _ in FEATURE_COLUMNS]
TARGET = "Biopsy"
