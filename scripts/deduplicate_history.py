import json
from pathlib import Path
from datetime import datetime
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
ARCHIVE_DIR = DATA_DIR / 'archive'

MASTER_FILE = ARCHIVE_DIR / 'jobs_master.json'

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def hash_job(job):
    key = f"{job['title']}|{job['company']}|{job['location']}"
    return hashlib.md5(key.encode()).hexdigest()

def run():
    logger.info("Starting historical deduplication...")

    # Load today's jobs
    today_str = datetime.now().strftime("%Y%m%d")
    today_file = PROCESSED_DIR / f"jobs_{today_str}.json"

    if not today_file.exists():
        logger.error(f"No jobs file found for today: {today_file}")
        return []

    today_jobs = load_json(today_file)

    # Load master historical jobs
    if MASTER_FILE.exists():
        historical_jobs = load_json(MASTER_FILE)
    else:
        historical_jobs = []

    # Build sets for quick lookup
    seen_hashes = {hash_job(job) for job in historical_jobs}

    # Filter today's jobs
    new_jobs = []
    for job in today_jobs:
        job_hash = hash_job(job)
        if job_hash not in seen_hashes:
            new_jobs.append(job)
            seen_hashes.add(job_hash)

    logger.info(f"Found {len(new_jobs)} new unique jobs today.")

    # Save updated today's jobs
    save_json(today_file, new_jobs)

    # Update master archive
    updated_historical_jobs = historical_jobs + new_jobs
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    save_json(MASTER_FILE, updated_historical_jobs)

    logger.info(f"Updated master archive with {len(updated_historical_jobs)} total jobs.")
    return new_jobs

if __name__ == "__main__":
    run()