import requests
from core.database import add_job

def fetch_remote_jobs():
    print("Checking Remote jobs...")

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        jobs = requests.get(url, headers=headers, timeout=10).json()

        for job in jobs[1:]:
            title = job.get("position", "Unknown")
            company = job.get("company", "Unknown")
            location = "Remote"
            link = "https://remoteok.com" + job.get("url", "")

            add_job(title, company, location, link)

    except Exception as e:
        print("Remote fetch failed:", e)