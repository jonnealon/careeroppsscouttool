#!/usr/bin/env python3
"""
Weekly Opportunity Scout for Jon Nealon
Searches for jobs, fellowships, grants, and gigs relevant to geospatial journalism / ISI.
Sends a curated digest via Gmail.
"""

import anthropic
import smtplib
import os
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Configuration ─────────────────────────────────────────────────────────────

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]          # your email
SENDER_EMAIL    = os.environ["GMAIL_SENDER_EMAIL"]       # gmail address sending from
GMAIL_APP_PW    = os.environ["GMAIL_APP_PASSWORD"]       # Gmail App Password (not your login pw)
ANTHROPIC_KEY   = os.environ["ANTHROPIC_API_KEY"]

# ── Search queries ─────────────────────────────────────────────────────────────
# Tuned to Jon's profile: geospatial journalism, human rights documentation,
# investigative documentary production/editing, longform writing, GIS, OSINT,
# fellowship/grant/faculty opportunities, high-prestige and human rights work.

SEARCH_QUERIES = [
    # Fellowships & grants — investigative journalism
    "investigative journalism fellowship grant 2026 open applications deadline",
    "geospatial journalism human rights fellowship 2026",
    "Pulitzer Center grant open applications 2026",
    "Knight Foundation journalism research grant open 2026",
    "MacArthur Ford Open Society journalism media grant 2026",
    "Alicia Patterson FIJ fellowship journalism 2026",
    "Nieman fellowship Harvard journalism 2026 applications",
    "Reuters Institute fellowship Oxford journalism 2026",
    "Shorenstein Center fellowship Harvard media politics 2026",

    # Academic / teaching
    "professor of practice journalist in residence journalism school hiring 2026",
    "adjunct lecturer data journalism GIS digital investigative faculty position 2026",
    "journalism school GIS geospatial curriculum developer instructor 2026",

    # Newsroom & consulting — geospatial / visual / OSINT
    "visual investigations OSINT geospatial journalist job hiring 2026",
    "human rights documentation geospatial consultant NGO hiring 2026",
    "NYT ProPublica BBC visual investigations producer hiring 2026",

    # Documentary production & directing
    "investigative documentary producer director commission 2026 PBS FRONTLINE",
    "documentary series executive producer senior producer human rights 2026",
    "Netflix HBO documentary development investigative commission 2026",
    "documentary filmmaker grant commission human rights conflict 2026",
    "POV documentary funding commission open 2026",
    "Sundance documentary fund grant 2026 open applications",

    # Longform writing & editing commissions
    "longform investigative journalist commission essay 2026 Atlantic Harper's New Yorker",
    "senior editor investigative longform journalism hiring 2026",
    "public intellectual writing fellowship essay grant 2026",
    "CJR Columbia Journalism Review contributor commission 2026",

    # High-prestige / awards / named fellowships
    "Guggenheim fellowship journalism media 2026",
    "Pulitzer Prize center reporting grant immigration human rights 2026",
    "Open Society fellowship media democracy 2026",
    "ICIJ International Consortium Investigative Journalists fellowship collaboration 2026",

    # Human rights — legal, tribunal, international bodies
    "human rights documentation consultant ICC UNITAD tribunal geospatial 2026",
    "Amnesty International Human Rights Watch consultant investigator hiring 2026",
    "UN human rights OHCHR consultant investigative journalist 2026",
    "war crimes documentation open source investigator position 2026",

    # Immigration / detention angle
    "immigration detention investigative journalist fellowship grant 2026",

    # European / international
    "digital methods journalism European fellowship 2026 funded",
    "Marie Curie individual fellowship journalism media 2026",
    "European Journalism Centre fellowship grant 2026",
]

# ── Profile context passed to the AI ──────────────────────────────────────────

