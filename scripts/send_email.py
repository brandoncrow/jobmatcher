import json
import os
import smtplib
import ssl
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Paths
CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
JOBS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
LETTERS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'letters'

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def load_jobs():
    latest_file = sorted(JOBS_DIR.glob("jobs_*.json"))[-1]
    logger.info(f"Loading jobs from {latest_file}")
    with open(latest_file, "r") as f:
        return json.load(f)

def load_letters():
    today = datetime.now().strftime("%Y%m%d")
    return list(LETTERS_DIR.glob(f"*{today}.txt"))

def compose_summary(jobs, letters, subject_prefix):
    job_count = len(letters)  # Match number of letters generated
    summary = f"Here are your top {job_count} job matches for {datetime.now().strftime('%Y-%m-%d')}:\n\n"

    for idx, job in enumerate(jobs[:job_count], 1):
        summary += f"{idx}. {job['title']} at {job['company']} ({job['location']})\n"
        summary += f"   Link: {job['url']}\n\n"

    summary += "Cover letters have been generated and saved.\n\nHave a great day!\n"
    subject = f"{subject_prefix} - {datetime.now().strftime('%Y-%m-%d')}"
    return subject, summary

def send_email(subject, body, config):
    mode = config['email']['mode']

    if mode == "local":
        # Local print mode
        print("=" * 80)
        print(f"Subject: {subject}\n")
        print(body)
        print("=" * 80)
        logger.info("Email printed to console (local mode).")
    elif mode == "smtp":
        try:
            smtp_server = config['email']['smtp_server']
            smtp_port = config['email']['smtp_port']
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            from_address = config['email']['from_address']
            to_address = config['email']['to_address']

            # Create the email
            message = MIMEMultipart()
            message["From"] = from_address
            message["To"] = to_address
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            # Connect and send
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_password)
                server.sendmail(from_address, to_address, message.as_string())

            logger.info(f"Email sent to {to_address} successfully.")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    else:
        logger.error(f"Unknown email mode: {mode}")

def run():
    logger.info("Starting email sending process...")

    config = load_config()
    jobs = load_jobs()
    letters = load_letters()
    subject_prefix = config['email'].get('subject_prefix', 'Job Matches')
    subject, body = compose_summary(jobs, letters, subject_prefix)

    send_email(subject, body, config)

    logger.info("Email sending process completed.")

if __name__ == "__main__":
    run()
