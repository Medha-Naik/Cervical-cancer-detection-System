# 🎗️ CervixGuard AI — Cervical Cancer Risk Assessment System

**BCS685 | Acharya Institute of Technology | Dept. of CSE**

## ✨ Features

- **Redesigned UI** — soft teal/violet "awareness ribbon" theme, rounded cards, an animated risk-ring gauge.
- **Dark mode** — toggle in the top nav, persisted per browser.
- **Languages** — English, Hindi and Kannada.
- **Symptom checklist** — optional section on the assessment form (abnormal bleeding, pelvic pain, etc.). It doesn't feed the ML model, but triggers a visible urgency alert and adjusted recommendations, since these symptoms warrant a clinical visit regardless of model score.
- **PDF report download** — every assessment gets a formatted PDF (ReportLab) from the result page or the dashboard history table.
- **Email & print-friendly result page** — "Email summary" opens a pre-filled draft; "Print" uses a dedicated print stylesheet.
- **Dashboard analytics** — stat cards, a risk-distribution donut and an assessments-over-time line chart (Chart.js), plus searchable history with per-row PDF download and delete.
- **Vaccine dose reminders** — HPV dose schedule per patient, calendar (.ics) export, and automatic reminder emails when a dose becomes due.
- **Local chatbot** — rule-based, no external API.

## 📁 Project Structure

```
cervical-cancer-detection/
├── run.py                  ← start the web app
├── train_model.py          ← train the model → model.pkl
├── evaluate.py             ← model evaluation + plots
├── setup_db.py             ← create/migrate the SQLite database
├── view_db.py              ← quick CLI view of stored records
├── requirements.txt
├── .env.example            ← copy to .env for SECRET_KEY / SMTP settings
├── kag_risk_factors_cervical_cancer.csv   ← training dataset
├── model.pkl               ← trained model (regenerate with train_model.py)
└── cervixguard/            ← the application package
    ├── __init__.py         ← create_app() wires everything together
    ├── config.py           ← paths, env vars, risk tiers, symptom list
    ├── db.py               ← connection helper + the single database schema
    ├── translations.py     ← English / Hindi / Kannada strings
    ├── ml/
    │   ├── features.py     ← the 11 model features (single source of truth)
    │   ├── dataset.py      ← CSV cleaning + train/test split
    │   ├── training.py     ← model definition + save/load
    │   └── model.py        ← runtime: load model, predict, classify risk tier
    ├── services/           ← business logic (no Flask objects)
    │   ├── users.py  predictions.py  recommendations.py  chatbot.py
    │   └── vaccine.py  reminders.py  mailer.py  reports.py
    ├── routes/             ← thin Flask blueprints
    │   └── auth.py  assess.py  dashboard.py  vaccine.py  chat.py
    ├── templates/
    └── static/
```

Routes only parse the request and render; anything reusable lives in `services/` or `ml/`.

## 🚀 How to Run

```bash
pip install -r requirements.txt
python setup_db.py      # creates cervical_cancer.db (SQLite, no server needed)
python run.py           # http://localhost:5000
```

The app also creates and migrates the database on startup, so `setup_db.py` is optional.

Optional steps:

```bash
python train_model.py   # retrain; writes model.pkl (a trained one is already included)
python evaluate.py      # confusion matrix, ROC curve, feature importances → evaluation_report.png
python view_db.py       # print stored assessments
```

Dataset: [Kaggle — Cervical Cancer Risk Classification](https://www.kaggle.com/datasets/loveall/cervical-cancer-risk-classification) (already included in the repo).

## 🧠 ML Model

| Property | Value |
|---|---|
| Algorithm | Random Forest |
| Output | Probability → Low / Medium / High (thresholds in `cervixguard/config.py`) |
| Features | 11 health risk factors |
| Class imbalance | SMOTE oversampling |

**Features:** age, number of sexual partners, age at first sexual intercourse, number of pregnancies, smoking status + years, hormonal contraceptives, IUD usage, STD count, HPV diagnosis.

**Symptom checklist** (advisory only, not model inputs): abnormal bleeding · post-intercourse bleeding · unusual discharge · pelvic pain · pain during intercourse.

## 🌐 Routes

| Route | Description |
|---|---|
| `/` | Risk assessment form |
| `/predict` | POST — runs prediction, saves to DB |
| `/dashboard` | Analytics with charts + history table |
| `/vaccine` | HPV vaccine dosing timeline + your registered schedule |
| `/vaccine/register` | POST — registers a vaccination plan |
| `/report/<id>` | Downloads a PDF report for a saved assessment |
| `/api/history` | JSON — all saved assessments |
| `/api/stats` | JSON — risk-tier counts |
| `/api/delete/<id>` | DELETE — removes a saved assessment |
| `/api/chat` | POST — chatbot |

## 💉 Vaccine dose reminder emails

If an account has an email on file, a reminder is sent once for every HPV dose that becomes due and isn't marked done. A background check runs daily inside the Flask process.

Set these in a `.env` file (copy `.env.example`) or as environment variables:

| Variable | Purpose |
|---|---|
| `SMTP_HOST` | Mail server host (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | Defaults to 587 |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | Login for the SMTP account |
| `SMTP_USE_TLS` | `true` (default) or `false` |
| `MAIL_FROM` | From address; defaults to `SMTP_USERNAME` |
| `REMINDER_CHECK_INTERVAL_SECONDS` | Defaults to once every 24 hours |
| `SECRET_KEY` | Flask session secret — set a long random value |

If `SMTP_HOST` isn't set, reminder emails are printed to the console instead, so the app runs fully without mail setup.

## 👥 Team

| Member | USN | Responsibility |
|---|---|---|
| Manya K | 1AY23CS112 | Frontend (HTML/CSS/JS) |
| G. Bhavana | 1AY23CS074 | Data preprocessing + EDA |
| Medha M | 1AY23CS113 | Flask backend + ML integration |
| Priyanka C | 1AY23CS143 | Model training + evaluation + docs |

**Guide:** Anitta Antony, Assistant Professor

## ⚕️ Disclaimer

This system is a decision-support tool built for educational purposes. It is **not** a substitute for professional medical advice or diagnosis.
