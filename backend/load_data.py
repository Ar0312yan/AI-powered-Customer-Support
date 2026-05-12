import csv
import sys
import os

# Build the path to data/tickets.csv from the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(project_root, 'data', 'tickets.csv')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db, save_tickets, count
from pipeline.processor import analyze_batch

init_db()

print(f'Looking for CSV at: {csv_path}')

if count() == 0:
    with open(csv_path, encoding='utf-8') as f:
        tickets = list(csv.DictReader(f))
    print(f'Processing {len(tickets)} tickets...')
    enriched = analyze_batch(tickets)
    save_tickets(enriched)
    print(f'Done. Loaded {len(enriched)} tickets.')
else:
    print(f'Database already has {count()} tickets, skipping.')