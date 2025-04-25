import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
OUT_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def deduplicate(jobs):
    seen = set()
    unique = []
    for job in jobs:
        key = f"{job['title']}|{job['location']['name']}|{job['company']['name']}"
        hash_ = hashlib.md5(key.encode()).hexdigest()
        if hash_ not in seen:
            seen.add(hash_)
            unique.append(job)
    return unique

def is_recent(job, max_days):
    updated_at = job["updated_at"]
    if "." in updated_at:
        updated_at = updated_at.split(".")[0] + updated_at[-6:]
    job_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S%z")
    return datetime.now(job_date.tzinfo) - job_date <= timedelta(days=max_days)

def score_job(job, keywords, boost_keywords):
    title = job['title'].lower()
    desc = job.get('content', '').lower()
    text = title + " " + desc
    score = sum(1 for kw in keywords if kw.lower() in text)
    score += sum(2 for kw in boost_keywords if kw.lower() in text)
    return score

def normalize(job):
    return {
        "title": job["title"],
        "company": job["company"]["name"],
        "location": job["location"]["name"],
        "url": job["absolute_url"],
        "updated_at": job["updated_at"],
        "score": 0,  # updated later
    }

def run(jobs):
    config = load_config()
    max_days = config["filter"]["days_old_max"]
    keywords = config["filter"]["required_keywords"]
    boosts = config["filter"]["score_boost_keywords"]

    jobs = deduplicate(jobs)
    jobs = [normalize(job) for job in jobs if is_recent(job, max_days)]

    for job in jobs:
        job["score"] = score_job(job, keywords, boosts)

    jobs = sorted(jobs, key=lambda x: x["score"], reverse=True)

    out_file = OUT_DIR / f"jobs_{datetime.now().strftime('%Y%m%d')}.json"
    with open(out_file, "w") as f:
        json.dump(jobs, f, indent=2)

    print(f"Saved {len(jobs)} jobs to {out_file}")
    return jobs

if __name__ == "__main__":
    from scrape_greenhouse import run as scrape_run
    jobs = scrape_run()
    run(jobs)
