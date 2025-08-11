# HR Attrition Intelligence

An ETL pipeline that scrapes public employee reviews, generates dummy internal HRMS data, enriches reviews with HRMS attributes, and persists the results to CSV backups and a SQLite database.

## Features
- Incremental scraping with page checkpointing
- Consistent CSV backups with timestamped versions
- Synthetic HRMS data generation aligned to scraped volume
- Merge/enrichment of reviews with HRMS attributes
- SQLite storage with a simple schema
- Optional daily scheduler for automation

## Project Structure
```
.
├── data/                     # CSVs and SQLite DB live here
├── etl/
│   ├── scraper.py            # Scrapes reviews (incremental)
│   ├── hrms_generator.py     # Generates/extends HRMS dummy dataset
│   ├── merger.py             # Enriches reviews with HRMS attributes + writes to SQLite
│   └── utils.py              # Shared helpers (backup + save)
├── sql/
│   └── schema.sql            # SQLite schema for merged_data
├── main.py                   # Orchestrates ETL: scraper -> hrms -> merger
├── scheduler.py              # Simple schedule-based runner (local)
├── scripts/                  # Legacy/auxiliary scripts (Drive/Sheets, etc.)
├── requirements.txt
└── README.md
```

## Quickstart

### 1) Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Initialize the database schema
```bash
python setup_db.py
```
This creates `data/hr_analytics.db` and the `merged_data` table.

### 3) Run the ETL pipeline
```bash
python main.py
```
The pipeline runs the following steps:
1. `etl/scraper.py` scrapes reviews and appends to `data/<company>_reviews.csv` with timestamped backups under `Backup/reviews/`.
2. `etl/hrms_generator.py` generates or extends `data/hrms_latest.csv` and backs up under `Backup/hrms/`.
3. `etl/merger.py` enriches new reviews and writes to `data/reviews_enriched_latest.csv`, appending only new rows to SQLite.

Outputs:
- CSVs in `data/`
- Backups in `Backup/`
- SQLite DB at `data/hr_analytics.db`

## Configuration
- Company slug and scrape parameters are currently set in `etl/scraper.py` (default example: `nineleaps-technology-solutions`).
- Adjust `num_pages` and `delay` as needed (or we can externalize them to CLI flags upon request).

## Scheduling
Run locally on a schedule using the simple scheduler:
```bash
python scheduler.py
```
- By default it schedules one run per day (see code for exact time).
- For production/servers, prefer `cron` or a workflow runner and target `python main.py`.

## Logs
- Prints to console. You can redirect output to files if needed or run under a process manager/cron for logging.

## Notes and Next Steps
- The scraper currently disables TLS verification in requests; consider enabling verification and adding retry/backoff.
- `scripts/` contains legacy utilities and Google integrations; they are optional.
- We can add CLI flags/config, structured logging, and DB upsert safeguards if you’d like.

## License
Private/internal project. Add a license here if you intend to open source.
