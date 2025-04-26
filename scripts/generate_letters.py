import json
from datetime import datetime
from pathlib import Path
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Paths
CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
JOBS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
LETTERS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'letters'
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / 'templates'

LETTERS_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    logger.info("Loading configuration file...")
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def load_jobs():
    latest_file = sorted(JOBS_DIR.glob("jobs_*.json"))[-1]
    logger.info(f"Loading jobs from {latest_file}")
    with open(latest_file, "r") as f:
        return json.load(f)

def clean_filename(text):
    return text.lower().replace(' ', '_').replace('&', 'and').replace('/', '-')

def select_template(job_title, config):
    title = job_title.lower()
    for keyword, template_file in config['templates'].items():
        if keyword in title:
            logger.info(f"Selected template '{template_file}' for job title: {job_title}")
            return TEMPLATES_DIR / template_file
    logger.info(f"No specific template match for {job_title}. Using default.")
    return TEMPLATES_DIR / config['templates']['default']

def fill_template(template_path, job_title, company_name, user_profile):
    with open(template_path, 'r') as f:
        template = f.read()
    return template.format(
        hiring_manager="Hiring Team",
        job_title=job_title,
        company_name=company_name,
        user_name=user_profile['name'],
        user_email=user_profile['email'],
        user_phone=user_profile['phone']
    )

def clear_old_letters():
    today = datetime.now().strftime("%Y%m%d")
    files_deleted = 0
    for file in LETTERS_DIR.glob(f"*{today}.txt"):
        file.unlink()
        files_deleted += 1
    if files_deleted > 0:
        logger.info(f"Cleared {files_deleted} old letters for today.")

def run(top_n=None):
    logger.info("Starting cover letter generation...")
    clear_old_letters()

    config = load_config()
    top_n = top_n or config['general']['top_n_jobs']
    user_profile = config['user_profile']

    jobs = load_jobs()
    top_jobs = jobs[:top_n]

    today = datetime.now().strftime("%Y%m%d")

    for job in top_jobs:
        try:
            template_path = select_template(job["title"], config)
            letter = fill_template(template_path, job["title"], job["company"], user_profile)

            safe_title = clean_filename(job['title'])
            safe_company = clean_filename(job['company'])
            filename = LETTERS_DIR / f"{safe_title}_{safe_company}_{today}.txt"

            with open(filename, "w") as f:
                f.write(letter)

            logger.info(f"Saved letter: {filename}")
        except Exception as e:
            logger.error(f"Failed to generate letter for {job.get('title')} at {job.get('company')}: {e}")

    logger.info("Finished generating all letters.")

if __name__ == "__main__":
    run()
