import pytest
from datetime import datetime, timedelta, timezone
from scripts import format_jobs
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

def sample_job(
    title="Data Engineer",
    company="ACME",
    location="Remote",
    updated_at=None,
    content="Looking for Python and ETL skills."
):
    if updated_at is None:
        updated_at = datetime.now(timezone.utc).isoformat()
    return {
        "title": title,
        "company": company,
        "location": location,
        "updated_at": updated_at,
        "absolute_url": "https://example.com/job",
        "content": content
    }


def test_deduplicate_jobs():
    jobs = [
        sample_job(),
        sample_job(),  # duplicate
        sample_job(title="Analytics Engineer"),
    ]
    deduped = format_jobs.deduplicate(jobs)
    assert len(deduped) == 2
    titles = [job["title"] for job in deduped]
    assert "Data Engineer" in titles
    assert "Analytics Engineer" in titles

def test_is_recent_within_window():
    job = sample_job(updated_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat())
    assert format_jobs.is_recent(job, max_days=2) is True

def test_is_recent_outside_window():
    job = sample_job(updated_at=(datetime.now(timezone.utc) - timedelta(days=5)).isoformat())
    assert format_jobs.is_recent(job, max_days=2) is False

def test_score_job_keywords_and_boosts():
    job = sample_job(content="Python, ETL, and data pipelines")
    score = format_jobs.score_job(job, ["data", "pipelines"], ["python", "etl"])
    # expected: data + pipelines = 1+1, python + etl = 2+2 → total = 6
    assert score == 6

def test_normalize_structure():
    raw = sample_job()
    norm = format_jobs.normalize(raw)
    assert norm["title"] == "Data Engineer"
    assert norm["company"] == "ACME"
    assert norm["location"] == "Remote"
    assert norm["url"] == "https://example.com/job"
    assert "updated_at" in norm
    assert "score" in norm
