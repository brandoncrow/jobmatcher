from scripts import send_email
from unittest.mock import patch, Mock

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

    subject, summary = send_email.compose_summary(jobs, letters, subject_prefix="Test Matches")
    
    assert "Data Engineer at ACME Corp" in summary
    assert "Analytics Engineer at Beta Inc" in summary
    assert "https://example.com/data-engineer" in summary
    assert "https://example.com/analytics-engineer" in summary
    assert "Cover letters have been generated" in summary
    assert "Test Matches" in subject

def test_send_email_local_mode(capsys):
    """Test local mode prints email instead of sending."""
    subject = "Test Subject"
    body = "This is a test email body."

    fake_config = {
        "email": {
            "mode": "local",
            "from_address": "from@example.com",
            "to_address": "to@example.com",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
        }
    }

    send_email.send_email(subject, body, fake_config)

    captured = capsys.readouterr()
    assert "Test Subject" in captured.out
    assert "This is a test email body." in captured.out

@patch('scripts.send_email.smtplib.SMTP')
def test_send_email_smtp_mode(mock_smtp):
    """Test SMTP mode sends email without crashing."""
    subject = "Test Subject"
    body = "Test body"
    fake_config = {
        "email": {
            "mode": "smtp",
            "from_address": "from@example.com",
            "to_address": "to@example.com",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
        }
    }
    with patch.dict('os.environ', {"SMTP_USER": "user", "SMTP_PASSWORD": "pass"}):
        send_email.send_email(subject, body, fake_config)

    mock_smtp.assert_called_once()
