import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

EMAIL_MODE = "local"  # "local" (print to console) or "smtp" (future swap)

JOBS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
LETTERS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'letters'

def load_jobs():
    latest_file = sorted(JOBS_DIR.glob("jobs_*.json"))[-1]
    logger.info(f"Loaded jobs from {latest_file}")
    with open(latest_file, "r") as f:
        return json.load(f)

def load_letters():
    today = datetime.now().strftime("%Y%m%d")
    letters = list(LETTERS_DIR.glob(f"*{today}.txt"))
    logger.info(f"Found {len(letters)} letters for today")
    return letters

def compose_summary(jobs, letters):
    job_count = len(letters)  # Match number of letters, not all jobs
    logger.info(f"Composing summary for {job_count} jobs")
    summary = f"Here are your top {job_count} job matches for {datetime.now().strftime('%Y-%m-%d')}:\n\n"

    for idx, job in enumerate(jobs[:job_count], 1):
        summary += f"{idx}. {job['title']} at {job['company']} ({job['location']})\n"
        summary += f"   Link: {job['url']}\n\n"

    summary += "Cover letters have been generated and saved.\n\nHave a great day!\n"
    return summary

def send_email(subject, body):
    if EMAIL_MODE == "local":
        logger.info("Sending email in local mode")
        print("="*80)
        print(f"Subject: {subject}\n")
        print(body)
        print("="*80)
    elif EMAIL_MODE == "smtp":
        # Placeholder for future SMTP setup
        logger.warning("SMTP email mode selected, but not yet implemented")
        print("SMTP sending not implemented yet.")

def run():
    logger.info("Starting email summary process...")
    try:
        jobs = load_jobs()
        letters = load_letters()
        body = compose_summary(jobs, letters)
        subject = f"Daily Job Matches - {datetime.now().strftime('%Y-%m-%d')}"
        send_email(subject, body)
        logger.info("Email summary completed successfully") 
    except Exception as e:
        logger.error(f"Failed to send summary: {e}")

if __name__ == "__main__":
    run()
