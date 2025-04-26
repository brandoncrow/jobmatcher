from pathlib import Path
import yaml
from scripts import generate_letters

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def test_select_template_exact_matches():
    config = load_config()
    assert generate_letters.select_template("Analytics Engineer", config).name == "analytics_engineer.txt"
    assert generate_letters.select_template("Data Engineer", config).name == "data_engineer.txt"
    assert generate_letters.select_template("ETL Developer", config).name == "etl_developer.txt"
    assert generate_letters.select_template("Data Integration Specialist", config).name == "integration.txt"
    assert generate_letters.select_template("Data Quality Engineer", config).name == "data_quality_engineer.txt"

def test_select_template_default():
    config = load_config()
    template = generate_letters.select_template("Senior Data Scientist", config)
    assert template.name == config["templates"]["default"]

def test_clean_filename_basic():
    cleaned = generate_letters.clean_filename("Data Engineer / Automation & AI")
    assert cleaned == "data_engineer_-_automation_and_ai"

def test_create_letter_without_crashing():
    config = load_config()
    user_profile = config["user_profile"]
    template_path = generate_letters.select_template("Data Engineer", config)

    job = {
        "title": "Data Engineer",
        "company": "ACME Corp"
    }

    letter = generate_letters.fill_template(template_path, job["title"], job["company"], user_profile)
    assert "ACME Corp" in letter
    assert "Data Engineer" in letter
    assert user_profile["name"] in letter