"""
evaluate.py — Full model evaluation with confusion matrix, ROC curve, and metrics.
Run: python evaluate.py
"""
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay, accuracy_score, classification_report,
    confusion_matrix, roc_auc_score, roc_curve
)

from cervixguard.ml.dataset import load_dataset, make_splits
from cervixguard.ml.training import load_saved_model

print("Loading dataset...")
X, y = load_dataset()
# Exactly the split train_model.py used (same cleaning, same seed), so the test rows
# really are unseen by the saved model.
_, _, X_test, y_test = make_splits(X, y)

# ── Load saved model ───────────────────────────────────────────────────────────
print("Loading model.pkl...")
artifact = load_saved_model()
model = artifact["model"]
features = artifact["features"]
X_test = X_test[features]

# ── Predict ────────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# ── Print metrics ──────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print(f"  Accuracy  : {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(f"  ROC-AUC   : {roc_auc_score(y_test, y_prob):.4f}")
print("=" * 55)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Not At Risk", "At Risk"]))

# ── Feature importances ────────────────────────────────────────────────────────
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("Feature Importances:")
for feat, imp in importances.items():
    bar = "█" * int(imp * 100)
    print(f"  {feat:<35} {imp:.4f}  {bar}")

# ── Plots ──────────────────────────────────────────────────────────────────────
PURPLE, LIGHT_PURPLE = "#6d28d9", "#a78bfa"


def hide_top_right(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Model Evaluation — Cervical Cancer Risk Predictor",
             fontsize=14, fontweight="bold", color=PURPLE)

# 1. Confusion Matrix
ConfusionMatrixDisplay(
    confusion_matrix=confusion_matrix(y_test, y_pred),
    display_labels=["Not At Risk", "At Risk"],
).plot(ax=axes[0], colorbar=False, cmap="Purples")
axes[0].set_title("Confusion Matrix")

# 2. ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
auc = roc_auc_score(y_test, y_prob)
axes[1].plot(fpr, tpr, color=PURPLE, lw=2, label=f"AUC = {auc:.3f}")
axes[1].plot([0, 1], [0, 1], "k--", lw=1)
axes[1].fill_between(fpr, tpr, alpha=0.08, color=PURPLE)
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")
axes[1].set_title("ROC Curve")
axes[1].legend(loc="lower right")
hide_top_right(axes[1])

# 3. Feature Importance Bar Chart
colors = [PURPLE if i == 0 else LIGHT_PURPLE for i in range(len(importances))]
axes[2].barh(importances.index[::-1], importances.values[::-1],
             color=colors[::-1], edgecolor="white")
axes[2].set_xlabel("Importance Score")
axes[2].set_title("Feature Importances")
hide_top_right(axes[2])

plt.tight_layout()
plt.savefig("evaluation_report.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n" + "=" * 55)
print("  evaluation_report.png saved!")
print("=" * 55)
