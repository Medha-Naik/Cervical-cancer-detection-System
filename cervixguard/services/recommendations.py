"""Personalised advice and the suggested-tests table shown on the result page and in the PDF."""

_SYMPTOM_ADVICE = ("You reported symptoms that warrant a clinical evaluation regardless of risk tier "
                   "— please book a gynaecologist visit soon.")

_ADVICE_BY_TIER = {
    "High Risk": [
        "Immediate consultation with a gynaecologist is strongly advised.",
        "Schedule a Pap smear and colposcopy at the earliest.",
        "Do not delay - early diagnosis significantly improves outcomes.",
    ],
    "Medium Risk": [
        "Consult a gynaecologist within the next few weeks.",
        "A Pap smear test is recommended soon.",
        "Schedule a follow-up within 3-6 months.",
    ],
    "Low Risk": [
        "Continue regular annual gynaecological check-ups.",
        "Next Pap smear recommended within 1-3 years as per guidelines.",
    ],
}

# (input flag, extra advice when that flag == 1)
_ADVICE_BY_FACTOR = [
    ("Smokes", "Quit smoking - it significantly increases cervical cancer risk."),
    ("STDs:HPV", "HPV vaccination and regular monitoring are very important."),
    ("Hormonal Contraceptives", "Discuss long-term contraceptive use with your doctor."),
    ("IUD", "Periodic IUD check-ups are recommended."),
]

_DISCLAIMER = "This tool is for educational purposes and not a substitute for medical advice."


def get_recommendations(risk_label, data, symptoms=None):
    symptoms = symptoms or {}
    recs = []
    if any(symptoms.values()):
        recs.append(_SYMPTOM_ADVICE)
    recs += _ADVICE_BY_TIER.get(risk_label, _ADVICE_BY_TIER["Low Risk"])
    recs += [advice for factor, advice in _ADVICE_BY_FACTOR if data.get(factor, 0) == 1]
    recs.append(_DISCLAIMER)
    return recs


# ── Suggested tests ──

# Test name -> (emoji, default description)
_TESTS = {
    "Pap Smear": ("🔬", "Detects abnormal cervical cells before they become cancerous."),
    "Colposcopy": ("🔍", "Detailed examination of the cervix using a magnifying instrument."),
    "HPV DNA Test": ("🧬", "Detects high-risk HPV strains linked to cervical cancer."),
    "HPV Genotyping Test": ("🧬", "Identifies the specific HPV strain to assess cancer risk level."),
    "Biopsy": ("🏥", "Tissue sample to check for cancerous or pre-cancerous cells."),
    "STD Screening Panel": ("🩺", "Full screening for sexually transmitted infections including HIV."),
    "STD Screening": ("🩺", "Basic STD screening as part of annual health check."),
    "Pelvic Ultrasound": ("📡", "Imaging to examine the uterus, ovaries and cervix."),
    "Pelvic Examination": ("👩‍⚕️", "Physical examination of the pelvic region by a gynaecologist."),
    "HPV Vaccination": ("💉", "Gardasil / Cervarix vaccine - highly effective against HPV strains."),
}

# Tier -> rows of (test name, priority, frequency[, description override])
_TESTS_BY_TIER = {
    "High Risk": [
        ("Pap Smear", "Urgent", "Immediately, then every 6 months"),
        ("Colposcopy", "Urgent", "As soon as possible"),
        ("HPV DNA Test", "High", "Immediately"),
        ("Biopsy", "High", "If colposcopy shows abnormalities"),
        ("STD Screening Panel", "High", "Immediately"),
        ("Pelvic Ultrasound", "Medium", "As recommended by doctor"),
    ],
    "Medium Risk": [
        ("Pap Smear", "High", "Within 1-3 months, then annually"),
        ("HPV DNA Test", "High", "Within 3 months"),
        ("STD Screening Panel", "Medium", "Within 1-3 months",
         "Screening for sexually transmitted infections."),
        ("Pelvic Examination", "Medium", "Every 6 months"),
        ("Colposcopy", "Medium", "If Pap smear shows abnormalities",
         "Detailed cervical examination if Pap smear results are abnormal."),
    ],
    "Low Risk": [
        ("Pap Smear", "Routine", "Every 1-3 years",
         "Routine screening to detect any early abnormal cervical cells."),
        ("HPV Vaccination", "Routine", "If not yet vaccinated"),
        ("Pelvic Examination", "Routine", "Annually",
         "Routine annual gynaecological check-up."),
        ("STD Screening", "Routine", "As recommended based on lifestyle"),
    ],
}


def _test_entry(name, priority, frequency, description=None):
    icon, default_description = _TESTS[name]
    return {"name": name, "priority": priority, "frequency": frequency,
            "description": description or default_description, "icon": icon}


def get_testing_recommendations(risk_label, data):
    # Anything that isn't High/Medium falls back to the Low Risk list, as before.
    rows = _TESTS_BY_TIER.get(risk_label, _TESTS_BY_TIER["Low Risk"])
    tests = [_test_entry(*row) for row in rows]
    if data.get("STDs:HPV", 0) == 1 and risk_label != "High Risk":
        tests.insert(0, _test_entry("HPV Genotyping Test", "High", "Immediately"))
    return tests
