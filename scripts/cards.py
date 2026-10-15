"""Generates the animated "pod" cards for featured projects -> assets/pods/*.svg

Edit PROJECTS below and run:  python scripts/cards.py
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "pods"

FONT_MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
FONT_SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

PROJECTS = [
    {
        "slug": "ghostops",
        "pod": "pod/ghostops-7c9f4d",
        "ns": "sre",
        "title": "GhostOps",
        "tagline": "AI-powered self-healing Kubernetes infrastructure",
        "lines": [
            "Detects failures, runs AI root-cause analysis and heals the",
            "cluster on its own, with chaos engineering baked in.",
        ],
        "stack": ["Kubernetes", "Prometheus", "Grafana", "Loki", "OpenTelemetry", "Python", "AWS"],
        "accent": "#00D4FF",
        "viz": "heartbeat",
    },
    {
        "slug": "shadowdeploy",
        "pod": "pod/shadowdeploy-5b21e8",
        "ns": "delivery",
        "title": "ShadowDeploy",
        "tagline": "Canary & shadow deployment platform",
        "lines": [
            "Mirrors production traffic to new versions and scores deploy",
            "confidence with AI before a single user is affected.",
        ],
        "stack": ["Kubernetes", "Istio", "ArgoCD", "GitHub Actions", "FastAPI"],
        "accent": "#A371F7",
        "viz": "shadow",
    },
    {
        "slug": "cloudbill",
        "pod": "pod/cloudbill-assassin-91aa0c",
        "ns": "finops",
        "title": "CloudBill Assassin",
        "tagline": "AWS cost optimization & FinOps automation",
        "lines": [
            "Hunts idle resources, oversized services and billing anomalies,",
            "then schedules them away. Reports managed with Terraform.",
        ],
        "stack": ["AWS Lambda", "EventBridge", "Terraform", "DynamoDB", "Boto3"],
        "accent": "#3FB950",
        "viz": "cost",
    },
]


def viz_heartbeat(a):
    # an ECG trace that flatlines, then recovers: failure -> self-heal
    path = ("M0 60 H40 L50 60 L58 30 L66 90 L74 60 H120 L130 60 L138 25 L146 95 L154 60 "
            "H200 H260 L268 60 L276 28 L284 92 L292 60 H340")
    return f"""
    <rect x="0" y="0" width="340" height="120" rx="10" fill="#0d1117" stroke="#30363d"/>
    <path d="M0 30H340M0 60H340M0 90H340" stroke="#21262d"/>
    <path d="{path}" fill="none" stroke="{a}" stroke-width="2.5" stroke-linejoin="round"
          stroke-dasharray="560" stroke-dashoffset="560">
      <animate attributeName="stroke-dashoffset" values="560;0;0" keyTimes="0;.7;1" dur="4s" repeatCount="indefinite"/>
    </path>
    <rect x="160" y="8" width="100" height="104" fill="#f85149" fill-opacity="0">
      <animate attributeName="fill-opacity" values="0;0;.12;.12;0;0" keyTimes="0;.3;.35;.5;.55;1" dur="4s" repeatCount="indefinite"/>
    </rect>
    <text x="210" y="24" text-anchor="middle" font-family="{FONT_MONO}" font-size="11" fill="#f85149" opacity="0">OOMKilled
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.3;.35;.5;.55;1" dur="4s" repeatCount="indefinite"/></text>
    <text x="300" y="24" text-anchor="middle" font-family="{FONT_MONO}" font-size="11" fill="#3fb950" opacity="0">healed ✔
      <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.6;.65;.95;1" dur="4s" repeatCount="indefinite"/></text>"""


def viz_shadow(a):
    dots = []
    for i in range(4):
        d = f"{i * 0.6:.1f}s"
        dots.append(f"""<circle r="4" fill="#3fb950"><animateMotion dur="2.4s" begin="{d}" repeatCount="indefinite" path="M20 60 H150 C190 60 190 30 230 30 H320"/></circle>
    <circle r="4" fill="{a}" opacity=".9"><animateMotion dur="2.4s" begin="{d}" repeatCount="indefinite" path="M20 60 H150 C190 60 190 90 230 90 H320"/></circle>""")
    return f"""
    <rect x="0" y="0" width="340" height="120" rx="10" fill="#0d1117" stroke="#30363d"/>
    <path d="M20 60 H150 C190 60 190 30 230 30 H320" fill="none" stroke="#3fb950" stroke-opacity=".35" stroke-width="2"/>
    <path d="M20 60 H150 C190 60 190 90 230 90 H320" fill="none" stroke="{a}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="5 5"/>
    {''.join(dots)}
    <text x="20" y="50" font-family="{FONT_MONO}" font-size="10.5" fill="#7d8590">traffic</text>
    <text x="236" y="20" font-family="{FONT_MONO}" font-size="10.5" fill="#3fb950">v1 · prod</text>
    <text x="236" y="112" font-family="{FONT_MONO}" font-size="10.5" fill="{a}">v2 · shadow</text>
    <text x="102" y="108" font-family="{FONT_MONO}" font-size="10.5" fill="#7d8590">confidence</text>
    <rect x="102" y="80" width="0" height="8" rx="4" fill="{a}">
      <animate attributeName="width" values="0;96;96" keyTimes="0;.8;1" dur="2.4s" repeatCount="indefinite"/>
    </rect>
    <rect x="102" y="80" width="96" height="8" rx="4" fill="none" stroke="#30363d"/>"""


