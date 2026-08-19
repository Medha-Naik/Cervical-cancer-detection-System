import os
import pickle
import pandas as pd
from config import MODEL_PATH, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD

# ── Model singleton ───────────────────────────────────────────────────────────

_model_data = None


def load_model():
    global _model_data
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            _model_data = pickle.load(f)
        print("[ML] Model loaded.")
    else:
        print("[ML] model.pkl not found — run ml/train_model.py first.")


def get_model():
    return _model_data


# ── Core prediction ───────────────────────────────────────────────────────────

def classify_risk(prob: float) -> tuple[str, str]:
    """Return (risk_label, css_class) for a given probability."""
    if prob >= HIGH_RISK_THRESHOLD:
        return "High Risk", "danger"
    elif prob >= MEDIUM_RISK_THRESHOLD:
        return "Medium Risk", "warning"
    return "Low Risk", "success"


def predict(input_data: dict) -> dict:
    """
    Run the model on input_data and return a result dict.
    Raises RuntimeError if the model is not loaded.
    """
    if _model_data is None:
        raise RuntimeError("Model not loaded. Run ml/train_model.py first.")

    model    = _model_data["model"]
    features = _model_data["features"]

    df   = pd.DataFrame([{f: input_data.get(f, 0) for f in features}])
    prob = float(model.predict_proba(df)[0][1])

    risk_label, risk_class = classify_risk(prob)
    confidence = f"{prob * 100:.1f}%"

    return {
        "prediction":   risk_label,
        "risk_class":   risk_class,
        "confidence":   confidence,
        "prob_at_risk": round(prob * 100, 1),
    }


# ── Recommendation helpers ────────────────────────────────────────────────────

def get_recommendations(risk_label: str, data: dict) -> list[str]:
    recs = []

    if risk_label == "High Risk":
        recs += [
            "Immediate consultation with a gynaecologist is strongly advised.",
            "Schedule a Pap smear and colposcopy at the earliest.",
            "Do not delay — early diagnosis significantly improves outcomes.",
        ]
    elif risk_label == "Medium Risk":
        recs += [
            "Consult a gynaecologist within the next few weeks.",
            "A Pap smear test is recommended soon.",
            "Schedule a follow-up within 3–6 months.",
        ]
    else:
        recs += [
            "Continue regular annual gynaecological check-ups.",
            "Next Pap smear recommended within 1–3 years as per guidelines.",
        ]

    if data.get("Smokes", 0) == 1:
        recs.append("Quit smoking — it significantly increases cervical cancer risk.")
    if data.get("STDs:HPV", 0) == 1:
        recs.append("HPV vaccination and regular monitoring are very important.")
    if data.get("Hormonal Contraceptives", 0) == 1:
        recs.append("Discuss long-term contraceptive use with your doctor.")
    if data.get("IUD", 0) == 1:
        recs.append("Periodic IUD check-ups are recommended.")

    recs.append(
        "This tool is for educational purposes and is not a substitute for medical advice."
    )
    return recs


def get_testing_recommendations(risk_label: str, data: dict) -> list[dict]:
    if risk_label == "High Risk":
        tests = [
            {"name": "Pap Smear",            "priority": "Urgent",  "frequency": "Immediately, then every 6 months",      "description": "Detects abnormal cervical cells before they become cancerous.",              "icon": "🔬"},
            {"name": "Colposcopy",            "priority": "Urgent",  "frequency": "As soon as possible",                   "description": "Detailed examination of the cervix using a magnifying instrument.",         "icon": "🔍"},
            {"name": "HPV DNA Test",          "priority": "High",    "frequency": "Immediately",                            "description": "Detects high-risk HPV strains linked to cervical cancer.",                 "icon": "🧬"},
            {"name": "Biopsy",                "priority": "High",    "frequency": "If colposcopy shows abnormalities",      "description": "Tissue sample to check for cancerous or pre-cancerous cells.",            "icon": "🏥"},
            {"name": "STD Screening Panel",   "priority": "High",    "frequency": "Immediately",                            "description": "Full screening for sexually transmitted infections including HIV.",        "icon": "🩺"},
            {"name": "Pelvic Ultrasound",     "priority": "Medium",  "frequency": "As recommended by doctor",              "description": "Imaging to examine the uterus, ovaries and cervix.",                      "icon": "📡"},
        ]
    elif risk_label == "Medium Risk":
        tests = [
            {"name": "Pap Smear",            "priority": "High",    "frequency": "Within 1–3 months, then annually",      "description": "Detects abnormal cervical cells before they become cancerous.",              "icon": "🔬"},
            {"name": "HPV DNA Test",         "priority": "High",    "frequency": "Within 3 months",                       "description": "Detects high-risk HPV strains linked to cervical cancer.",                 "icon": "🧬"},
            {"name": "STD Screening Panel",  "priority": "Medium",  "frequency": "Within 1–3 months",                     "description": "Screening for sexually transmitted infections.",                           "icon": "🩺"},
            {"name": "Pelvic Examination",   "priority": "Medium",  "frequency": "Every 6 months",                        "description": "Physical examination of the pelvic region by a gynaecologist.",           "icon": "👩‍⚕️"},
            {"name": "Colposcopy",           "priority": "Medium",  "frequency": "If Pap smear shows abnormalities",      "description": "Detailed cervical examination if Pap smear results are abnormal.",         "icon": "🔍"},
        ]
    else:
        tests = [
            {"name": "Pap Smear",           "priority": "Routine", "frequency": "Every 1–3 years",                       "description": "Routine screening to detect any early abnormal cervical cells.",            "icon": "🔬"},
            {"name": "HPV Vaccination",     "priority": "Routine", "frequency": "If not yet vaccinated",                  "description": "Gardasil / Cervarix vaccine — highly effective against HPV strains.",     "icon": "💉"},
            {"name": "Pelvic Examination",  "priority": "Routine", "frequency": "Annually",                               "description": "Routine annual gynaecological check-up.",                                  "icon": "👩‍⚕️"},
            {"name": "STD Screening",       "priority": "Routine", "frequency": "As recommended based on lifestyle",      "description": "Basic STD screening as part of annual health check.",                      "icon": "🩺"},
        ]

    if data.get("STDs:HPV", 0) == 1 and risk_label != "High Risk":
        tests.insert(0, {
            "name":        "HPV Genotyping Test",
            "priority":    "High",
            "frequency":   "Immediately",
            "description": "Identifies the specific HPV strain to assess cancer risk level.",
            "icon":        "🧬",
        })

    return tests