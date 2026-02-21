"""
core/collector.py
Fetches jobs from 6 sources:
  1. Greenhouse  — startup/mid companies (free public API)
  2. Lever       — startup/mid companies (free public API)
  3. Remotive    — remote jobs aggregator (free)
  4. The Muse    — general job board (free)
  5. Amazon      — amazon.jobs public JSON search API
  6. Google      — careers.google.com public JSON API
"""

import hashlib
import httpx
from typing import List
from config import GREENHOUSE_COMPANIES, LEVER_COMPANIES
from db.database import save_job

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def make_id(*parts) -> str:
    return hashlib.md5("_".join(str(p) for p in parts).encode()).hexdigest()


def categorize(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["react", "next.js", "nextjs"]):             return "React"
    if any(k in t for k in ["node", "express.js"]):                      return "Node.js"
    if any(k in t for k in ["javascript", "typescript"]):                return "JavaScript"
    if "python" in t:                                                     return "Python"
    if any(k in t for k in ["java ", "java,", "spring boot", "kotlin"]): return "Java"
    if any(k in t for k in ["machine learning", "deep learning", "nlp", "llm", "ai engineer"]): return "ML/AI"
    if any(k in t for k in ["data scientist", "data science", "data analyst"]): return "Data Science"
    if any(k in t for k in ["devops", "site reliability", "sre", "kubernetes", "docker", "platform engineer"]): return "DevOps"
    if any(k in t for k in ["android", "kotlin developer"]):             return "Android"
    if any(k in t for k in ["ios", "swift developer"]):                  return "iOS"
    if any(k in t for k in ["qa engineer", "quality assurance", "test engineer", "sdet"]): return "Testing/QA"
    if any(k in t for k in ["ui/ux", "ux designer", "product designer"]): return "UI/UX"
    if any(k in t for k in ["full stack", "fullstack", "full-stack"]):   return "Full Stack"
    if any(k in t for k in ["frontend", "front-end"]):                   return "Frontend"
    if any(k in t for k in ["backend", "back-end"]):                     return "Backend"
    return "Software Engineering"


