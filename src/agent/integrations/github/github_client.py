"""GitHub REST integration (issues) using only the standard library."""

import json
import urllib.error
import urllib.request


class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.token = token

    def _request(self, method: str, url: str, body: dict | None = None):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "goat-agent"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": e.read().decode("utf-8", "replace")}

    def list_issues(self, repo: str, state: str = "open"):
        return self._request("GET", f"{self.BASE}/repos/{repo}/issues?state={state}")

    def create_issue(self, repo: str, title: str, body: str = ""):
        return self._request(
            "POST", f"{self.BASE}/repos/{repo}/issues",
            {"title": title, "body": body},
        )