PROFILE = """
Jon Nealon is an Emmy- and Peabody-nominated investigative journalist, documentary filmmaker,
writer, and editor completing an MS in Geographic Information Sciences at University at Albany
(exp. Spring 2027). He is building the Institute for Spatial Inquiry (ISI), focused on
geospatial journalism as a discipline at the intersection of investigative reporting, critical
cartography, human rights documentation, and spatial cognition.

DOCUMENTARY PRODUCTION & DIRECTING:
- Emmy-nominated and Peabody-nominated documentary producer/director (FRONTLINE/PBS)
- "Crime Scene Bucha" — acclaimed investigation into Russian war crimes in Ukraine using
  geospatial and open-source evidence; widely covered by BBC, CNN, NYT
- Active documentary series: "Deportation Inc" (producing with SITU Research), a video
  investigation series into ICE Air deportation and detention systems
- "Torpedo / Quiet Death" — short-form investigative doc in development (Mk-48 torpedo
  program, defense procurement); targeting FRONTLINE, The Atlantic, NYT Op-Docs
- Deep experience with geospatial evidence, 3D reconstruction, and satellite imagery
  as narrative tools in documentary storytelling
- Experienced story producer, editor, and correspondent for long-form documentary

WRITING & EDITING:
- Longform investigative journalist with publication history across major outlets
- Academic writer: papers under review at Digital Journalism and Environment & Planning C
- Public intellectual voice bridging geospatial methods, human rights, and policy
- Experienced editor; can story-edit, script-edit, and develop investigative narratives
  for other journalists and documentary projects

GEOSPATIAL / OSINT / INVESTIGATIVE:
- Geospatial investigation: ICE Air deportation flight network (ShuffleMap), Alligator
  Alcatraz (hydrological/satellite analysis of ICE detention site), migrant busing
  political value analysis
- OSINT: ADS-B flight tracking, satellite imagery analysis (Google Earth Engine),
  network visualization, open-source verification
- Collaborators: SITU Research (Brad Samuels), NYT Visual Investigations (Helmuth Rosales)
- McGraw Fellowship submitted (ICE Voluntary Work Program as forced labor investigation)
- Pulitzer Center application submitted (Alligator Alcatraz)

HUMAN RIGHTS:
- War crimes documentation experience (Bucha, Ukraine)
- Immigration detention and deportation investigations (forced labor, carceral geography)
- Theoretical framework: migrant body commodification (co-authored with Dr. Kate Coddington,
  under review at Environment & Planning C; accepted at RGS-IBG, TMC Bratislava, Vienna)
- Network includes Human Rights Watch, Human Rights First, Earthjustice, SITU Research,
  and UNITAD-adjacent contacts
- Litigation-adjacent credibility: work used in legal proceedings and accountability contexts

ACADEMIC & INSTITUTIONAL:
- MS in GIS, University at Albany (advisor Dr. Kate Coddington)
- Accepted: UCGIS 2026, RGS-IBG, TMC Bratislava, Vienna Migration Research Conference
- DMI Summer School Amsterdam (June 2026) — primary European institutional anchor
- ISI operates as DBA under Moldy Tapes LLC
- Pursuing Italian citizenship for EU access (Horizon Europe, Marie Curie fellowships)

IDEAL OPPORTUNITIES (prioritize these):
- High-prestige fellowships: Nieman, Guggenheim, Reuters Institute, Shorenstein, OSF,
  Alicia Patterson, MacArthur, Knight, Pulitzer Center
- Documentary commissions and co-productions: PBS, FRONTLINE, Netflix, HBO, BBC,
  POV, Sundance Fund — investigative, human rights, immigration, environment, conflict
- Longform writing commissions: The Atlantic, Harper's, New Yorker, NYT Magazine,
  CJR, The Baffler — investigative essays, public intellectual work
- Human rights consulting: ICC, UNITAD, HRW, Amnesty, UN OHCHR — geospatial evidence,
  open-source investigation, documentation
- Professor of Practice / Journalist-in-Residence at journalism schools
- Senior editor or story consultant roles for investigative documentary projects
- European academic fellowships (especially funded, post-EU citizenship)

NOT interested in: pure GIS/remote sensing academic roles requiring a PhD, entry-level
positions or internships, Africa-specific regional fellowships, military/defense OSINT,
production coordinator or PA roles, anything below senior/principal level in production.
"""

# ── Core functions ─────────────────────────────────────────────────────────────

def run_searches(client: anthropic.Anthropic) -> list[dict]:
    """Run all search queries using the web search tool, collect raw results."""
    all_results = []

    for query in SEARCH_QUERIES:
        print(f"  Searching: {query}")
        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1500,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{
                    "role": "user",
                    "content": (
                        f"Search for: {query}\n\n"
                        "Return a JSON array of up to 5 results. Each result must have:\n"
                        "  title, url, snippet (2-3 sentences), deadline (if found, else null), "
                        "  source_org, opportunity_type (fellowship|grant|job|consulting|academic|other)\n"
                        "Return ONLY the JSON array, no preamble or markdown fences."
                    )
                }]
            )

            # Extract text from response
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text

            # Parse JSON
            text = text.strip()
            if text.startswith("["):
                results = json.loads(text)
                for r in results:
                    r["_query"] = query
                all_results.extend(results)

        except Exception as e:
            print(f"    Error on query '{query}': {e}")
            continue

    return all_results


