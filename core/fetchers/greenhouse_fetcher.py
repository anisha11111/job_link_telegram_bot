import requests
from core.database import add_job

# Companies using Greenhouse (REAL companies)
GREENHOUSE_COMPANIES = [
    "stripe",
    "discord",
    "datadog",
    "cloudflare",
    "shopify",
    "airbnb"
]

def fetch_greenhouse_jobs():
    print("Checking Greenhouse companies...")

    for company in GREENHOUSE_COMPANIES:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        try:
            r = requests.get(url, timeout=10)
            data = r.json()

            for job in data.get("jobs", []):
                title = job.get("title", "Unknown")
                location = job.get("location", {}).get("name", "Remote")
                link = job.get("absolute_url", "")
                company_name = company

                add_job(title, company_name, location, link)

        except Exception as e:
            print(f"Failed: {company}", e)