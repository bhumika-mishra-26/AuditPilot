import re

def classify_task_keywords(user_task: str) -> dict:
    """
    Keyword-based classification for AuditPilot tasks.
    Used as a fallback for the LLM classifier or as a lightweight alternative.
    """
    task_lower = user_task.lower()

    w1_keywords = [
        "onboard", "register", "add client", "new client",
        "sign up", "enroll", "create account", "kyc",
    ]
    w2_keywords = [
        "pay", "payment", "purchase order", "po", "invoice",
        "vendor", "procurement", "approve", "transaction",
        "pay to", "process payment", "settle",
    ]
    w3_keywords = [
        "meeting", "notes", "assign task", "action item",
        "task", "minute", "discussed", "follow up",
        "sprint", "standup", "sync",
    ]

    w1_score = sum(1 for k in w1_keywords if k in task_lower)
    w2_score = sum(1 for k in w2_keywords if k in task_lower)
    w3_score = sum(1 for k in w3_keywords if k in task_lower)
    total    = w1_score + w2_score + w3_score

    if total == 0:
        return {
            "route"     : "unclear",
            "confidence": 0.0,
            "extracted" : {},
            "is_multi"  : False,
            "routes"    : [],
            "reason"    : "No matching keywords found",
        }

    scores   = {"W1": w1_score, "W2": w2_score, "W3": w3_score}
    active   = sorted([k for k, v in scores.items() if v > 0])
    is_multi = len(active) >= 2
    best     = max(scores, key=scores.get)
    conf     = round(scores[best] / max(total, 1), 2)

    # extract name hint — words after trigger keywords
    extracted = {}
    words = user_task.split()
    for i, w in enumerate(words):
        if w.lower() in ("onboard", "register", "pay", "to") and i + 1 < len(words):
            extracted["name_hint"] = " ".join(words[i+1:i+3])

    # extract amount hint — any number in the sentence
    amounts = re.findall(r'\b\d[\d,]*\b', user_task)
    if amounts:
        extracted["amount_hint"] = amounts[-1].replace(",", "")

    reason = (
        f"Multi-task detected — will run {' then '.join(active)}"
        if is_multi else
        f"Matched {scores[best]} {best} keyword(s) in your task"
    )

    # construct task_list for consistency
    task_list = []
    if is_multi:
        for r in active:
            task_list.append({"route": r, "extracted_params": extracted if r == best else {}})
    else:
        task_list = [{"route": best, "extracted_params": extracted}]

    return {
        "route"     : best,
        "confidence": conf,
        "extracted_params" : extracted,
        "is_multi"  : is_multi,
        "routes"    : active,
        "task_list" : task_list,
        "reason"    : reason,
    }
