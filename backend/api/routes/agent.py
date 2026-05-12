import os
from fastapi import APIRouter, HTTPException
from models.database import query

router = APIRouter()

USE_AI = bool(os.getenv("ANTHROPIC_API_KEY", ""))


@router.post("/ask")
def ask(body: dict):
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(400, "question field required")

    # Pull relevant tickets as context
    recent = query("""
        SELECT category, sentiment, message, suggested_response
        FROM tickets
        ORDER BY frustration_score DESC
        LIMIT 5
    """)

    if not USE_AI:
        return {
            "answer": "AI agent requires an Anthropic API key. Set ANTHROPIC_API_KEY in your .env file to enable this feature.",
            "note": "Rule-based analysis is still running for all other features."
        }

    import anthropic
    client = anthropic.Anthropic()

    context = "\n".join([
        f"- [{r['category']}] {r['message'][:100]}" for r in recent
    ])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": f"You are a support team assistant. Answer this question based on recent ticket data.\n\nRecent tickets:\n{context}\n\nQuestion: {question}"
        }]
    )
    return {"answer": response.content[0].text}


@router.get("/weekly-report")
def weekly_report():
    summary = query("""
        SELECT category, COUNT(*) as count,
               ROUND(AVG(frustration_score), 1) as avg_frustration,
               ROUND(SUM(revenue_risk), 2) as revenue_risk
        FROM tickets
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY category
        ORDER BY count DESC
    """)

    total = query("SELECT COUNT(*) as c FROM tickets WHERE timestamp >= datetime('now', '-7 days')")
    frustrated = query("""
        SELECT COUNT(*) as c FROM tickets
        WHERE sentiment = 'frustrated'
        AND timestamp >= datetime('now', '-7 days')
    """)

    total_count = total[0]["c"] if total else 0
    frustrated_count = frustrated[0]["c"] if frustrated else 0
    frustrated_pct = round(frustrated_count / total_count * 100, 1) if total_count else 0

    if not USE_AI:
        return {
            "period": "Last 7 days",
            "total_tickets": total_count,
            "frustrated_pct": frustrated_pct,
            "top_categories": summary,
            "report": "Enable AI by setting ANTHROPIC_API_KEY for a natural language summary.",
        }

    import anthropic
    client = anthropic.Anthropic()

    data_str = "\n".join([
        f"- {r['category']}: {r['count']} tickets, avg frustration {r['avg_frustration']}/10, revenue risk ${r['revenue_risk']}"
        for r in summary
    ])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Write a short weekly support summary for leadership. Be direct and practical.\n\nData:\nTotal tickets: {total_count}\nFrustrated customers: {frustrated_pct}%\n{data_str}\n\nFormat: 3 key insights, 2 recommended actions. Keep it under 200 words."
        }]
    )

    return {
        "period": "Last 7 days",
        "total_tickets": total_count,
        "frustrated_pct": frustrated_pct,
        "top_categories": summary,
        "report": response.content[0].text,
    }