def viz_cost(a):
    heights = [92, 86, 88, 70, 58, 44, 36, 30]
    bars = []
    for i, h in enumerate(heights):
        x = 24 + i * 38
        col = "#f85149" if i < 3 else a
        bars.append(f"""<rect x="{x}" y="{110 - h}" width="24" height="{h}" rx="4" fill="{col}" fill-opacity=".85">
      <animate attributeName="height" values="0;{h};{h}" keyTimes="0;.4;1" dur="3s" begin="{i * 0.08:.2f}s" repeatCount="indefinite"/>
      <animate attributeName="y" values="110;{110 - h};{110 - h}" keyTimes="0;.4;1" dur="3s" begin="{i * 0.08:.2f}s" repeatCount="indefinite"/>
    </rect>""")
    return f"""
    <rect x="0" y="0" width="340" height="120" rx="10" fill="#0d1117" stroke="#30363d"/>
    <path d="M10 110H330" stroke="#30363d"/>
    {''.join(bars)}
    <text x="320" y="24" text-anchor="end" font-family="{FONT_MONO}" font-size="11" fill="{a}">monthly bill ↓</text>
    <text x="24" y="24" font-family="{FONT_MONO}" font-size="11" fill="#f85149">idle EC2 · orphan EBS</text>"""


VIZ = {"heartbeat": viz_heartbeat, "shadow": viz_shadow, "cost": viz_cost}


def chips(stack, accent):
    out, x = [], 0
    for s in stack:
        w = int(len(s) * 7.2 + 18)
        out.append(f'<g transform="translate({x},0)"><rect width="{w}" height="22" rx="11" fill="{accent}" fill-opacity=".12" stroke="{accent}" stroke-opacity=".45"/>'
                   f'<text x="{w / 2}" y="15" text-anchor="middle" font-family="{FONT_MONO}" font-size="11.5" fill="#c9d1d9">{escape(s)}</text></g>')
        x += w + 8
    return "".join(out)


def card(p):
    a = p["accent"]
    lines = "".join(
        f'<text x="32" y="{124 + i * 21}" font-family="{FONT_SANS}" font-size="14.5" fill="#9da7b3">{escape(t)}</text>'
        for i, t in enumerate(p["lines"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="210" viewBox="0 0 900 210" role="img" aria-label="{escape(p['title'])}: {escape(p['tagline'])}">
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{a}" stop-opacity=".9"/><stop offset=".6" stop-color="{a}" stop-opacity="0"/>
    </linearGradient>
    <style>.pulse{{animation:p 2s ease-in-out infinite}}@keyframes p{{50%{{opacity:.3}}}}</style>
  </defs>
  <rect x="1" y="1" width="898" height="208" rx="14" fill="#0d1117" stroke="#30363d"/>
  <rect x="1" y="1" width="898" height="3" rx="1.5" fill="url(#edge)"/>
  <text x="32" y="36" font-family="{FONT_MONO}" font-size="12" fill="#7d8590">{escape(p['pod'])}  ·  ns/{escape(p['ns'])}</text>
  <g transform="translate(448,22)">
    <rect width="86" height="22" rx="11" fill="#3fb950" fill-opacity=".14" stroke="#3fb950" stroke-opacity=".5"/>
    <circle cx="14" cy="11" r="4" fill="#3fb950" class="pulse"/>
    <text x="24" y="15" font-family="{FONT_MONO}" font-size="11.5" fill="#3fb950">Running</text>
  </g>
  <text x="32" y="74" font-family="{FONT_SANS}" font-size="28" font-weight="800" fill="#e6edf3">{escape(p['title'])}</text>
  <text x="32" y="98" font-family="{FONT_SANS}" font-size="15" font-weight="600" fill="{a}">{escape(p['tagline'])}</text>
  {lines}
  <g transform="translate(32,170)">{chips(p['stack'], a)}</g>
  <g transform="translate(540,44)">{VIZ[p['viz']](a)}</g>
  <text x="868" y="190" text-anchor="end" font-family="{FONT_MONO}" font-size="11.5" fill="#7d8590">kubectl describe → click ↗</text>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for p in PROJECTS:
        (OUT / f"{p['slug']}.svg").write_text(card(p), encoding="utf-8")
        print("wrote", OUT / f"{p['slug']}.svg")
