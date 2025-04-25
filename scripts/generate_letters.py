# scripts/generate_letters.py

import json
from datetime import datetime
from pathlib import Path

# === Template Texts ===
TEMPLATES = {
    "data engineer": """Dear {hiring_manager},

I am excited to apply for the {job_title} position at {company_name}. With a strong background in full-scale data migrations, ETL development, and data quality automation, I bring a proven ability to deliver reliable, scalable solutions that improve data usability across business domains.

At PakEnergy, I led the migration of legacy oil & gas client systems to modern cloud platforms, designing ETL pipelines using Python, SQL Server, and YAML-driven configurations. I also built QA automation processes in T-SQL, reducing manual error detection and streamlining client onboarding.

Currently, I am advancing my cloud data engineering expertise through AWS and dbt certifications, complementing my hands-on experience with technologies like Snowflake, Tableau, and Git. I am passionate about building efficient, fault-tolerant pipelines that empower teams to make better data-driven decisions.

I would be thrilled to bring my technical skills, collaborative approach, and continuous improvement mindset to {company_name}. Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to your team.

Sincerely,
Brandon Crow
(405) 408-5892 | brandoncrow87@gmail.com
""",
    "analytics engineer": """Dear {hiring_manager},

I am writing to express my interest in the {job_title} role at {company_name}. With a background in data migrations, ETL pipeline development, and advanced analytics instruction, I have cultivated the skills necessary to transform raw data into actionable insights for business stakeholders.

In my role at PakEnergy, I engineered ETL workflows that mapped, transformed, and validated complex client data, improving data quality and integration into cloud-based platforms. Prior to that, as a Data Science & Analytics Instructor at the University of Oklahoma, I designed and taught Python, machine learning, and data visualization courses for professionals transitioning into analytics roles.

Currently pursuing AWS and dbt certifications, I am committed to building modern, scalable data solutions that drive value. My hands-on experience with SQL, Snowflake, Tableau, and Git further strengthens my ability to bridge the gap between raw data and decision-ready analytics.

I am excited about the opportunity to apply my technical skills and passion for data-driven storytelling at {company_name}. Thank you for considering my application. I look forward to connecting.

Sincerely,
Brandon Crow
(405) 408-5892 | brandoncrow87@gmail.com
""",
    "integration": """Dear {hiring_manager},

I am pleased to submit my application for the {job_title} position at {company_name}. With hands-on experience building pipelines that integrate, transform, and validate diverse data sources, I am passionate about solving complex data challenges that drive business innovation.

At PakEnergy, I developed ETL solutions integrating multiple client files into a cloud-based SaaS database, ensuring seamless onboarding across varied legacy systems. I also built QA automation frameworks in T-SQL, significantly improving data integrity and reducing manual review cycles.

My technical toolkit includes Python (Pandas, NumPy), SQL (T-SQL, PostgreSQL), Tableau, Snowflake, and Git. I am currently pursuing AWS and dbt certifications to deepen my cloud integration skills and stay ahead in a rapidly evolving field.

I am eager to contribute my problem-solving skills, technical acumen, and commitment to continuous improvement to the data initiatives at {company_name}. Thank you for your time and consideration.

Sincerely,
Brandon Crow
(405) 408-5892 | brandoncrow87@gmail.com
""",
    "quality": """Dear {hiring_manager},

I am writing to apply for the {job_title} position at {company_name}. With hands-on experience designing automated quality control systems and validating large-scale data pipelines, I bring a meticulous and scalable approach to ensuring data integrity.

At PakEnergy, I developed a peer QA review automation process using T-SQL that significantly reduced manual oversight and caught issues earlier in the data pipeline. I also designed YAML-driven ETL workflows that enabled consistent validation and rollback capabilities across multiple client environments.

My experience spans SQL Server, Python, Tableau, and Snowflake, and I am currently pursuing AWS and dbt certifications to strengthen my cloud and data modeling skills. I am passionate about creating systems that catch issues before they impact operations and ensuring data teams can trust their inputs.

I would be excited to bring my precision, engineering mindset, and automation skills to the Data Quality team at {company_name}. Thank you for your time and consideration.

Sincerely,
Brandon Crow
(405) 408-5892 | brandoncrow87@gmail.com
""",
    "etl": """Dear {hiring_manager},

I am excited to express my interest in the {job_title} role at {company_name}. With a strong background in designing robust ETL pipelines for data migration and transformation, I thrive on building systems that move data efficiently, reliably, and at scale.

While at PakEnergy, I led the development of reusable Python and SQL-based ETL workflows to migrate oil & gas client data from legacy systems into modern SaaS platforms. These pipelines incorporated client-specific mapping, logging, rollback logic, and validation, enabling smooth onboarding across complex and varied source data environments.

My technical stack includes T-SQL, Python (Pandas), YAML configuration files, and tools like Snowflake, Git, and Tableau. I am also in the process of earning AWS and dbt certifications to expand my cloud-native data pipeline capabilities.

I am eager to bring my passion for clean data engineering and scalable architecture to {company_name}. Thank you for considering my application. I look forward to the opportunity to contribute.

Sincerely,
Brandon Crow
(405) 408-5892 | brandoncrow87@gmail.com
""",
}

DEFAULT_TEMPLATE = TEMPLATES["data engineer"]  # Default if no match

JOBS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'processed'
LETTERS_DIR = Path(__file__).resolve().parents[1] / 'data' / 'letters'
LETTERS_DIR.mkdir(parents=True, exist_ok=True)

def load_jobs():
    latest_file = sorted(JOBS_DIR.glob("jobs_*.json"))[-1]
    with open(latest_file, "r") as f:
        return json.load(f)

def select_template(job_title):
    title = job_title.lower()
    if "analytics engineer" in title:
        return TEMPLATES["analytics engineer"]
    elif "integration" in title:
        return TEMPLATES["integration"]
    elif "quality" in title or "qa" in title:
        return TEMPLATES["quality"]
    elif "etl" in title:
        return TEMPLATES["etl"]
    elif "data engineer" in title:
        return TEMPLATES["data engineer"]
    else:
        return DEFAULT_TEMPLATE

def clean_filename(text):
    return text.lower().replace(' ', '_').replace('&', 'and').replace('/', '-')

def run(top_n=5):
    jobs = load_jobs()
    top_jobs = jobs[:top_n]  # Top N jobs by score

    today = datetime.now().strftime("%Y%m%d")

    for job in top_jobs:
        template = select_template(job["title"])
        letter = template.format(
            hiring_manager="Hiring Team",
            job_title=job["title"],
            company_name=job["company"]
        )
        safe_title = clean_filename(job['title'])
        safe_company = clean_filename(job['company'])
        filename = LETTERS_DIR / f"{safe_title}_{safe_company}_{today}.txt"
        with open(filename, "w") as f:
            f.write(letter)
        print(f"Saved letter for {job['title']} at {job['company']} -> {filename}")

if __name__ == "__main__":
    run()
