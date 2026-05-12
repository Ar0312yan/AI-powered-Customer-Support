from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import tickets, insights, agent
from models.database import init_db

app = FastAPI(title="SupportIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "message": "SupportIQ API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
