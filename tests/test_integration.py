import os
import json
from pathlib import Path
from datetime import datetime
from scripts import format_jobs, generate_letters, send_email

# paths
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
LETTERS_DIR = DATA_DIR / 'letters'

# sample test data
TEST_JOBS = [
    {
        "title": "Data Engineer",
        "location": "Remote",
        "company": "TestCorp",
        "updated_at": datetime.now().astimezone().isoformat(),
        "absolute_url": "https://example.com/data-engineer",
        "content": "Looking for ETL experience."
    },
    {
        "title": "Analytics Engineer",
        "location": "Austin, TX",
        "company": "Beta Inc",
        "updated_at": datetime.now().astimezone().isoformat(),
        "absolute_url": "https://example.com/analytics-engineer",
        "content": "Analytics role, Python preferred."
    }
]

def setup_test_data():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    test_file = PROCESSED_DIR / f"jobs_{today}.json"
    with open(test_file, "w") as f:
        json.dump(TEST_JOBS, f, indent=2)

def test_full_pipeline_local(capsys):
    """Simulate a full scrape -> format -> generate -> email pipeline."""

    # save sample jobs
    setup_test_data()

    # format jobs
    formatted_jobs = format_jobs.run(TEST_JOBS)
    assert len(formatted_jobs) == 2
    assert formatted_jobs[0]["score"] >= 0

    # generate letters
    generate_letters.clear_old_letters()  # Clean up first
    generate_letters.run(top_n=2)
    today = datetime.now().strftime("%Y%m%d")
    letters = list(LETTERS_DIR.glob(f"*{today}.txt"))
    assert len(letters) == 2

    # compose summary (local print)
    subject, body = send_email.compose_summary(formatted_jobs, letters, subject_prefix="Test Matches")
    assert "Data Engineer at TestCorp" in body
    assert "Analytics Engineer at Beta Inc" in body
    assert "https://example.com/data-engineer" in body

    print(subject)
    print(body)

    # confirm printed output
    captured = capsys.readouterr()
    assert "Test Matches" in captured.out
    assert "Cover letters have been generated" in captured.out
