import requests
from db.database import add_job

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

async def fetch_workday(company, tenant):

    print(f"Fetching Workday jobs from {company}")

    url = f"https://{company}.wd3.myworkdayjobs.com/wday/cxs/{company}/{tenant}/jobs"

    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": "",
        "locale": "en-US"
    }

    try:
        res = requests.post(url, headers=HEADERS, json=payload, timeout=30)

        if res.status_code != 200:
            print("Failed:", company, res.status_code, res.text[:120])
            return

        data = res.json()

        jobs = data.get("jobPostings", [])
        if not jobs:
            print("No jobs:", company)
            return

        for job in jobs:
            title = job.get("title", "Unknown")
            location = job.get("locationsText", "Unknown")
            external = job.get("externalPath", "")

            link = f"https://{company}.wd3.myworkdayjobs.com/{tenant}/job/{external}"

            await add_job(title, company.upper(), location, link)

        print(f"Saved {len(jobs)} jobs from {company}")

    except Exception as e:
        print("Error:", company, e)