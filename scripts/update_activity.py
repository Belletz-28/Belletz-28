"""Rigenera le sezioni dinamiche del README: progetti aggiornati di recente e attività pubblica."""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

USER = os.environ.get("GH_USER", "Belletz-28")
ORGS = [o for o in os.environ.get("GH_ORGS", "CBM-Solutions").split(",") if o]
PROFILE_REPO = f"{USER}/{USER}"
MAX_PROJECTS = 6
MAX_EVENTS = 8
API = "https://api.github.com"


def get(path):
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, headers=headers)) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        # Un endpoint che fallisce (es. org inesistente) non deve bloccare l'intero aggiornamento.
        print(f"warning: {path} -> HTTP {err.code}", file=sys.stderr)
        return []


def day(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%b %d, %Y")


def repo_link(name):
    return f"[{name}](https://github.com/{name})"


def fetch_projects():
    repos = get(f"/users/{USER}/repos?sort=pushed&per_page=30&type=owner")
    for org in ORGS:
        repos += get(f"/orgs/{org}/repos?sort=pushed&per_page=30&type=public")
    repos = [r for r in repos
             if not r["private"] and not r["fork"] and not r["archived"]
             and r["full_name"] != PROFILE_REPO]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    return repos[:MAX_PROJECTS]


def render_projects(repos):
    if not repos:
        return "_No public projects to show yet: most of my work lives in private client repositories._"
    rows = ["| Project | What it is | Stack | Last update |", "| --- | --- | --- | --- |"]
    for r in repos:
        desc = (r["description"] or "—").replace("|", "\\|")
        stars = f" ⭐ {r['stargazers_count']}" if r["stargazers_count"] else ""
        lang = f"`{r['language']}`" if r["language"] else "—"
        rows.append(f"| **{repo_link(r['full_name'])}**{stars} | {desc} | {lang} | {day(r['pushed_at'])} |")
    return "\n".join(rows)


def describe(event):
    """Ritorna (chiave di deduplica, testo) oppure None per gli eventi da ignorare."""
    repo = event["repo"]["name"]
    link = repo_link(repo)
    payload = event["payload"]
    kind = event["type"]
    if kind == "PushEvent":
        branch = payload.get("ref", "").removeprefix("refs/heads/")
        where = f" to `{branch}`" if branch else ""
        return (kind, repo, branch), f"⬆️ Pushed{where} in {link}"
    if kind == "PullRequestEvent":
        action = payload.get("action")
        pr = payload.get("pull_request") or {}
        if action == "closed" and pr.get("merged"):
            action = "merged"
        if action not in ("opened", "closed", "merged", "reopened"):
            return None
        number = pr.get("number") or payload.get("number")
        title = pr.get("title")
        url = pr.get("html_url") or f"https://github.com/{repo}/pull/{number}"
        label = f"#{number} {title}" if title else f"#{number}"
        return (kind, repo, number, action), f"🔀 {action.capitalize()} PR [{label}]({url}) in {link}"
    if kind == "IssuesEvent" and payload.get("action") in ("opened", "closed"):
        issue = payload.get("issue") or {}
        return (kind, repo, issue.get("number"), payload["action"]), \
            f"🐛 {payload['action'].capitalize()} issue [#{issue.get('number')}]({issue.get('html_url')}) in {link}"
    if kind == "ReleaseEvent" and payload.get("action") == "published":
        rel = payload.get("release") or {}
        return (kind, repo, rel.get("tag_name")), \
            f"🚀 Released [{rel.get('tag_name')}]({rel.get('html_url')}) of {link}"
    if kind == "CreateEvent" and payload.get("ref_type") == "repository":
        return (kind, repo), f"✨ Created repository {link}"
    if kind == "PublicEvent":
        return (kind, repo), f"🌍 Open-sourced {link}"
    if kind == "ForkEvent":
        return (kind, repo), f"🍴 Forked {link}"
    if kind == "WatchEvent":
        return (kind, repo), f"⭐ Starred {link}"
    return None


def render_events(events):
    items, seen = [], set()
    for event in events:
        # Il repo del profilo genera solo rumore (commit del bot, modifiche al README).
        if event["repo"]["name"] == PROFILE_REPO:
            continue
        described = describe(event)
        if not described or described[0] in seen:
            continue
        seen.add(described[0])
        items.append(f"- `{day(event['created_at'])}` · {described[1]}")
        if len(items) == MAX_EVENTS:
            break
    return "\n".join(items) or "_No recent public activity: currently heads-down on private client work._"


def replace_section(readme, name, body):
    start, end = f"<!--{name}:START-->", f"<!--{name}:END-->"
    return re.sub(f"{re.escape(start)}.*?{re.escape(end)}",
                  lambda _: f"{start}\n{body}\n{end}", readme, flags=re.S)


def main():
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    new = replace_section(readme, "RECENT_PROJECTS", render_projects(fetch_projects()))
    new = replace_section(new, "RECENT_ACTIVITY",
                          render_events(get(f"/users/{USER}/events/public?per_page=100")))
    if new != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new)


if __name__ == "__main__":
    main()
