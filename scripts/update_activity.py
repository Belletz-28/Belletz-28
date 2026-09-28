"""Riscrive la sezione "Attività recente" del README con gli ultimi eventi pubblici."""
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "Belletz-28")
MAX_ITEMS = 5
START, END = "<!--RECENT_ACTIVITY:START-->", "<!--RECENT_ACTIVITY:END-->"


def fetch_events():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/events/public?per_page=50",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                 "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def describe(event):
    repo = event["repo"]["name"]
    link = f"[{repo}](https://github.com/{repo})"
    payload = event["payload"]
    kind = event["type"]
    if kind == "PushEvent":
        return f"⬆️ Push su {link}"
    if kind == "PullRequestEvent":
        return f"🔀 PR {payload['action']} in {link}"
    if kind == "IssuesEvent":
        return f"🐛 Issue {payload['action']} in {link}"
    if kind == "CreateEvent":
        return f"🆕 Creato {payload['ref_type']} in {link}"
    if kind == "WatchEvent":
        return f"⭐ Star a {link}"
    return None


def main():
    items = []
    for event in fetch_events():
        text = describe(event)
        if text and text not in items:
            items.append(text)
        if len(items) == MAX_ITEMS:
            break
    body = "\n".join(f"- {i}" for i in items) or "- Nessuna attività pubblica recente"
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    new = re.sub(f"{re.escape(START)}.*?{re.escape(END)}",
                 f"{START}\n{body}\n{END}", readme, flags=re.S)
    if new != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new)


if __name__ == "__main__":
    main()
