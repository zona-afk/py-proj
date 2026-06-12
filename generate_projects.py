"""
Task 3 — GitHub Projects Sync 
------------------------------------------
Fetches your public GitHub repos via the GitHub API and writes
projects.json. Your portfolio site's script.js then reads this
file and displays your projects automatically.
"""

import os
import json
import requests

USERNAME = "zona-afk"  
def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos"
    params = {"sort": "updated", "per_page": 100}
    headers = {}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def build_projects(repos):
    projects = []
    for repo in repos:
        if repo.get("fork"):
            continue
        projects.append({
            "name": repo["name"],
            "description": repo.get("description") or "",
            "url": repo["html_url"],
            "language": repo.get("language") or "N/A",
            "stars": repo.get("stargazers_count", 0),
            "updated_at": repo["updated_at"],
        })
    return projects


def main():
    repos = fetch_repos()
    projects = build_projects(repos)
    with open("projects.json", "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)
    print(f"Wrote {len(projects)} projects to projects.json")


if __name__ == "__main__":
    main()
