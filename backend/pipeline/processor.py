import os
import json
import hashlib
import re

# Only import anthropic if key is available
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USE_AI = bool(ANTHROPIC_API_KEY)

if USE_AI:
    import anthropic
    _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


ANALYSIS_PROMPT = """Analyze this customer support ticket. Reply ONLY with a JSON object, no extra text.

Message: {message}
Product: {product}
Order value: {order_value}
Channel: {channel}

Return this exact structure:
{{
  "category": "<delivery_delay|wrong_item|payment_failed|refund_not_received|account_login|product_quality|cancellation|other>",
  "sentiment": "<frustrated|dissatisfied|neutral|satisfied>",
  "frustration_score": <integer 1-10>,
  "priority": "<high|medium|low>",
  "revenue_risk": <float, estimated revenue at risk>,
  "suggested_response": "<empathetic agent response under 80 words>"
}}

Priority is high if sentiment is frustrated AND order_value > 50, medium for dissatisfied, low otherwise."""


def _rule_based_analysis(ticket: dict) -> dict:
    """Fallback when no API key is set. Uses keyword matching."""
    msg = ticket.get("message", "").lower()

    category = "other"
    keyword_map = [
        (["delay", "late", "arrived", "tracking", "stuck", "shipped"], "delivery_delay"),
        (["wrong item", "incorrect", "different product", "wrong size"], "wrong_item"),
        (["payment", "declined", "card", "checkout", "error"], "payment_failed"),
        (["refund", "money back", "return"], "refund_not_received"),
        (["login", "password", "account", "locked", "sign in"], "account_login"),
        (["broken", "defective", "quality", "damaged", "doesnt work"], "product_quality"),
        (["cancel", "cancellation"], "cancellation"),
    ]
    for keywords, cat in keyword_map:
        if any(k in msg for k in keywords):
            category = cat
            break

    frustrated_words = ["ridiculous", "unacceptable", "terrible", "worst", "disgusting", "!!"]
    dissatisfied_words = ["disappointed", "unhappy", "frustrated", "annoyed", "upset"]

    if any(w in msg for w in frustrated_words):
        sentiment = "frustrated"
        frustration_score = 8
    elif any(w in msg for w in dissatisfied_words):
        sentiment = "dissatisfied"
        frustration_score = 5
    else:
        sentiment = "neutral"
        frustration_score = 3

    order_value = float(ticket.get("order_value", 0))
    priority = "high" if sentiment == "frustrated" and order_value > 50 else \
               "medium" if sentiment in ["frustrated", "dissatisfied"] else "low"

    revenue_risk = order_value if sentiment == "frustrated" else order_value * 0.3 if sentiment == "dissatisfied" else 0

    suggested_response = (
        f"Thank you for reaching out. I am sorry to hear about the issue with your {ticket.get('product', 'order')}. "
        "I am looking into this right now and will get back to you with an update shortly. "
        "We want to make sure this gets resolved for you as quickly as possible."
    )

    return {
        "category": category,
        "sentiment": sentiment,
        "frustration_score": frustration_score,
        "priority": priority,
        "revenue_risk": round(revenue_risk, 2),
        "suggested_response": suggested_response,
    }


def _ai_analysis(ticket: dict) -> dict:
    """Uses Claude API when key is available."""
    prompt = ANALYSIS_PROMPT.format(
        message=ticket.get("message", ""),
        product=ticket.get("product", "unknown"),
        order_value=ticket.get("order_value", 0),
        channel=ticket.get("channel", "unknown"),
    )
    try:
        response = _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        # strip markdown fences if present
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return _rule_based_analysis(ticket)


def analyze_ticket(ticket: dict) -> dict:
    """Entry point — uses AI if available, otherwise rule-based."""
    if USE_AI:
        result = _ai_analysis(ticket)
    else:
        result = _rule_based_analysis(ticket)

    return {
        **ticket,
        "category": result.get("category", "other"),
        "sentiment": result.get("sentiment", "neutral"),
        "frustration_score": result.get("frustration_score", 5),
        "priority": result.get("priority", "medium"),
        "revenue_risk": result.get("revenue_risk", 0.0),
        "suggested_response": result.get("suggested_response", ""),
    }


def analyze_batch(tickets: list[dict]) -> list[dict]:
    results = []
    for ticket in tickets:
        results.append(analyze_ticket(ticket))
    return results
