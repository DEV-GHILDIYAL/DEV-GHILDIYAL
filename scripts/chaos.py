"""Chaos engineering game played through GitHub issues.

A visitor opens an issue titled  chaos|<action>|<target>  and the workflow:
  1. validates it against an allow-list (issue titles are untrusted input)
  2. "breaks" the target and records how the cluster healed itself
  3. re-renders assets/cluster.svg and the CHAOS block in README.md
  4. writes the reply comment to $REPLY_FILE

Run with no env vars to just re-render from data/cluster.json.
"""
import datetime as dt
import json
import os
import random
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data" / "cluster.json"
REPO = os.environ.get("GITHUB_REPOSITORY", "DEV-GHILDIYAL/DEV-GHILDIYAL")

MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

NODES = {
    "node-a": ["ghostops", "prometheus", "grafana"],
    "node-b": ["shadowdeploy", "argocd", "api-gateway"],
    "node-c": ["cloudbill", "loki", "redis"],
}
PODS = [p for pods in NODES.values() for p in pods]

ACTIONS = {
    "kill-pod": {
        "emoji": "💀", "label": "killed",
        "heals": ["ReplicaSet spun up a fresh replica", "liveness probe failed → kubelet restarted the container",
                  "GhostOps detected CrashLoopBackOff and rolled back to last good image"],
    },
    "cpu-spike": {
        "emoji": "🔥", "label": "spiked CPU on",
        "heals": ["HPA scaled replicas 2 → 6 and back down after the spike", "VPA bumped the CPU request, throttling stopped",
                  "Karpenter added a node and rebalanced the pods"],
    },
    "net-chaos": {
        "emoji": "🌩️", "label": "injected network latency into",
        "heals": ["Istio retries + outlier detection ejected the bad endpoint", "circuit breaker tripped, traffic drained to healthy pods",
                  "ShadowDeploy flagged the p99 regression and halted the rollout"],
    },
    "oom": {
        "emoji": "🧨", "label": "memory-bombed",
        "heals": ["OOMKilled → restarted with raised limits via GitOps PR", "GhostOps root-caused a leak and paged nobody (it fixed it)",
                  "PodDisruptionBudget kept 2 replicas serving while it recovered"],
    },
}

TITLE_RE = re.compile(r"^\s*chaos\s*\|\s*([a-z-]+)\s*\|\s*([a-z-]+)\s*$", re.I)


def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"pods": {p: {"restarts": 0} for p in PODS}, "incidents": [], "agents": {}, "total": 0}