def curate_and_format(client: anthropic.Anthropic, raw_results: list[dict]) -> str:
    """Send raw results to Claude for curation, dedup, ranking, and HTML formatting."""

    results_json = json.dumps(raw_results, indent=2)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""You are helping Jon Nealon track opportunities relevant to his career.

Here is his profile:
{PROFILE}

Here are raw search results collected this week (may include duplicates):
{results_json}

Your task:
1. Deduplicate (same opportunity appearing from multiple queries = one entry).
2. Filter ruthlessly: remove anything clearly irrelevant (wrong region, requires PhD he doesn't
   have, entry-level, defense/military OSINT, PA/coordinator roles, opportunities whose
   deadlines have clearly already passed).
3. Score each remaining item on two axes:
   - FIT (1-5): how well it matches Jon's specific skills and investigations
   - PRESTIGE (1-5): how career-advancing or field-defining the opportunity is
     (5 = Nieman/Guggenheim/FRONTLINE commission; 1 = small regional grant)
4. Rank by combined score. Aim for 10-18 items total.
5. For each item, write a 1-2 sentence "why this fits Jon" note that references his
   specific work (Crime Scene Bucha, Deportation Inc, ICE VWP, Alligator Alcatraz,
   the hot air balloon paper, migrant body commodification framework, etc.) where relevant.
6. Flag any item with a deadline within 30 days as URGENT.
7. Group into these categories (only show categories that have results):
   - 🏆 High Prestige Fellowships
   - 🎬 Documentary & Production
   - ✍️ Writing & Editing
   - ⚖️ Human Rights & Legal
   - 🗺 Geospatial & Investigative
   - 🎓 Academic & Teaching
   - 💰 Grants & Funding

Output clean HTML suitable for embedding in an email body. Use this structure:

<h2 style="color:#1a1a2e;font-family:Georgia,serif;">🗺 Weekly Opportunity Scout</h2>
<p style="color:#555;font-family:Arial,sans-serif;font-size:14px;">
  Week of {datetime.now().strftime("%B %d, %Y")} — curated for Jon Nealon / ISI
</p>

Then for each category that has results, use a section header like:
<h3 style="color:#c0392b;font-family:Georgia,serif;border-bottom:2px solid #eee;padding-bottom:4px;">
  🏆 High Prestige Fellowships
</h3>

And for each opportunity:
<div style="margin-bottom:20px;padding:14px;background:#f9f9f9;border-left:4px solid #3498db;border-radius:3px;">
  <p style="margin:0 0 4px 0;">
    <strong><a href="URL" style="color:#2980b9;text-decoration:none;">TITLE</a></strong>
    — <span style="color:#7f8c8d;font-size:12px;">SOURCE ORG</span>
    &nbsp;<span style="color:#999;font-size:11px;">fit: FIT/5 · prestige: PRESTIGE/5</span>
    [if urgent: &nbsp;<span style="background:#e74c3c;color:white;padding:2px 6px;border-radius:3px;font-size:11px;">⚡ DEADLINE: DATE</span>]
  </p>
  <p style="margin:4px 0;font-size:13px;color:#333;">SNIPPET</p>
  <p style="margin:4px 0;font-size:12px;color:#27ae60;font-style:italic;">→ WHY THIS FITS JON</p>
</div>

End with a footer:
<p style="font-size:11px;color:#aaa;margin-top:30px;border-top:1px solid #eee;padding-top:10px;">
  Generated by ISI Opportunity Scout · {datetime.now().strftime("%Y-%m-%d")}
</p>

Output ONLY the HTML, nothing else.
"""
        }]
    )

    return response.content[0].text


def send_email(html_body: str):
    """Send the digest via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🗺 ISI Opportunity Scout — {datetime.now().strftime('%b %d, %Y')}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    # Plain text fallback
    plain = "Weekly opportunity digest — view in an HTML-capable email client."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_APP_PW)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"  Email sent to {RECIPIENT_EMAIL}")


def main():
    print(f"\n=== ISI Opportunity Scout — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print("Step 1: Running web searches...")
    raw = run_searches(client)
    print(f"  Collected {len(raw)} raw results\n")

    print("Step 2: Curating and formatting...")
    html = curate_and_format(client, raw)
    print(f"  HTML digest generated ({len(html)} chars)\n")

    print("Step 3: Sending email...")
    send_email(html)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
