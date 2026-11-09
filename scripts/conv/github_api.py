"""GitHub REST API에서 이슈와 PR을 읽는다. 표준 라이브러리만 쓴다."""
import json
import os
import urllib.error
import urllib.request


class GitHub:
    def __init__(self, repo, token, api_url=None):
        self.repo = repo
        self.token = token
        self.api_url = api_url or os.environ.get("GITHUB_API_URL", "https://api.github.com")

    def _get(self, path):
        request = urllib.request.Request(
            f"{self.api_url}/repos/{self.repo}/{path}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "convention-check",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (404, 410):
                return None
            raise

    def issue(self, number):
        """이슈(또는 PR) 정보. 없으면 None."""
        return self._get(f"issues/{number}")

    def pull(self, number):
        return self._get(f"pulls/{number}")
