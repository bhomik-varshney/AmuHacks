def detect_financial_intent(text: str):
    t = text.lower()

    if any(x in t for x in ["scam","fraud","hacked"]):
        return "fraud","fraud_shock"

    if any(x in t for x in ["loan","emi","debt"]):
        return "debt","debt_shock"

    if any(x in t for x in ["salary","not paid"]):
        return "salary_issue","income_shock"

    if any(x in t for x in ["lost money","crypto","trading loss"]):
        return "financial_loss","asset_shock"

    if any(x in t for x in ["job lost","laid off"]):
        return "job_loss","income_shock"

    return "financial_loss","income_shock"
