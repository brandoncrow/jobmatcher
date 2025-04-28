from unittest.mock import patch, Mock
from scripts import scrape_greenhouse

@patch('scripts.scrape_greenhouse.requests.get')
def test_get_jobs_from_valid_company(mock_get):
    """Test fetching jobs with a mocked successful response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jobs": [{"title": "Data Engineer", "location": {"name": "Remote"}, "absolute_url": "url"}]
    }
    mock_get.return_value = mock_response

    jobs = scrape_greenhouse.get_jobs_from_company("notion")
    assert isinstance(jobs, list)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Data Engineer"

@patch('scripts.scrape_greenhouse.requests.get')
def test_get_jobs_from_invalid_company(mock_get):
    """Test that an invalid company returns an empty list without crashing."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("404 Error")
    mock_get.return_value = mock_response

    jobs = scrape_greenhouse.get_jobs_from_company("fake-company")
    assert isinstance(jobs, list)
    assert len(jobs) == 0

def test_filter_jobs_matches_keywords():
    """Test that filtering finds jobs matching keywords."""
    sample_jobs = [
        {"title": "Data Engineer", "location": {"name": "Remote"}, "absolute_url": "url1"},
        {"title": "Product Designer", "location": {"name": "SF"}, "absolute_url": "url2"},
    ]
    keywords = ["data engineer", "analytics"]
    filtered = scrape_greenhouse.filter_jobs(sample_jobs, keywords)
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Data Engineer"
