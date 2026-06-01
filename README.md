# ISI Opportunity Scout

Runs weekly via GitHub Actions. Searches for fellowships, grants, academic roles, and consulting
gigs relevant to geospatial journalism / ISI. Sends a curated HTML digest to your Gmail.

---

## Setup (one-time, ~10 minutes)

### 1. Add files to your GitHub repo

Put these two files in a GitHub repo (private is fine — can be your existing one):

```
opportunity_scout/scout.py
.github/workflows/scout.yml
```

### 2. Get a Gmail App Password

Regular Gmail passwords don't work with SMTP. You need an App Password:

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Go to **Security → 2-Step Verification → App passwords** (scroll to bottom)
4. Select app: **Mail** / device: **Other** → name it "ISI Scout"
5. Copy the 16-character password (you won't see it again)

### 3. Add GitHub Secrets

In your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these four secrets:

| Secret name          | Value                                      |
|----------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY`  | Your Anthropic API key (from console.anthropic.com) |
| `GMAIL_SENDER_EMAIL` | The Gmail address sending the email        |
| `GMAIL_APP_PASSWORD` | The 16-char App Password from Step 2       |
| `RECIPIENT_EMAIL`    | Where you want the digest sent             |

`GMAIL_SENDER_EMAIL` and `RECIPIENT_EMAIL` can be the same address (email yourself).

### 4. Test it

In your repo → **Actions → ISI Opportunity Scout → Run workflow** → click **Run workflow**.

Check your inbox within ~5 minutes. If nothing arrives, check the Actions log for errors.

---

## Schedule

Runs every **Monday at 8 AM ET**. Change the cron line in `scout.yml` if you want a different day/time.

Cron reference: `"0 13 * * 1"` = minute 0, hour 13 UTC, any day-of-month, any month, Monday (1).

---

## Customizing the searches

Edit `SEARCH_QUERIES` in `scout.py` to add, remove, or modify search topics.
Edit `PROFILE` to update your bio/interests as your situation evolves.

---

## Cost estimate

Each weekly run makes ~14 web searches + 1 curation call. Using claude-opus-4-5.
Approximate cost per run: **$0.10–0.25**. Roughly **$5–12/year**.
