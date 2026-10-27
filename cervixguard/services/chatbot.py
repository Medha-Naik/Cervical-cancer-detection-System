"""Rule-based, fully local chatbot. No external API calls.

A rule maps a regex to either a fixed reply string or a function taking the user's
last assessment result (or None) and returning a reply.
"""
import re

from .. import config


def _explain_risk(last_result):
    if last_result:
        risk = last_result.get("risk", "your last")
        conf = last_result.get("confidence", "")
        return (f"Your most recent result was **{risk}** with a model confidence of {conf}. "
                "That's a statistical estimate from 11 health factors, not a diagnosis — "
                "check the Recommendations and Suggested Tests on your result page for what to do next.")
    return ("I don't see a recent assessment for you yet — run one from the Assess page and I can "
            "explain exactly what your risk tier means.")


def _next_steps(last_result):
    if last_result and last_result.get("urgent"):
        return "You reported symptoms on your last assessment — please prioritize a clinical evaluation soon, regardless of your risk tier."
    if last_result:
        risk = last_result.get("risk")
        days = config.FOLLOWUP_DAYS.get(risk, config.DEFAULT_FOLLOWUP_DAYS)
        return f"Based on your last result ({risk}), a follow-up within about {days} days is a reasonable target — worth booking with your clinic."
    return "Start with an assessment on the Assess page — I can help interpret your result once you have one."


CHAT_RULES = [
    (r"\b(hi|hello|hey|namaste)\b", "Hi! I'm the CervixGuard assistant. Ask me about your risk result, Pap smears, HPV, the vaccine, or what to do next."),
    (r"\b(risk tier|what does my (result|risk) mean|what does .*(low|medium|high) risk mean)\b", _explain_risk),
    (r"\b(pap smear|pap test)\b",
     "A Pap smear checks cervical cells for early abnormal changes, years before they could become cancer. It's quick, done in a clinic, and the single most effective cervical cancer screening tool we have."),
    (r"\bhpv\b.*\b(test|dna)\b",
     "An HPV DNA test checks for the high-risk HPV strains that cause most cervical cancers. It's often done alongside or instead of a Pap smear, depending on your age and guidelines."),
    (r"\b(hpv)\b",
     "HPV (human papillomavirus) is a very common virus; most infections clear on their own, but persistent high-risk strains can lead to cervical cancer over time. Vaccination and regular screening are the best defenses."),
    (r"\b(vaccine|vaccination|gardasil|cervarix)\b",
     "The HPV vaccine protects against the strains responsible for most cervical cancers. It's most effective before HPV exposure, but catch-up doses are available up to age 45 — check the Vaccine page for the full dosing schedule."),
    (r"\b(colposcopy)\b",
     "A colposcopy is a closer, magnified examination of the cervix, usually done as a follow-up when a Pap smear shows abnormal cells."),
    (r"\b(biopsy)\b",
     "A biopsy takes a small tissue sample from the cervix to check under a microscope for pre-cancerous or cancerous cells — usually done if a colposcopy shows something abnormal."),
    (r"\b(symptom|bleeding|discharge|pelvic pain|pain during sex|pain during intercourse)\b",
     "Symptoms like abnormal bleeding, unusual discharge, or pelvic pain are worth a clinical evaluation regardless of any risk score — they aren't something a model like this one can safely rule out."),
    (r"\b(next step|what should i do|what now|what next)\b", _next_steps),
    (r"\b(appointment|book|schedule|follow.?up)\b",
     "It's worth booking a follow-up with a clinician — your result page shows a suggested timeframe based on your risk tier."),
    (r"\b(accurate|reliable|trust|how good is)\b.*\b(model|prediction|this)\b",
     "This model was trained on a public clinical dataset and reaches roughly 95% accuracy in testing, but it's a screening aid, not a diagnosis — always confirm results with a real clinician."),
    (r"\b(thank|thanks|thank you)\b", "You're welcome! Take care of yourself, and don't hesitate to see a doctor if anything feels off."),
    (r"\b(bye|goodbye)\b", "Take care! Your assessments are always saved on your Dashboard if you want to revisit them."),
]

EMPTY_MESSAGE_REPLY = "Ask me anything about your result, Pap smears, HPV, the vaccine, or next steps."

FALLBACK_REPLY = ("I'm a simple local assistant, so I can only help with cervical health topics — "
                  "try asking about your risk result, Pap smears, HPV, the vaccine, symptoms, or next steps.")


def chatbot_reply(message, last_result):
    msg = message.lower().strip()
    for pattern, reply in CHAT_RULES:
        if re.search(pattern, msg):
            return reply(last_result) if callable(reply) else reply
    return FALLBACK_REPLY
