"""Scrapes public GitHub data and renders it like a Grafana board.

Outputs:
  assets/dashboard.svg          - observability-style stats dashboard
  README.md (ACTIVITY markers)  - latest public events, kubectl-logs style

Stdlib only. Uses GITHUB_TOKEN when present (GraphQL contribution calendar),
otherwise falls back to the public contributions page.
"""
import datetime as dt
import json
import os
import re
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path

USER = os.environ.get("GH_USER", "DEV-GHILDIYAL")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = Path(__file__).resolve().parent.parent
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Java": "#b07219",
    "C#": "#178600", "HTML": "#e34c26", "CSS": "#663399", "Go": "#00ADD8", "Shell": "#89e051",
    "HCL": "#844FBA", "Dockerfile": "#384d54", "ShaderLab": "#222c37",
}


def http(url, data=None):
    headers = {"User-Agent": f"{USER}-profile-bot", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def api(path):
    return json.loads(http(f"https://api.github.com{path}"))


def calendar():
    """Returns [(date, count)] for the last year, oldest first."""
    if TOKEN:
        q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar"
                      "{weeks{contributionDays{date contributionCount}}}}}}", "variables": {"u": USER}}
        res = json.loads(http("https://api.github.com/graphql", json.dumps(q).encode()))
        weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    page = http(f"https://github.com/users/{USER}/contributions")
    dates = dict(re.findall(r'data-date="([\d-]+)" id="([^"]+)"', page))
    dates = {v: k for k, v in dates.items()}
    days = []
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)', page):
        m = re.match(r"(\d+) contribution", text)
        if cid in dates:
            days.append((dates[cid], int(m.group(1)) if m else 0))
    return sorted(days)


def streaks(days):
    longest = cur = 0
    for _, c in days:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    current = 0
    for i, (_, c) in enumerate(reversed(days)):
        if c:
            current += 1
        elif i == 0:
            continue  # today not counted yet
        else:
            break
    return current, longest


