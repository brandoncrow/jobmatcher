import requests
import yaml
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).resolve().parents[1] / "logs" / f"scrape_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
OUT_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)
    
def get_jobs_from_company(board_token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs", [])
        for job in jobs:
            job["company"] = {"name": board_token.capitalize()}
        logger.info(f"Pulled {len(jobs)} jobs from {board_token}")
        return jobs
    except Exception as e:
        logger.error(f"Error fetching jobs from {board_token}: {e}")
        return []

def filter_jobs(jobs, keywords):
    matched = [
        job for job in jobs
        if any(kw.lower() in job["title"].lower() for kw in keywords)
    ]
    logger.info(f"{len(matched)} jobs matched keywords: {keywords}")
    return matched

def run():
    logger.info("Starting scrape_greenhouse pipeline...")
    config = load_config()
    keywords = config["filter"]["required_keywords"]
    companies = config["greenhouse_companies"]

    all_jobs = []

    for company in companies:
        logger.info(f"Scraping {company}...")
        jobs = get_jobs_from_company(company)
        matched = filter_jobs(jobs, keywords)
        all_jobs.extend(matched)

    logger.info(f"Total matching jobs found: {len(all_jobs)}")

    if all_jobs:
        out_path = OUT_DIR / f"jobs_{datetime.now().strftime('%Y%m%d')}.json"
        with open(out_path, "w") as f:
            json.dump(all_jobs, f, indent=2)
        logger.info(f"Saved jobs to {out_path}")
    else:
        logger.warning("No jobs matched the given keywords.")

    return all_jobs

if __name__ == "__main__":
    run()
