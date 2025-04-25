import pytest
from scripts import generate_letters

def test_select_template_exact_matches():
    assert generate_letters.select_template("Analytics Engineer") == generate_letters.TEMPLATES["analytics engineer"]
    assert generate_letters.select_template("Data Engineer") == generate_letters.TEMPLATES["data engineer"]
    assert generate_letters.select_template("ETL Developer") == generate_letters.TEMPLATES["etl"]
    assert generate_letters.select_template("Data Integration Specialist") == generate_letters.TEMPLATES["integration"]
    assert generate_letters.select_template("Data Quality Engineer") == generate_letters.TEMPLATES["quality"]


def test_select_template_default():
    template = generate_letters.select_template("Senior Data Scientist")
    assert "data engineer" in template.lower()  # falls back to default template

def test_clean_filename_basic():
    cleaned = generate_letters.clean_filename("Data Engineer / Automation & AI")
    assert cleaned == "data_engineer_-_automation_and_ai"

def test_create_letter_without_crashing():
    # simulate a job
    job = {
        "title": "Data Engineer",
        "company": "ACME Corp"
    }
    template = generate_letters.select_template(job["title"])
    letter = template.format(
        hiring_manager="Hiring Team",
        job_title=job["title"],
        company_name=job["company"]
    )
    assert "ACME Corp" in letter
    assert "Data Engineer" in letter
    assert "Hiring Team" in letter
