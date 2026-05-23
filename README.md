<div align="center">

```
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

**Autonomous Job Hunting Agent System**  
*Hunt while you sleep. Apply while you grind.*

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Cost](https://img.shields.io/badge/Cost-₹0_Forever-00C851?style=for-the-badge&logo=cashapp&logoColor=white)
![Status](https://img.shields.io/badge/Status-Actively_Hunting-FF6B35?style=for-the-badge)

</div>

---

## ⚡ What Is NEXUS?

NEXUS is a **fully autonomous, zero-cost job hunting system** that runs on GitHub Actions — 24/7, even when your laptop is off. It scrapes job listings, finds HR email addresses, tailors your resume with ATS-killing keywords, and fires off personalized cold emails. All while you sleep.

No manual searching. No copy-pasting. No begging job portals.  
**You set it once. NEXUS runs forever.**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (Every 12hr)                   │
│                    7:30 AM IST  |  7:30 PM IST                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │     main.py      │
              │  Pipeline Runner │
              └────────┬─────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌─────────────────┐       ┌──────────────────┐
│  🔍 SCOUT       │       │  📬 MAILER        │
│                 │       │                  │
│ • Naukri.com    │──────▶│ • Parse base PDF  │
│ • LinkedIn      │       │ • Keyword gap     │
│ • Career portals│       │   analysis (Groq) │
│ • 18 top cos    │       │ • Rewrite resume  │
│                 │       │ • Compose email   │
│ → Find HR email │       │ • Send via Gmail  │
│   Hunter.io     │       │ • Log to SQLite   │
│   Apollo.io     │       │                  │
│   Pattern guess │       │ Max 10/run        │
└─────────────────┘       └──────────────────┘
          │                         │
          └────────────┬────────────┘
                       ▼
              ┌─────────────────┐
              │   data/jobs.db  │
              │   sent_log.json │
              │  (git committed)│
              └─────────────────┘
```

---

## 📁 Project Structure

```
NEXUS/
│
├── 🔍 scout/                        # Agent 1 — Finds jobs & HR emails
│   ├── scrapers/
│   │   ├── naukri_scraper.py        # Naukri.com (authenticated)
│   │   ├── linkedin_scraper.py      # LinkedIn public listings
│   │   ├── company_portal_scraper.py
│   │   └── top_companies_scraper.py # Direct career page hunting
│   ├── email_finder/
│   │   ├── hunter_client.py         # Hunter.io API
│   │   ├── apollo_client.py         # Apollo.io API
│   │   └── pattern_guesser.py       # hr@, careers@, talent@ fallback
│   ├── filters/
│   │   └── job_filter.py            # Match scoring engine
│   └── scout_agent.py               # Scout orchestrator
│
├── 📬 mailer/                       # Agent 2 — Tailors & sends
│   ├── resume/
│   │   ├── base_resume.pdf          # ← YOUR RESUME GOES HERE
│   │   ├── resume_parser.py         # PDF text extraction
│   │   └── resume_tailor.py         # Groq-powered keyword injection
│   ├── email/
│   │   ├── email_composer.py        # Groq cold email writer
│   │   └── email_sender.py          # Gmail SMTP
│   └── mailer_agent.py              # Mailer orchestrator
│
├── 🔧 shared/
│   ├── models.py                    # Pydantic v2 data models
│   ├── db.py                        # SQLite CRUD operations
│   └── logger.py                    # Unified logging
│
├── 📊 data/
│   ├── jobs.db                      # SQLite job tracker (auto-created)
│   ├── sent_log.json                # Full email audit trail
│   ├── api_usage.json               # Free tier credit tracker
│   └── top_companies.json           # 18 Indian tech company targets
│
├── ⚙️ .github/
│   └── workflows/
│       └── nexus_run.yml            # Cron scheduler
│
├── config.py                        # Central env config
├── main.py                          # Entry point
├── .env.example                     # Secret keys template
└── requirements.txt
```

---

## 🎯 Target Companies (Hardcoded)

NEXUS proactively checks these companies' career pages every run:

| Company | Domain |
|---------|--------|
| Razorpay | Fintech |
| Zepto | Quick Commerce |
| CRED | Fintech |
| Groww | Investment |
| Flipkart | E-Commerce |
| Swiggy | Food Tech |
| Zomato | Food Tech |
| PhonePe | Payments |
| Meesho | E-Commerce |
| BrowserStack | Dev Tools |
| Postman | Dev Tools |
| InfraCloud | Cloud Native |
| HashedIn | Consulting |
| Thoughtworks | Consulting |
| CloudSEK | Cybersecurity |
| Sigmoid | Data Engineering |
| Ola | Mobility |
| Paytm | Fintech |

---

## 🧠 Resume Tailoring Logic

NEXUS **never fabricates experience**. It only injects keywords where they genuinely fit.

```
Job Description (JD)
       ↓
[Groq] Extract top 20 ATS keywords
       ↓
Compare against base resume
       ↓
Identify keyword gaps
       ↓
[Groq] Rewrite resume sections naturally
       ↓
Generate tailored PDF via fpdf2
       ↓
Attach to cold email
```

