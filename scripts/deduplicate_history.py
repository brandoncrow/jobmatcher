# scripts/deduplicate_history.py
import json
from pathlib import Path
from datetime import datetime
import hashlib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
ARCHIVE_DIR = DATA_DIR / 'archive'

MASTER_FILE = ARCHIVE_DIR / 'jobs_master.json'

def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return []

def save_json(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        raise

def hash_job(job):
    key = f"{job['title']}|{job['company']}|{job['location']}"
    return hashlib.md5(key.encode()).hexdigest()

def run(jobs):
    logger.info("Starting historical deduplication...")

    if not jobs:
        logger.warning("No jobs provided for deduplication")
        return []

    # Load master historical jobs
    historical_jobs = load_json(MASTER_FILE)

    # Build set for quick lookup
    seen_hashes = {hash_job(job) for job in historical_jobs}

    # Filter new jobs
    new_jobs = []
    for job in jobs:
        job_hash = hash_job(job)
        if job_hash not in seen_hashes:
            new_jobs.append(job)
            seen_hashes.add(job_hash)

    logger.info(f"Found {len(new_jobs)} new unique jobs.")

    # Save new jobs for today
    today_str = datetime.now().strftime("%Y%m%d")
    today_file = PROCESSED_DIR / f"jobs_{today_str}.json"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    save_json(today_file, new_jobs)

    # Update master archive
    updated_historical_jobs = historical_jobs + new_jobs
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    save_json(MASTER_FILE, updated_historical_jobs)

    logger.info(f"Updated master archive with {len(updated_historical_jobs)} total jobs.")
    return new_jobs

if __name__ == "__main__":
    # For testing only
    today_str = datetime.now().strftime("%Y%m%d")
    today_file = PROCESSED_DIR / f"jobs_{today_str}.json"
    jobs = load_json(today_file)
    run(jobs)