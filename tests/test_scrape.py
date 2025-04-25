# tests/test_scrape.py

import sys
from pathlib import Path

# Add the job-matcher directory to the system path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts import scrape_greenhouse

def test_get_jobs_from_valid_company():
    """Test that we can fetch jobs from a known valid company."""
    jobs = scrape_greenhouse.get_jobs_from_company("notion")
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    assert "title" in jobs[0]

def test_get_jobs_from_invalid_company():
    """Test that an invalid company returns an empty list and doesn't crash."""
    jobs = scrape_greenhouse.get_jobs_from_company("not-a-real-company")
    assert isinstance(jobs, list)
    assert len(jobs) == 0

def test_filter_jobs_matches_keywords():
    """Test that filtering logic correctly finds job titles with given keywords."""
    sample_jobs = [
        {"title": "Data Engineer", "location": {"name": "Remote"}, "absolute_url": "url1"},
        {"title": "Product Designer", "location": {"name": "SF"}, "absolute_url": "url2"},
    ]
    keywords = ["data engineer", "analytics"]
    filtered = scrape_greenhouse.filter_jobs(sample_jobs, keywords)
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Data Engineer"
