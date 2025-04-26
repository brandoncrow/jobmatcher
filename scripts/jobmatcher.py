from scripts import scrape_greenhouse, format_jobs, generate_letters, send_email, gpt_letters
import logging, yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 80)
    logger.info("Starting Job Matcher Pipeline...")

    try:
        logger.info("[1/4] Scraping jobs from Greenhouse...")
        raw_jobs = scrape_greenhouse.run()

        logger.info("[2/4] Formatting and filtering jobs...")
        filtered_jobs = format_jobs.run(raw_jobs)

        logger.info("[3/4] Generating cover letters...")

        config = load_config()
        use_gpt = config['general'].get('use_gpt', False)

        if use_gpt:
            logger.info("Using GPT-generated cover letters...")
            gpt_letters.run(top_n=config['general']['top_n_jobs'])
        else:
            logger.info("Using template-based cover letters...")
            generate_letters.run(top_n=config['general']['top_n_jobs'])

        logger.info("[4/4] Sending daily email summary...")
        send_email.run()

        logger.info("Pipeline completed successfully!")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

    logger.info("=" * 80)

if __name__ == "__main__":
    main()
