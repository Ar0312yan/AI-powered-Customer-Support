# Design Document

## What this is

A system that ingests e-commerce support tickets, runs them through an AI pipeline to classify and analyze them, and shows the results in a dashboard. Built for the AI/ML Software Dev assignment.

---

## Stack choices and why

**Backend: FastAPI**
FastAPI was the obvious pick for a Python-first project. It auto-generates API docs at /docs which is useful for the demo, and it is fast enough for this scale without needing async complexity.

**Database: SQLite**
Deliberately chose SQLite over PostgreSQL to keep setup simple — no installation, no credentials, just a file. For a production system with multiple servers you would switch to PostgreSQL. The query patterns here (GROUP BY, COUNT, WHERE filters) work the same in both.

**Frontend: Streamlit**
Streamlit lets you build a working dashboard in pure Python. No JavaScript, no separate build step, no npm. For a project like this where the data work is the main point, it makes sense to not spend time fighting with frontend tooling.

**AI: Claude API (with rule-based fallback)**
The processor does classification and sentiment in a single API call returning structured JSON. One call per ticket instead of two saves about half the token cost. When no API key is set, the system falls back to keyword-based classification so everything still runs and the architecture can be demonstrated without spend.

---

## Data pipeline

```
CSV file
   |
   v
Clean and normalize (fix encoding, cast types, truncate long messages)
   |
   v
AI analysis (Claude Haiku or rule-based fallback)
   - category: what type of issue is this
   - sentiment: how frustrated is the customer
   - frustration_score: 1-10
   - priority: high / medium / low
   - revenue_risk: estimated order value at risk
   - suggested_response: what the agent should reply
   |
   v
SQLite database
   |
   v
FastAPI endpoints
   |
   v
Streamlit dashboard
```

---

## AI approach

The prompt asks the model to return a strict JSON object with no extra text. This avoids parsing issues. The model is given the ticket message, product, order value, and channel. From that it can infer:

- Category — keyword patterns in the message
- Sentiment — tone and word choice
- Priority — combination of sentiment and order value (a frustrated customer on a $200 order is higher priority than a neutral one on a $20 order)
- Revenue risk — estimated based on order value and sentiment

The rule-based fallback uses the same logic manually with keyword lists. It is less accurate but makes the app fully functional without an API key, which matters during development and demos.

---

## Three insights that matter to leadership

**1. Revenue at risk**
Frustrated customers on high-value orders are the ones most likely to churn and leave bad reviews. Tracking total revenue at risk (frustrated tickets × order value) gives finance a number to work with.

**2. Which categories are growing**
A 40% week-on-week spike in wrong_item tickets is probably a warehouse or fulfillment problem, not a customer service problem. Catching this early from ticket data is faster than waiting for returns data.

**3. Agent response quality**
If suggested responses are accepted by agents 60%+ of the time, that is measurable deflection. If acceptance is low, the suggestions are off and the prompt needs tuning.

---

## How this reduces support costs

- Suggested responses cut average handle time. An agent who starts with a good draft reply finishes faster.
- High-priority routing means senior agents spend time on the tickets that actually matter (high order value, frustrated customers).
- Anomaly detection catches operational problems before they compound into hundreds more tickets.

---

## Metrics to track

- Ticket volume by category week over week
- Frustrated customer percentage
- Average frustration score
- Revenue at risk total
- Resolution rate by category
- High priority ticket count

---

## What I would add with more time

- A proper vector database for semantic search so agents can find similar past tickets
- Multilingual support (detect language, translate before analysis)
- Email or Slack alerts when a category spikes
- Fine-tuned classifier to reduce API cost at high volume
- PostgreSQL for production instead of SQLite
