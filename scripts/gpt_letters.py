# scripts/gpt_letters.py

import json
import os
from datetime import datetime
from pathlib import Path
import openai
from dotenv import load_dotenv
import yaml
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Paths
CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
JOBS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
LETTERS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'letters'

LETTERS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client (new style)
client = openai.OpenAI()

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def load_jobs():
    latest_file = sorted(JOBS_DIR.glob("jobs_*.json"))[-1]
    logger.info(f"Loading jobs from {latest_file}")
    with open(latest_file, "r") as f:
        return json.load(f)

def clean_filename(text):
    return text.lower().replace(' ', '_').replace('&', 'and').replace('/', '-')

def build_prompt(job, user_profile):
    """Construct a prompt for GPT to generate a custom cover letter."""
    return f"""
Write a professional cover letter for the following job and applicant:

Job Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Job Link: {job['url']}

Applicant Details:
Name: {user_profile['name']}
Email: {user_profile['email']}
Phone: {user_profile['phone']}
Strengths: Strong background in data migrations, ETL development, data quality automation, cloud platforms (AWS), and data tools (Python, SQL Server, Snowflake, Tableau).

Tone: Professional but friendly. Highlight a passion for data engineering and solving business problems.

Do not invent fake certifications, employment history, or skills.
Keep it concise (about 250-300 words).
End politely, expressing enthusiasm to discuss the opportunity.
"""

def generate_letter(prompt, model="gpt-4o", temperature=0.5):
    """Call OpenAI API to generate a cover letter."""
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled at writing professional cover letters."},
                {"role": "user", "content": prompt}
            ]
        )
        letter = response.choices[0].message.content.strip()
        return letter
    except Exception as e:
        logger.error(f"Failed to generate letter: {e}", exc_info=True)
        return None

def run(top_n=None):
    logger.info("Starting GPT-based letter generation...")

    config = load_config()
    user_profile = config['user_profile']
    top_n = top_n or config['general']['top_n_jobs']
    model_name = config['model']['name']
    temperature = config['model']['temperature']

    jobs = load_jobs()
    top_jobs = jobs[:top_n]

    today = datetime.now().strftime("%Y%m%d")

    for job in top_jobs:
        prompt = build_prompt(job, user_profile)
        letter = generate_letter(prompt, model_name, temperature)

        if letter:
            safe_title = clean_filename(job['title'])
            safe_company = clean_filename(job['company'])
            filename = LETTERS_DIR / f"{safe_title}_{safe_company}_{today}.txt"

            with open(filename, "w") as f:
                f.write(letter)

            logger.info(f"Saved GPT-generated letter: {filename}")
        else:
            logger.error(f"Skipping saving letter for {job['title']} at {job['company']} due to generation failure.")

    logger.info("Finished GPT-based letter generation.")

if __name__ == "__main__":
    run()
