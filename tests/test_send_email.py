import pytest
from scripts import send_email

def test_compose_summary_structure():
    jobs = [
        {
            "title": "Data Engineer",
            "company": "ACME Corp",
            "location": "Remote",
            "url": "https://example.com/data-engineer"
        },
        {
            "title": "Analytics Engineer",
            "company": "Beta Inc",
            "location": "Austin, TX",
            "url": "https://example.com/analytics-engineer"
        },
    ]
    letters = ["letter1.txt", "letter2.txt"]

    summary = send_email.compose_summary(jobs, letters)

    assert "Data Engineer at ACME Corp" in summary
    assert "Analytics Engineer at Beta Inc" in summary
    assert "https://example.com/data-engineer" in summary
    assert "https://example.com/analytics-engineer" in summary
    assert "Cover letters have been generated" in summary

def test_send_email_local_mode(capsys):
    subject = "Test Email"
    body = "This is a test email body."

    send_email.EMAIL_MODE = "local"
    send_email.send_email(subject, body)

    captured = capsys.readouterr()
    assert "Test Email" in captured.out
    assert "This is a test email body." in captured.out
