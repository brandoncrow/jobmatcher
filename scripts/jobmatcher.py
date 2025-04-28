from scripts import scrape_greenhouse, format_jobs, generate_letters, send_email, gpt_letters, deduplicate_history
import logging
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Config file not found: {CONFIG_PATH}")
        raise

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# planning to scrape additional sites...
SCRAPERS = {
    "greenhouse": scrape_greenhouse
}

def main():
    logger.info("=" * 80)
    logger.info("Starting Job Matcher Pipeline...")

    try:
        config = load_config()
        scraper_configs = config.get("scrapers", {"greenhouse": config.get("greenhouse_companies", [])})

        # scrape jobs
        logger.info("[1/6] Scraping jobs...")
        raw_jobs = []
        for board, scraper_config in scraper_configs.items():
            if board not in SCRAPERS:
                logger.warning(f"No scraper defined for board: {board}")
                continue
            logger.info(f"Running scraper for {board}...")
            jobs = SCRAPERS[board].run(scraper_config.get("companies", []))
            raw_jobs.extend(jobs)
        logger.info(f"Scraped {len(raw_jobs)} raw jobs")

        # [2/6] Format and filter jobs
        logger.info("[2/6] Formatting and filtering jobs...")
        formatted_jobs = format_jobs.run(raw_jobs)
        if not formatted_jobs:
            logger.warning("No jobs after formatting; exiting pipeline")
            return

        # [3/6] Save formatted jobs (handled in format_jobs.py)

        # [4/6] Deduplicate against historical jobs
        logger.info("[4/6] Deduplicating historical jobs...")
        new_jobs = deduplicate_history.run(formatted_jobs)
        logger.info(f"Found {len(new_jobs)} new jobs after deduplication")

        # [5/6] Generate cover letters
        logger.info("[5/6] Generating cover letters...")
        use_gpt = config['general'].get('use_gpt', False)
        top_n = config['general'].get('top_n_jobs', 5)

        if use_gpt:
            logger.info("Using GPT-generated cover letters...")
            gpt_letters.run(top_n=top_n)
        else:
            logger.info("Using template-based cover letters...")
            generate_letters.run(top_n=top_n)

        # [6/6] Send email summary
        logger.info("[6/6] Sending daily email summary...")
        send_email.run()

        logger.info("Pipeline completed successfully!")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

    logger.info("=" * 80)

if __name__ == "__main__":
    main()