def save(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def attack(state, title, user, issue, created_at):
    m = TITLE_RE.match(title or "")
    if not m or m.group(1).lower() not in ACTIONS or m.group(2).lower() not in PODS:
        return None, (
            "🤖 **admission webhook denied the request**: I couldn't parse that chaos command.\n\n"
            f"Use the format `chaos|<action>|<pod>`.\n\n**Actions:** {', '.join(f'`{a}`' for a in ACTIONS)}\n\n"
            f"**Pods:** {', '.join(f'`{p}`' for p in PODS)}\n\n"
            f"Or just click one of the links on the [profile](https://github.com/{REPO.split('/')[0]}) 🙂")
    action, pod = m.group(1).lower(), m.group(2).lower()
    now = dt.datetime.now(dt.timezone.utc)
    try:
        opened = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        mttr = max(1, int((now - opened).total_seconds()))
    except (AttributeError, ValueError):
        mttr = random.randint(8, 40)
    heal = random.choice(ACTIONS[action]["heals"])

    state["total"] += 1
    state["pods"].setdefault(pod, {"restarts": 0})
    state["pods"][pod]["restarts"] += 1
    state["agents"][user] = state["agents"].get(user, 0) + 1
    state["incidents"].insert(0, {
        "id": state["total"], "user": user, "action": action, "pod": pod, "heal": heal,
        "mttr": mttr, "issue": issue, "at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    del state["incidents"][25:]

    reply = (
        f"{ACTIONS[action]['emoji']} **INC-{state['total']:04d}** · @{user} {ACTIONS[action]['label']} `{pod}`\n\n"
        "```console\n"
        f"$ kubectl get pod {pod} -w\n"
        f"{pod:<14} 0/1   {'Error' if action != 'cpu-spike' else 'Throttled':<17} {state['pods'][pod]['restarts']}\n"
        f"{pod:<14} 1/1   Running           {state['pods'][pod]['restarts']}\n"
        "```\n"
        f"✅ **Self-healed:** {heal}.\n\n"
        f"⏱️ Time to recovery: **{mttr}s** (measured from when you opened this issue) · zero humans paged.\n\n"
        f"The cluster has now survived **{state['total']}** chaos attacks. "
        f"Check the [profile](https://github.com/{REPO.split('/')[0]}) to see your name on the incident board. Thanks for playing!")
    return state, reply


def pod_box(x, y, name, restarts, hit):
    ring = ""
    if hit:
        ring = (f'<rect x="-4" y="-4" width="156" height="58" rx="12" fill="none" stroke="#f85149" stroke-width="2">'
                f'<animate attributeName="stroke" values="#f85149;#f85149;#3fb950;#3fb950" keyTimes="0;.4;.6;1" dur="3s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="1;.2;1" dur="1.5s" repeatCount="indefinite"/></rect>')
    return f"""<g transform="translate({x},{y})">{ring}
      <rect width="148" height="50" rx="9" fill="#0d1117" stroke="#30363d"/>
      <circle cx="16" cy="18" r="5" fill="#3fb950"><animate attributeName="opacity" values="1;.35;1" dur="{2 + (x % 7) / 5:.1f}s" repeatCount="indefinite"/></circle>
      <text x="28" y="22" font-family="{MONO}" font-size="12.5" fill="#e6edf3">{escape(name)}</text>
      <text x="16" y="40" font-family="{MONO}" font-size="10.5" fill="#7d8590">restarts: <tspan fill="{'#d29922' if restarts else '#7d8590'}">{restarts}</tspan></text>
      <text x="136" y="40" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="#3fb950">1/1</text>
    </g>"""


def render_svg(state):
    last = state["incidents"][0] if state["incidents"] else None
    nodes = []
    for i, (node, pods) in enumerate(NODES.items()):
        nx = 24 + i * 288
        boxes = "".join(pod_box(nx + 14, 132 + j * 62, p, state["pods"].get(p, {}).get("restarts", 0),
                                bool(last and last["pod"] == p)) for j, p in enumerate(pods))
        nodes.append(f"""<g>
      <rect x="{nx}" y="96" width="276" height="232" rx="12" fill="#161b22" stroke="#30363d" stroke-dasharray="4 4"/>
      <text x="{nx + 14}" y="118" font-family="{MONO}" font-size="12" fill="#7d8590">{node} · Ready</text>
      {boxes}</g>""")
    if last:
        banner = (f"{ACTIONS[last['action']]['emoji']} INC-{last['id']:04d}  @{last['user']} {ACTIONS[last['action']]['label']} "
                  f"{last['pod']} → healed in {last['mttr']}s")
    else:
        banner = "no incidents yet · be the first to break something"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="380" viewBox="0 0 900 380" role="img" aria-label="Live chaos cluster: survived {state['total']} attacks">
  <defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#30363d"/></pattern></defs>
  <rect x="1" y="1" width="898" height="378" rx="14" fill="#0d1117" stroke="#30363d"/>
  <rect x="1" y="1" width="898" height="378" rx="14" fill="url(#g)" opacity=".6"/>
  <text x="24" y="40" font-family="{SANS}" font-size="20" font-weight="800" fill="#e6edf3">prod-cluster <tspan fill="#7d8590" font-weight="400" font-size="14">· ap-south-1 · 3 nodes · 9 pods</tspan></text>
  <g transform="translate(676,20)">
    <rect width="200" height="30" rx="15" fill="#3fb950" fill-opacity=".12" stroke="#3fb950" stroke-opacity=".5"/>
    <text x="100" y="20" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="#3fb950">survived {state['total']} attacks</text>
  </g>
  <text x="24" y="72" font-family="{MONO}" font-size="12.5" fill="#d29922">{escape(banner)}</text>
  {''.join(nodes)}
  <text x="24" y="358" font-family="{MONO}" font-size="11.5" fill="#7d8590">every attack below is a real GitHub issue from a real visitor · the cluster heals itself via GitHub Actions</text>
</svg>
"""


def render_md(state):
    owner = REPO.split("/")[0]
    rows = []
    for inc in state["incidents"][:5]:
        rows.append(f"| [INC-{inc['id']:04d}](https://github.com/{REPO}/issues/{inc['issue']}) | "
                    f"[@{inc['user']}](https://github.com/{inc['user']}) | {ACTIONS[inc['action']]['emoji']} `{inc['action']}` → `{inc['pod']}` | "
                    f"{inc['heal']} | **{inc['mttr']}s** |")
    if not rows:
        rows = ["| — | *you?* | the cluster is suspiciously calm | — | — |"]
    board = sorted(state["agents"].items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
    leaders = " · ".join(f"{medals[i]} [@{u}](https://github.com/{u}) ×{n}" for i, (u, n) in enumerate(board)) or "*empty — claim the top spot*"
    return ("| incident | chaos agent | attack | how it self-healed | MTTR |\n|:--|:--|:--|:--|--:|\n"
            + "\n".join(rows) + f"\n\n**Top chaos agents:** {leaders}")


def replace_block(text, tag, body):
    return re.sub(rf"(<!-- {tag}:START -->).*?(<!-- {tag}:END -->)",
                  lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text, flags=re.S)


def render(state):
    (ROOT / "assets" / "cluster.svg").write_text(render_svg(state), encoding="utf-8")
    readme = ROOT / "README.md"
    readme.write_text(replace_block(readme.read_text(encoding="utf-8"), "CHAOS", render_md(state)), encoding="utf-8")


def main():
    state = load()
    title = os.environ.get("ISSUE_TITLE")
    if title is not None:
        new_state, reply = attack(state, title, os.environ["ISSUE_USER"], os.environ["ISSUE_NUMBER"],
                                  os.environ.get("ISSUE_CREATED_AT", ""))
        Path(os.environ.get("REPLY_FILE", "reply.md")).write_text(reply, encoding="utf-8")
        if new_state is None:
            return
        state = new_state
    save(state)
    render(state)


if __name__ == "__main__":
    main()
