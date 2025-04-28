# Job Matcher

> **Note:** This project is actively under development. Core functionality is working; new features and improvements are added regularly.

Job Matcher is a fully automated daily job search and cover letter generation pipeline.
It scrapes job postings from Greenhouse-hosted boards, filters and scores relevant jobs,
deduplicates against past jobs, generates personalized cover letters (using either templates or GPT),
and emails a daily summary.

## Features

- **Scrape Jobs**: Pulls jobs from Greenhouse job boards.
- **Flexible Filtering**: Uses keywords and scoring boosts to rank matches.
- **Historical Deduplication**: Prevents resending jobs you've already seen.
- **Cover Letter Generation**:
  - Template-based (fast, no cost)
  - GPT-based (high quality, customizable)
- **Email Delivery**: Sends you a daily curated email with links and cover letters.
- **Modular Design**: Easy to add new scrapers (e.g., Lever, Workday, etc.).

## Project Structure

```bash
job-matcher/
|├── config/
|├── data/
|   |├── processed/
|   |└── archive/
|├── logs/
|├── scripts/
|   |├── jobmatcher.py
|   |├── scrape_greenhouse.py
|   |├── format_jobs.py
|   |├── deduplicate_history.py
|   |├── generate_letters.py
|   |├── gpt_letters.py
|   |└── send_email.py
|└── tests/
```

## How It Works

1. **Scrape**: Pull jobs from Greenhouse boards based on configured companies.
2. **Format & Score**: Filter by keywords, boost by preferred terms, rank.
3. **Deduplicate**: Exclude jobs seen in previous days.
4. **Generate Letters**:
   - Use templates (free, quick) or GPT (smarter, customizable).
5. **Email Results**: Send yourself a concise daily report.

## Installation

```bash
# Clone the repository
$ git clone https://github.com/yourusername/job-matcher.git
$ cd job-matcher

# Set up virtual environment
$ python3 -m venv venv
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt

# Create a .env file
OPENAI_API_KEY=your-openai-key
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
```

## Configuration

All settings are controlled in `config/config.yaml`:

- **Scrapers**: List of companies to scrape from each platform.
- **Filtering**: Keywords to include and boost.
- **User Profile**: Personal info for letters.
- **Email Settings**: SMTP server, mode (local/smtp).
- **Model Settings**: GPT model and temperature.

Example:
```yaml
scrapers:
  greenhouse:
    - notion
    - stripe
    - datadog

filter:
  required_keywords:
    - data
    - engineer

user_profile:
  name: "Brandon Crow"
  email: "brandoncrow87@gmail.com"
  phone: "(405) 408-5892"

general:
  use_gpt: false
  days_old_max: 3
  top_n_jobs: 5

email:
  mode: smtp
  smtp_server: smtp.gmail.com
  smtp_port: 587
  from_address: your@email.com
  to_address: your@email.com
```

## Usage

Run the full daily pipeline:

```bash
$ python -m scripts.jobmatcher
```

Or run components individually:

```bash
$ python -m scripts.scrape_greenhouse
$ python -m scripts.format_jobs
$ python -m scripts.deduplicate_history
$ python -m scripts.generate_letters
$ python -m scripts.gpt_letters
$ python -m scripts.send_email
```

## Testing

```bash
$ pytest tests/
```
Includes:
- Unit tests (scraping, formatting, letters, email)
- Integration test (full scrape → format → letter → email)

## Roadmap

- [ ] Add scrapers for additional job sites
- [ ] Improve scoring (e.g., NLP-based match percentage)
- [ ] Save letters to Google Drive automatically
- [ ] AWS deployment option
- [ ] More robust matching and filtering