def human(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def stat_panel(x, title, value, color, unit=""):
    return f"""<g transform="translate({x},56)">
    <rect width="138" height="92" rx="8" fill="#181b1f" stroke="#2c3235"/>
    <text x="12" y="22" font-family="{SANS}" font-size="12" fill="#ccccdc" font-weight="600">{escape(title)}</text>
    <text x="69" y="68" text-anchor="middle" font-family="{SANS}" font-size="32" font-weight="700" fill="{color}">{escape(value)}<tspan font-size="14" fill="#8e8e8e">{escape(unit)}</tspan></text>
  </g>"""


def timeseries(days, x, y, w, h):
    weeks = [sum(c for _, c in days[i:i + 7]) for i in range(0, len(days), 7)][-52:]
    peak = max(weeks + [1])
    step = (w - 40) / max(len(weeks) - 1, 1)
    pts = [(x + 28 + i * step, y + h - 26 - (v / peak) * (h - 66)) for i, v in enumerate(weeks)]
    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    area = f"M{pts[0][0]:.1f},{y + h - 26} L" + line.replace(" ", " L") + f" L{pts[-1][0]:.1f},{y + h - 26} Z"
    grid = "".join(
        f'<path d="M{x + 28} {y + h - 26 - f * (h - 66):.1f}H{x + w - 12}" stroke="#2c3235"/>'
        f'<text x="{x + 22}" y="{y + h - 22 - f * (h - 66):.1f}" text-anchor="end" font-family="{MONO}" font-size="9" fill="#8e8e8e">{round(peak * f)}</text>'
        for f in (0, .5, 1))
    lx, ly = pts[-1]
    return f"""<g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#181b1f" stroke="#2c3235"/>
    <text x="{x + 12}" y="{y + 22}" font-family="{SANS}" font-size="12" fill="#ccccdc" font-weight="600">contributions / week · last 52w</text>
    {grid}
    <path d="{area}" fill="url(#area)"/>
    <polyline points="{line}" fill="none" stroke="#00D4FF" stroke-width="2" stroke-linejoin="round"
      stroke-dasharray="3000" stroke-dashoffset="3000"><animate attributeName="stroke-dashoffset" to="0" dur="2.5s" fill="freeze"/></polyline>
    <circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="#00D4FF"><animate attributeName="r" values="3;6;3" dur="1.6s" repeatCount="indefinite"/></circle>
  </g>"""


def langs_panel(langs, x, y, w, h):
    total = sum(langs.values()) or 1
    rows = []
    for i, (name, n) in enumerate(langs.most_common(6)):
        pct = n / total
        bw = (w - 140) * pct
        ry = y + 44 + i * 26
        col = LANG_COLORS.get(name, "#8e8e8e")
        rows.append(f"""<text x="{x + 12}" y="{ry + 11}" font-family="{MONO}" font-size="11" fill="#ccccdc">{escape(name)}</text>
    <rect x="{x + 96}" y="{ry}" width="{w - 140}" height="14" rx="3" fill="#22252b"/>
    <rect x="{x + 96}" y="{ry}" width="0" height="14" rx="3" fill="{col}"><animate attributeName="width" to="{bw:.1f}" dur="1.2s" begin="{i * .12:.2f}s" fill="freeze"/></rect>
    <text x="{x + w - 10}" y="{ry + 11}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#8e8e8e">{pct:.0%}</text>""")
    return f"""<g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#181b1f" stroke="#2c3235"/>
    <text x="{x + 12}" y="{y + 22}" font-family="{SANS}" font-size="12" fill="#ccccdc" font-weight="600">languages · by repo</text>
    {''.join(rows)}
  </g>"""


def dashboard(user, repos, days):
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = Counter(r["language"] for r in own if r["language"])
    year = sum(c for _, c in days)
    cur, longest = streaks(days)
    now = dt.datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
    panels = "".join([
        stat_panel(16, "Contributions · 1y", human(year), "#73bf69"),
        stat_panel(162, "Current streak", str(cur), "#fade2a", "d"),
        stat_panel(308, "Longest streak", str(longest), "#ff9830", "d"),
        stat_panel(454, "Public repos", str(len(own)), "#5794f2"),
        stat_panel(600, "Stars earned", human(stars), "#b877d9"),
        stat_panel(746, "Followers", human(user["followers"]), "#00D4FF"),
    ])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="388" viewBox="0 0 900 388" role="img" aria-label="GitHub stats dashboard for {USER}: {year} contributions in the last year">
  <defs>
    <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#00D4FF" stop-opacity=".35"/><stop offset="1" stop-color="#00D4FF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="898" height="386" rx="14" fill="#111217" stroke="#2c3235"/>
  <g font-family="{SANS}">
    <rect x="16" y="14" width="10" height="20" rx="2" fill="#ff9830"/><rect x="28" y="20" width="10" height="14" rx="2" fill="#fade2a"/><rect x="40" y="10" width="10" height="24" rx="2" fill="#00D4FF"/>
    <text x="60" y="30" font-size="15" font-weight="700" fill="#ccccdc">Dashboards / <tspan fill="#ffffff">dev-ghildiyal · github-telemetry</tspan></text>
    <text x="884" y="30" text-anchor="end" font-family="{MONO}" font-size="11" fill="#8e8e8e">⟳ every 6h · last scrape {now}</text>
  </g>
  {panels}
  {timeseries(days, 16, 160, 560, 212)}
  {langs_panel(langs, 588, 160, 296, 212)}
</svg>
"""


EVENT_FMT = {
    "PushEvent": lambda e: ("🚀", f"pushed {len(e['payload']['commits'])} commit(s) to" if e["payload"].get("commits") else "pushed to"),
    "CreateEvent": lambda e: ("🌱", f"created {e['payload'].get('ref_type', 'repo')}{' `' + e['payload']['ref'] + '` in' if e['payload'].get('ref') else ''}"),
    "PullRequestEvent": lambda e: ("🔀", f"{e['payload'].get('action', 'updated')} a pull request in"),
    "IssuesEvent": lambda e: ("🐛", f"{e['payload'].get('action', 'updated')} an issue in"),
    "IssueCommentEvent": lambda e: ("💬", "commented on an issue in"),
    "WatchEvent": lambda e: ("⭐", "starred"),
    "ForkEvent": lambda e: ("🍴", "forked"),
    "ReleaseEvent": lambda e: ("📦", "published a release in"),
    "PublicEvent": lambda e: ("🔓", "open-sourced"),
}


def activity(events, limit=6):
    # collapse bursts (e.g. 12 pushes to one repo) into a single log line
    groups = []
    for e in sorted(events, key=lambda e: e["created_at"], reverse=True):
        repo = e["repo"]["name"]
        if e["type"] not in EVENT_FMT or repo == f"{USER}/{USER}":
            continue  # skip noise + bot commits to this profile repo
        if groups and groups[-1][0]["type"] == e["type"] and groups[-1][0]["repo"]["name"] == repo:
            groups[-1][1] += 1
        else:
            groups.append([e, 1])
    lines = []
    for e, n in groups[:limit]:
        repo = e["repo"]["name"]
        icon, verb = EVENT_FMT[e["type"]](e)
        if n > 1 and e["type"] == "PushEvent":
            verb = f"pushed {n} times to"
        when = dt.datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).astimezone(IST)
        lines.append(f"| `{when:%b %d · %H:%M}` | {icon} | {verb} [{repo.split('/')[-1]}](https://github.com/{repo}) |")
    if not lines:
        lines = ["| `—` | 💤 | quiet week… probably debugging YAML indentation |"]
    return "| timestamp (IST) | | event |\n|:--|:-:|:--|\n" + "\n".join(lines)


def replace_block(text, tag, body):
    return re.sub(rf"(<!-- {tag}:START -->).*?(<!-- {tag}:END -->)",
                  lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text, flags=re.S)


def main():
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
    days = calendar()
    (ROOT / "assets" / "dashboard.svg").write_text(dashboard(user, repos, days), encoding="utf-8")

    events = api(f"/users/{USER}/events/public?per_page=50")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    readme.write_text(replace_block(text, "ACTIVITY", activity(events)), encoding="utf-8")
    print(f"dashboard + activity updated ({len(days)} days of calendar data)")


if __name__ == "__main__":
    main()