**Example:** JD requires `Helm` → GhostOps project description updated to mention Helm chart deployments (only if legitimately applicable).

---

## 📧 Cold Email Strategy

- **Personalized** to company name and role
- **150-200 words** — short enough to read, long enough to impress
- References **specific projects** relevant to the JD
- Clear **CTA** — never generic
- **3-5 minute delay** between sends (spam filter bypass)
- **Max 10 emails per run**
- **Never emails same company twice** within 30 days

---

## 💰 Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| GitHub Actions | 2 runs/day × ~5min = ~300min/month | **FREE** (2000min limit) |
| Groq API (LLaMA 3.3 70B) | Resume + email generation | **FREE** tier |
| Hunter.io | HR email lookup | **FREE** (25/month) |
| Apollo.io | HR email backup | **FREE** (50/month) |
| Gmail SMTP | Email sending | **FREE** |
| SQLite | Job database | **FREE** (it's a file) |
| **TOTAL** | | **₹0** |

---

## 🚀 Setup Guide

### Step 1 — Clone & Install

```bash
git clone https://github.com/DEV-GHILDIYAL/NEXUS.git
cd NEXUS
pip install -r requirements.txt
playwright install chromium
```

### Step 2 — Add Your Resume

```bash
cp your_resume.pdf mailer/resume/base_resume.pdf
```

### Step 3 — Get API Keys (All Free)

| Key | Where |
|-----|-------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → Create API Key |
| `HUNTER_API_KEY` | [hunter.io](https://hunter.io) → Sign up → Dashboard |
| `APOLLO_API_KEY` | [apollo.io](https://app.apollo.io) → Sign up → API |
| `GMAIL_APP_PASSWORD` | Gmail → Manage Account → Security → 2FA → App Passwords |

### Step 4 — Configure Secrets

```bash
cp .env.example .env
# Edit .env with your actual keys
```

For GitHub Actions, add each key under:  
`Repo → Settings → Secrets and variables → Actions → New repository secret`

```
GROQ_API_KEY
HUNTER_API_KEY
APOLLO_API_KEY
GMAIL_ADDRESS
GMAIL_APP_PASSWORD
NAUKRI_EMAIL
NAUKRI_PASSWORD
```

### Step 5 — Naukri Session Setup

Naukri requires a logged-in session for scraping. Run this once locally:

```bash
python scout/scrapers/naukri_scraper.py --export-cookies
# Opens browser → Login manually → Cookies auto-saved to data/naukri_cookies.json
```

### Step 6 — Test Run

```bash
python main.py --dry-run    # Scrapes + finds emails, NO emails sent
python main.py              # Full run
```

### Step 7 — Deploy to GitHub Actions

```bash
git add .
git commit -m "NEXUS: initial deployment"
git push
```

Actions will trigger automatically on schedule. Check the **Actions** tab to monitor runs.

> ⚠️ **Make your repo PRIVATE** before pushing. `jobs.db` and `sent_log.json` contain email addresses and company data.

---

## 🗄️ Database Schema

```sql
CREATE TABLE jobs (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    title                TEXT,
    company              TEXT,
    domain               TEXT,
    job_url              TEXT,
    jd_text              TEXT,
    hr_email             TEXT,
    email_source         TEXT,    -- 'hunter' | 'apollo' | 'pattern'
    match_score          REAL,    -- 0.0 → 1.0
    status               TEXT,    -- 'new' | 'sent' | 'failed' | 'no_email'
    found_at             TIMESTAMP,
    sent_at              TIMESTAMP,
    tailored_resume_path TEXT,
    UNIQUE(company, title, date(found_at))
);
```

---

## 📊 Monitoring

After each run, NEXUS commits updated logs back to the repo:

```bash
# Check what was sent
cat data/sent_log.json | python -m json.tool

# Check job pipeline
sqlite3 data/jobs.db "SELECT company, title, status, sent_at FROM jobs ORDER BY found_at DESC LIMIT 20;"

# Check API credits remaining
cat data/api_usage.json
```

---

## ⚡ GitHub Actions Schedule

```yaml
cron: '0 2,14 * * *'
# Runs at:
# → 02:00 UTC = 07:30 AM IST
# → 14:00 UTC = 07:30 PM IST
```

Manual trigger also available from the Actions tab anytime.

---

## 🛡️ Safeguards

- ✅ Never emails same company twice within 30 days
- ✅ Never fabricates experience in resume
- ✅ Pauses Hunter.io when < 3 credits remain
- ✅ Exponential backoff on Groq rate limits
- ✅ Max 10 emails per run (realistic, not spammy)
- ✅ 3-5 min randomized delay between sends
- ✅ Dry-run mode for testing without sending

---

## 🔮 Roadmap

- [ ] Telegram bot notifications (job found / email sent alerts)
- [ ] Dashboard — simple HTML page showing stats
- [ ] Internshala support
- [ ] ATS score before/after comparison
- [ ] Auto-follow-up email after 7 days of no response

---

<div align="center">

**Built by [Dev Lalit Ghildiyal](https://github.com/DEV-GHILDIYAL)**  
*DevOps Engineer · Mumbai, India*

*"The best time to apply was yesterday. The second best time is while you're asleep."*

</div>
