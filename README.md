# SupportIQ

A customer support analytics tool built for the AI/ML Software Dev assignment.

It takes support ticket data, runs it through an AI classification pipeline, and shows the results in a dashboard — top issues, sentiment trends, ticket summaries, and suggested agent responses.

---

## What it does

- Generates a synthetic dataset of 10,000 e-commerce support tickets
- Classifies each ticket by category (delivery delay, wrong item, payment issue, etc.)
- Scores sentiment and frustration level
- Suggests a response for the support agent
- Shows everything in a Streamlit dashboard with charts and filters

---

## Stack

- **Backend:** FastAPI + SQLite
- **AI:** Claude API (falls back to rule-based analysis if no key is set)
- **Frontend:** Streamlit
- **Language:** Python only, no JavaScript needed

Kept the stack simple on purpose — SQLite means no database setup, Streamlit means no frontend build step. Everything runs with just Python.

---

## Running locally on Windows

### Requirements
- Python 3.10 or higher

### Setup

```
git clone https://github.com/your-username/supportiq
cd supportiq
```

Copy the environment file and add your API key if you have one:
```
copy .env.example .env
```
Then open `.env` and replace `your_key_here` with your Anthropic API key.
If you do not have a key the app still works, it just uses rule-based classification instead.

### Start everything

Double-click `run.bat` or run it from the terminal:
```
run.bat
```

This will:
1. Create a virtual environment
2. Install dependencies
3. Generate a dataset if one does not exist
4. Load the data into the database
5. Start the API on port 8000
6. Start the dashboard on port 8501

Then open `http://localhost:8501` in your browser.

API docs are at `http://localhost:8000/docs`

---

## Project structure

```
supportiq/
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── generate_dataset.py      # Creates synthetic ticket data
│   ├── api/routes/
│   │   ├── tickets.py           # Upload and browse tickets
│   │   ├── insights.py          # Dashboard metrics and trends
│   │   └── agent.py             # Suggested responses and weekly report
│   ├── pipeline/
│   │   └── processor.py         # AI analysis pipeline
│   └── models/
│       └── database.py          # SQLite setup and queries
├── frontend/
│   └── dashboard.py             # Streamlit dashboard
├── docs/
│   ├── DESIGN.md                # Design decisions and architecture
│   └── DEPLOYMENT.md            # How to deploy to Render
├── requirements.txt
├── run.bat                      # Windows startup script
└── .env.example
```

---

## API endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| POST | `/api/tickets/upload` | Upload a CSV of tickets |
| POST | `/api/tickets` | Add a single ticket |
| GET | `/api/tickets` | List tickets with filters |
| GET | `/api/insights/summary` | Dashboard metrics |
| GET | `/api/insights/trends` | Weekly volume by category |
| GET | `/api/insights/top-issues` | Top issue categories |
| GET | `/api/insights/anomalies` | Spike detection |
| POST | `/api/agent/ask` | Ask a question about the data |
| GET | `/api/agent/weekly-report` | Generate a weekly summary |

---

## Deployment

See `docs/DEPLOYMENT.md` for step-by-step instructions to deploy the backend on Render and the dashboard on Streamlit Community Cloud. Both have free tiers.

---

## Without an API key

The app is fully functional without an Anthropic API key. Classification and sentiment use keyword-based rules instead of the LLM. The suggested responses are templated rather than generated. All charts, filters, and the weekly report still work.

To enable the AI features, sign up at console.anthropic.com and add your key to `.env`.