# ── 1. GREENHOUSE ─────────────────────────────────────────────────────────────
async def fetch_greenhouse(company: str) -> List[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            r = await client.get(url)
            if r.status_code != 200:
                print(f"  [Greenhouse:{company}] HTTP {r.status_code}")
                return []
            for item in r.json().get("jobs", []):
                title = item.get("title", "").strip()
                link  = item.get("absolute_url", "").strip()
                if not title or not link:
                    continue
                jobs.append({
                    "id":         make_id("gh", company, item["id"]),
                    "title":      title,
                    "company":    company.replace("-", " ").title(),
                    "location":   item.get("location", {}).get("name", "Remote"),
                    "category":   categorize(title),
                    "apply_link": link,
                    "source":     "Greenhouse",
                })
        print(f"  [Greenhouse:{company}] ✅ {len(jobs)} jobs")
    except Exception as e:
        print(f"  [Greenhouse:{company}] ❌ {e}")
    return jobs


# ── 2. LEVER ──────────────────────────────────────────────────────────────────
async def fetch_lever(company: str) -> List[dict]:
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            r = await client.get(url)
            if r.status_code != 200:
                print(f"  [Lever:{company}] HTTP {r.status_code}")
                return []
            data = r.json()
            if not isinstance(data, list):
                return []
            for item in data:
                title = item.get("text", "").strip()
                link  = item.get("hostedUrl", "").strip()
                if not title or not link:
                    continue
                location = item.get("categories", {}).get("location", "") or "Remote"
                jobs.append({
                    "id":         make_id("lv", company, item.get("id", "")),
                    "title":      title,
                    "company":    company.replace("-", " ").title(),
                    "location":   location,
                    "category":   categorize(title),
                    "apply_link": link,
                    "source":     "Lever",
                })
        print(f"  [Lever:{company}] ✅ {len(jobs)} jobs")
    except Exception as e:
        print(f"  [Lever:{company}] ❌ {e}")
    return jobs


# ── 3. REMOTIVE ───────────────────────────────────────────────────────────────
async def fetch_remotive() -> List[dict]:
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            r = await client.get("https://remotive.com/api/remote-jobs?limit=100")
            if r.status_code != 200:
                return []
            for item in r.json().get("jobs", []):
                title = item.get("title", "").strip()
                link  = item.get("url", "").strip()
                if not title or not link:
                    continue
                jobs.append({
                    "id":         make_id("rm", item.get("id", "")),
                    "title":      title,
                    "company":    item.get("company_name", "Unknown"),
                    "location":   "Remote",
                    "category":   categorize(title),
                    "apply_link": link,
                    "source":     "Remotive",
                })
        print(f"  [Remotive] ✅ {len(jobs)} jobs")
    except Exception as e:
        print(f"  [Remotive] ❌ {e}")
    return jobs


# ── 4. THE MUSE ───────────────────────────────────────────────────────────────
async def fetch_themuse(pages: int = 3) -> List[dict]:
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            for page in range(1, pages + 1):
                r = await client.get(
                    f"https://www.themuse.com/api/public/jobs?page={page}&descending=true"
                )
                if r.status_code != 200:
                    break
                for item in r.json().get("results", []):
                    title = item.get("name", "").strip()
                    link  = item.get("refs", {}).get("landing_page", "").strip()
                    if not title or not link:
                        continue
                    locs     = item.get("locations", [])
                    location = locs[0].get("name", "Remote") if locs else "Remote"
                    jobs.append({
                        "id":         make_id("tm", item.get("id", "")),
                        "title":      title,
                        "company":    item.get("company", {}).get("name", "Unknown"),
                        "location":   location,
                        "category":   categorize(title),
                        "apply_link": link,
                        "source":     "The Muse",
                    })
        print(f"  [TheMuse] ✅ {len(jobs)} jobs")
    except Exception as e:
        print(f"  [TheMuse] ❌ {e}")
    return jobs


# ── 5. AMAZON (amazon.jobs public JSON API) ───────────────────────────────────
async def fetch_amazon(pages: int = 5) -> List[dict]:
    """
    Amazon has a public undocumented JSON API used by their own website.
    Returns up to pages*10 jobs.
    """
    jobs = []
    base = "https://www.amazon.jobs/en/search.json"
    params_base = {
        "result_limit": 10,
        "sort":         "recent",
        "category[]":   "software-development",
        "facets[]":     ["category", "location", "business_category"],
    }
    try:
        async with httpx.AsyncClient(timeout=20, headers={
            **HEADERS,
            "Referer": "https://www.amazon.jobs/en/search",
        }) as client:
            for page in range(pages):
                params = {**params_base, "offset": page * 10}
                r = await client.get(base, params=params)
                if r.status_code != 200:
                    print(f"  [Amazon] Page {page} HTTP {r.status_code}")
                    break
                data = r.json()
                results = data.get("jobs", [])
                if not results:
                    break
                for item in results:
                    title = item.get("title", "").strip()
                    job_id = item.get("id_icims", item.get("job_id", ""))
                    link  = f"https://www.amazon.jobs/en/jobs/{job_id}" if job_id else ""
                    if not title or not link:
                        continue
                    loc_list = item.get("normalized_location", "")
                    location = loc_list if isinstance(loc_list, str) else "Remote"
                    jobs.append({
                        "id":         make_id("amz", job_id),
                        "title":      title,
                        "company":    "Amazon",
                        "location":   location or "USA",
                        "category":   categorize(title),
                        "apply_link": link,
                        "source":     "Amazon",
                    })
        print(f"  [Amazon] ✅ {len(jobs)} jobs")
    except Exception as e:
        print(f"  [Amazon] ❌ {e}")
    return jobs


# ── 6. GOOGLE (careers.google.com JSON API) ───────────────────────────────────
async def fetch_google(pages: int = 5) -> List[dict]:
    """
    Google's careers page loads jobs via a public JSON endpoint.
    """
    jobs = []
    base = "https://careers.google.com/api/v3/search/"
    try:
        async with httpx.AsyncClient(timeout=20, headers={
            **HEADERS,
            "Referer": "https://careers.google.com/",
        }) as client:
            for page in range(pages):
                params = {
                    "page":     page + 1,
                    "pageSize": 20,
                    "sort_by":  "date",
                }
                r = await client.get(base, params=params)
                if r.status_code != 200:
                    print(f"  [Google] Page {page+1} HTTP {r.status_code}")
                    break
                data = r.json()
                results = data.get("jobs", [])
                if not results:
                    break
                for item in results:
                    title = item.get("title", "").strip()
                    job_id = item.get("job_id", "")
                    link  = f"https://careers.google.com/jobs/results/{job_id}/" if job_id else ""
                    if not title or not link:
                        continue
                    locs     = item.get("locations", [])
                    location = locs[0].get("display", "USA") if locs else "USA"
                    jobs.append({
                        "id":         make_id("goog", job_id),
                        "title":      title,
                        "company":    "Google",
                        "location":   location,
                        "category":   categorize(title),
                        "apply_link": link,
                        "source":     "Google",
                    })
        print(f"  [Google] ✅ {len(jobs)} jobs")
    except Exception as e:
        print(f"  [Google] ❌ {e}")
    return jobs


# ── MASTER COLLECTOR ──────────────────────────────────────────────────────────
async def collect_all_jobs() -> int:
    print("\n" + "="*50)
    print("🔍 COLLECTING JOBS FROM ALL PLATFORMS")
    print("="*50)

    all_jobs = []

    print("\n📦 Greenhouse:")
    for company in GREENHOUSE_COMPANIES:
        all_jobs.extend(await fetch_greenhouse(company))

    print("\n📦 Lever:")
    for company in LEVER_COMPANIES:
        all_jobs.extend(await fetch_lever(company))

    print("\n📦 Remotive:")
    all_jobs.extend(await fetch_remotive())

    print("\n📦 The Muse:")
    all_jobs.extend(await fetch_themuse(pages=3))

    print("\n📦 Amazon:")
    all_jobs.extend(await fetch_amazon(pages=5))

    print("\n📦 Google:")
    all_jobs.extend(await fetch_google(pages=5))

    new_count = 0
    for job in all_jobs:
        if job.get("title") and job.get("apply_link"):
            if await save_job(job):
                new_count += 1

    print(f"\n✅ Done: {new_count} new jobs added ({len(all_jobs)} total fetched)")
    print("="*50 + "\n")
    return new_count