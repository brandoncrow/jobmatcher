from scripts import scrape_greenhouse, format_jobs, generate_letters, send_email

def main():
    print("="*80)
    print("Starting Job Matcher Pipeline...")

    print("\n[1/4] Scraping jobs from Greenhouse...")
    raw_jobs = scrape_greenhouse.run()

    print("\n[2/4] Formatting and filtering jobs...")
    filtered_jobs = format_jobs.run(raw_jobs)

    print("\n[3/4] Generating cover letters...")
    generate_letters.run(top_n=5)  # You can configure this number later if you want

    print("\n[4/4] Sending daily email summary...")
    send_email.run()

    print("\nPipeline completed successfully!")
    print("="*80)

if __name__ == "__main__":
    main()
