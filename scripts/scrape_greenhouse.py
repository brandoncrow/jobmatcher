# scripts/scrape_greenhouse.py

import requests
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def get_jobs_from_company(board_token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("jobs", [])
    except Exception as e:
        print(f"Error fetching {board_token}: {e}")
        return []

def filter_jobs(jobs, keywords):
    return [
        job for job in jobs
        if any(kw.lower() in job["title"].lower() for kw in keywords)
    ]

def run():
    config = load_config()
    keywords = config["keywords"]
    companies = config["greenhouse_companies"]

    all_jobs = []
    for company in companies:
        jobs = get_jobs_from_company(company)
        matched = filter_jobs(jobs, keywords)
        all_jobs.extend(matched)

    print(f"Found {len(all_jobs)} matching jobs.")
    for job in all_jobs:
        print(f"- {job['title']} at {job['location']['name']}")
        print(f"  Link: {job['absolute_url']}\n")

    return all_jobs

if __name__ == "__main__":
    run()
