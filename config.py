import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_PATH = os.getenv("DB_PATH", "jobs.db")
DB_NAME = DB_PATH
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", 60))

# ── Skills ────────────────────────────────────────────────────────────────────
SKILLS = [
    "Python", "Java", "JavaScript", "React", "Node.js",
    "Data Science", "ML/AI", "DevOps", "Testing/QA",
    "Android", "iOS", "Full Stack", "Backend", "Frontend", "Any"
]

# ── Companies shown to user as buttons ───────────────────────────────────────
# Format: "Display Name": "slug_used_in_api"
COMPANIES = {
    # 🇮🇳 Indian IT Giants (scraped via their career pages using Greenhouse/Lever)
    "TCS":          "tcs",
    "Infosys":      "infosys",
    "Wipro":        "wipro",
    "HCL":          "hcltech",
    # 🌐 Big Tech
    "Google":       "google",
    "Microsoft":    "microsoft",
    "Amazon":       "amazon",
    "Meta":         "meta",
    "Apple":        "apple",
    # 💼 Consulting MNCs
    "Accenture":    "accenture",
    "Capgemini":    "capgemini",
    "Cognizant":    "cognizant",
    # 🚀 Startups (Greenhouse)
    "Stripe":       "stripe",
    "Shopify":      "shopify",
    "Notion":       "notion",
    "Figma":        "figma",
    "Coinbase":     "coinbase",
    # 🎯 Lever companies
    "Netflix":      "netflix",
    "Reddit":       "reddit",
    "Canva":        "canva",
    "Postman":      "postman",
    # 🌍 Other popular
    "Any":          "any",
}

# ── Greenhouse slugs (these work with free API) ───────────────────────────────
GREENHOUSE_COMPANIES = [
    "stripe", "shopify", "notion", "figma",
    "coinbase", "dropbox", "pinterest", "twitch",
]

# ── Lever slugs (these work with free API) ────────────────────────────────────
LEVER_COMPANIES = [
    "netflix", "reddit", "postman", "canva",
    "plaid", "robinhood",
]

# ── Company name aliases for DB matching ──────────────────────────────────────
# Maps display name → keywords to search in company column in DB
COMPANY_ALIASES = {
    "TCS":        ["tcs", "tata consultancy"],
    "Infosys":    ["infosys"],
    "Wipro":      ["wipro"],
    "HCL":        ["hcl"],
    "Google":     ["google", "alphabet"],
    "Microsoft":  ["microsoft"],
    "Amazon":     ["amazon", "aws"],
    "Meta":       ["meta", "facebook"],
    "Apple":      ["apple"],
    "Accenture":  ["accenture"],
    "Capgemini":  ["capgemini"],
    "Cognizant":  ["cognizant"],
    "Stripe":     ["stripe"],
    "Shopify":    ["shopify"],
    "Notion":     ["notion"],
    "Figma":      ["figma"],
    "Coinbase":   ["coinbase"],
    "Netflix":    ["netflix"],
    "Reddit":     ["reddit"],
    "Canva":      ["canva"],
    "Postman":    ["postman"],
    "Any":        [],  # no company filter
}