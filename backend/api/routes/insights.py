from fastapi import APIRouter
from models.database import query, count

router = APIRouter()


@router.get("/summary")
def summary():
    total = count()

    categories = query("""
        SELECT category, COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets), 1) as pct
        FROM tickets
        GROUP BY category
        ORDER BY count DESC
    """)

    sentiment = query("""
        SELECT sentiment, COUNT(*) as count
        FROM tickets
        GROUP BY sentiment
        ORDER BY count DESC
    """)

    avg_frustration = query("SELECT ROUND(AVG(frustration_score), 1) as avg FROM tickets")
    revenue_risk = query("SELECT ROUND(SUM(revenue_risk), 2) as total FROM tickets")
    high_priority = query("SELECT COUNT(*) as count FROM tickets WHERE priority = 'high'")

    return {
        "total_tickets": total,
        "avg_frustration": avg_frustration[0]["avg"] if avg_frustration else 0,
        "total_revenue_risk": revenue_risk[0]["total"] if revenue_risk else 0,
        "high_priority_count": high_priority[0]["count"] if high_priority else 0,
        "categories": categories,
        "sentiment_distribution": sentiment,
    }


@router.get("/trends")
def trends():
    weekly = query("""
        SELECT
            strftime('%Y-W%W', timestamp) as week,
            category,
            COUNT(*) as count
        FROM tickets
        WHERE timestamp IS NOT NULL
        GROUP BY week, category
        ORDER BY week
    """)
    return {"weekly_trends": weekly}


@router.get("/top-issues")
def top_issues():
    issues = query("""
        SELECT
            category,
            COUNT(*) as count,
            ROUND(AVG(frustration_score), 1) as avg_frustration,
            ROUND(SUM(revenue_risk), 2) as total_revenue_risk,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets), 1) as pct
        FROM tickets
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10
    """)
    return {"issues": issues}


@router.get("/channels")
def channels():
    data = query("""
        SELECT channel, COUNT(*) as count,
               ROUND(AVG(frustration_score), 1) as avg_frustration
        FROM tickets
        GROUP BY channel
        ORDER BY count DESC
    """)
    return {"channels": data}


@router.get("/anomalies")
def anomalies():
    # Simple spike detection: categories with count > 1.5x their average week
    spikes = query("""
        WITH weekly AS (
            SELECT category,
                   strftime('%Y-W%W', timestamp) as week,
                   COUNT(*) as cnt
            FROM tickets
            GROUP BY category, week
        ),
        stats AS (
            SELECT category,
                   AVG(cnt) as avg_count,
                   MAX(cnt) as max_count
            FROM weekly
            GROUP BY category
        )
        SELECT category, avg_count, max_count,
               ROUND((max_count - avg_count) / avg_count * 100, 1) as spike_pct
        FROM stats
        WHERE max_count > avg_count * 1.5
        ORDER BY spike_pct DESC
    """)
    return {"anomalies": spikes}
