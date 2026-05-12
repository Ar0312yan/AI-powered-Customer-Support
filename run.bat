@echo off
echo Starting SupportIQ...
echo.

if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Setting up database...
cd backend
python -c "from models.database import init_db, count; from pipeline.processor import analyze_batch; from models.database import save_tickets; import csv; init_db(); print('DB ready, tickets:', count())"
cd ..

echo Generating dataset...
if not exist "data\tickets.csv" (
    cd backend
    python generate_dataset.py --output "..\data\tickets.csv"
    cd ..
)

echo.
echo Loading tickets into database...
cd backend
python load_data.py
cd ..

echo.
echo Starting backend API...
start cmd /k "call ..\venv\Scripts\activate.bat && cd backend && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo Starting dashboard...
start cmd /k "call ..\venv\Scripts\activate.bat && cd frontend && streamlit run dashboard.py --server.port 8501"

echo.
echo =============================================
echo SupportIQ is running!
echo.
echo Dashboard: http://localhost:8501
echo API docs:  http://localhost:8000/docs
echo =============================================
echo.
pause