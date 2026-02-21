from core.fetchers.greenhouse_fetcher import fetch_greenhouse_jobs
from core.fetchers.remote_fetcher import fetch_remote_jobs
from core.fetchers.workday_fetcher import fetch_workday
from config import WORKDAY_COMPANIES
from core.fetchers.workday_fetcher import fetch_workday
# from config import WORKDAY_COMPANIES

async def fetch_all_jobs():
    print("===== FETCHING MNC WORKDAY JOBS =====")
    companies = ["ag", "accenture", "capgemini", "dell", "nvidia"]

    for company, tenant in WORKDAY_COMPANIES.items():
        try:
            print(f"Fetching Workday jobs from {company}")
            await fetch_workday(company, tenant)
        except Exception as e:
            print("Failed:", company, e)

    print("===== MNC FETCH COMPLETE =====")

    print("===== FETCHING JOBS =====")
    try:
        fetch_greenhouse_jobs()
    except Exception as e:
        print("Greenhouse error:", e)

    try:
        fetch_remote_jobs()
    except Exception as e:
        print("Remote jobs error:", e)

    print("===== FETCH COMPLETE =====")