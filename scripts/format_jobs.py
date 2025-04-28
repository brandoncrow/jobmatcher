# scripts/format_jobs.py
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
OUT_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    logger.info("Loading configuration...")
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {CONFIG_PATH}")
        raise

def deduplicate(jobs):
    logger.info("Deduplicating jobs...")
    seen = set()
    unique = []
    for job in jobs:
        key = f"{job['title']}|{job['location']}|{job['company']}"
        hash_ = hashlib.md5(key.encode()).hexdigest()
        if hash_ not in seen:
            seen.add(hash_)
            unique.append(job)
    logger.info(f"Found {len(unique)} unique jobs after deduplication.")
    return unique

def is_recent(job, max_days):
    try:
        updated_at = job["updated_at"]
        if "." in updated_at:
            updated_at = updated_at.split(".")[0] + updated_at[-6:]
        job_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S%z")
        return datetime.now(job_date.tzinfo) - job_date <= timedelta(days=max_days)
    except (KeyError, ValueError) as e:
        logger.warning(f"Invalid updated_at for job {job.get('title', 'unknown')}: {e}")
        return False

def score_job(job, keywords, boost_keywords):
    title = job['title'].lower()
    desc = job.get('content', '').lower()
    text = title + " " + desc
    score = sum(1 for kw in keywords if kw.lower() in text)
    score += sum(2 for kw in boost_keywords if kw.lower() in text)
    return score

def normalize(job):
    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "url": job.get("absolute_url") or job.get("url", ""),
        "updated_at": job.get("updated_at", ""),
        "score": 0
    }

def run(jobs):
    logger.info("Starting job formatting and scoring...")
    if not jobs:
        logger.warning("No jobs provided for formatting")
        return []

    config = load_config()
    max_days = config.get("general", {}).get("days_old_max", 1)
    keywords = config.get("filter", {}).get("required_keywords", [])
    boosts = config.get("filter", {}).get("score_boost_keywords", [])

    jobs = deduplicate(jobs)
    jobs = [normalize(job) for job in jobs if is_recent(job, max_days)]

    for job in jobs:
        job["score"] = score_job(job, keywords, boosts)

    jobs = sorted(jobs, key=lambda x: x["score"], reverse=True)

    out_file = OUT_DIR / f"jobs_{datetime.now().strftime('%Y%m%d')}.json"
    try:
        with open(out_file, "w") as f:
            json.dump(jobs, f, indent=2)
        logger.info(f"Saved {len(jobs)} formatted jobs to {out_file}")
    except OSError as e:
        logger.error(f"Failed to save jobs to {out_file}: {e}")
        raise

    return jobs

if __name__ == "__main__":
    from scrape_greenhouse import run as scrape_run
    jobs = scrape_run()
    run(jobs)