import json
from datetime import datetime
from pathlib import Path

EMAIL_MODE = "local"  # "local" (print to console) or "smtp" (future swap)

JOBS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
LETTERS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'letters'

def load_jobs():
    latest_file = sorted(JOBS_DIR.glob("jobs_*.json"))[-1]
    with open(latest_file, "r") as f:
        return json.load(f)

def load_letters():
    today = datetime.now().strftime("%Y%m%d")
    return list(LETTERS_DIR.glob(f"*{today}.txt"))

def compose_summary(jobs, letters):
    summary = f"Good morning!\n\nHere are your top {len(letters)} job matches for {datetime.now().strftime('%Y-%m-%d')}:\n\n"
    for idx, job in enumerate(jobs[:len(letters)], 1):
        summary += f"{idx}. {job['title']} at {job['company']} ({job['location']})\n"
        summary += f"   Link: {job['url']}\n\n"
    summary += "Cover letters have been generated and saved.\n\nHave a great day!\n"
    return summary

def send_email(subject, body):
    if EMAIL_MODE == "local":
        print("="*80)
        print(f"Subject: {subject}\n")
        print(body)
        print("="*80)
    elif EMAIL_MODE == "smtp":
        # Placeholder for future SMTP setup
        print("SMTP sending not implemented yet.")

def run():
    jobs = load_jobs()
    letters = load_letters()
    body = compose_summary(jobs, letters)
    subject = f"Daily Job Matches - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, body)

if __name__ == "__main__":
    run()
