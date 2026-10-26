"""Train the risk model and save it to model.pkl:  python train_model.py

Data cleaning, the split and the model definition live in cervixguard/ml/.
"""
from sklearn.metrics import accuracy_score, classification_report

from cervixguard import config
from cervixguard.ml.dataset import load_dataset, make_splits
from cervixguard.ml.training import build_model, save_model

X, y = load_dataset()
X_train_res, y_train_res, X_test, y_test = make_splits(X, y)

model = build_model()
model.fit(X_train_res, y_train_res)

# ── Evaluate ──
y_pred = model.predict(X_test)
print(f"✅ Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print()
print(classification_report(y_test, y_pred, target_names=["Not At Risk", "At Risk"]))

# ── Probability spread across the app's risk tiers ──
# The app turns a probability into Low / Medium / High (see RISK_TIERS in config.py),
# so check the model actually produces probabilities in each band.
probs = model.predict_proba(X_test)[:, 1]
print(f"Prob range  → min: {probs.min():.3f}  max: {probs.max():.3f}  mean: {probs.mean():.3f}")
upper = float("inf")
for label, _, minimum in config.RISK_TIERS:
    count = ((probs >= minimum) & (probs < upper)).sum()
    print(f"{label:<12} ({minimum:.2f}+): {count} samples")
    upper = minimum

save_model(model)
print("\n✅ Model saved as model.pkl")
