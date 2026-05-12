import csv
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from models.database import save_tickets, query, count
from pipeline.processor import analyze_batch, analyze_ticket

router = APIRouter()


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Please upload a CSV file")

    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    raw_tickets = list(reader)

    if len(raw_tickets) > 50000:
        raise HTTPException(400, "Max 50,000 tickets per upload")

    enriched = analyze_batch(raw_tickets)
    save_tickets(enriched)

    return {
        "message": f"Processed and saved {len(enriched)} tickets",
        "count": len(enriched)
    }


@router.post("")
def create_ticket(ticket: dict):
    enriched = analyze_ticket(ticket)
    save_tickets([enriched])
    return enriched


@router.get("")
def get_tickets(limit: int = 20, offset: int = 0, category: str = None, sentiment: str = None):
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)
    if sentiment:
        conditions.append("sentiment = ?")
        params.append(sentiment)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = query(
        f"SELECT * FROM tickets {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    )
    return {"tickets": rows, "total": count()}


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str):
    rows = query("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    if not rows:
        raise HTTPException(404, "Ticket not found")
    return rows[0]
