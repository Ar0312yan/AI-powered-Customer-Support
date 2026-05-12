# Deploying to Render

This guide walks through deploying the backend API to Render's free tier.
The Streamlit dashboard can be deployed separately to Streamlit Community Cloud.

---

## Part 1 — Deploy the backend API on Render

### Step 1: Push your code to GitHub first
Make sure your code is on GitHub before starting. Render deploys directly from GitHub.

### Step 2: Create a Render account
Go to https://render.com and sign up with your GitHub account.

### Step 3: Create a new Web Service
- Click "New" → "Web Service"
- Connect your GitHub repository
- Give it a name like `supportiq-api`

### Step 4: Configure the service

Set these fields:

| Field | Value |
|-------|-------|
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

### Step 5: Add environment variables
In the "Environment" tab, add:

```
ANTHROPIC_API_KEY = your_key_here
```

If you do not have a key yet, skip this. The app will still run with rule-based analysis.

### Step 6: Deploy
Click "Create Web Service". Render will build and deploy automatically.
Your API will be available at something like `https://supportiq-api.onrender.com`

**Note on free tier:** Render's free tier spins down after 15 minutes of inactivity.
The first request after that takes about 30 seconds to respond. This is normal.

---

## Part 2 — Deploy the dashboard on Streamlit Community Cloud

Streamlit has its own free hosting that works well for Streamlit apps.

### Step 1: Go to share.streamlit.io
Sign in with your GitHub account.

### Step 2: Deploy an app
- Click "New app"
- Select your repository
- Set main file path to `frontend/dashboard.py`

### Step 3: Update the API URL
Before deploying, update the `API` variable in `frontend/dashboard.py`:

```python
# Change this line:
API = "http://localhost:8000"

# To your Render URL:
API = "https://supportiq-api.onrender.com"
```

Commit and push that change, then deploy.

### Step 4: Add secrets (optional)
If you want the dashboard to pass an API key, add it in
Streamlit's secrets management under App Settings.

---

## Checking if it works

Once both are deployed:

1. Visit your Streamlit URL
2. Go to the Upload tab
3. Generate a dataset and upload it
4. Switch to Overview to see the dashboard populate

The API docs are also available at `https://your-render-url.onrender.com/docs`

---

## Troubleshooting

**Build fails on Render**
Check that `requirements.txt` is in the root of the repo, not inside a subfolder.

**Dashboard shows API error**
Make sure the API URL in `dashboard.py` matches your Render URL exactly, no trailing slash.

**Render service keeps sleeping**
This is a free tier limitation. Consider upgrading to the Starter plan ($7/month) for always-on hosting, or use a service like UptimeRobot to ping it every 10 minutes.
