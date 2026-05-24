# github_client.py
import requests

def get_pr_diff(owner: str, repo: str, pr_number: int, token: str) -> str:
    """Fetch the raw unified diff of a pull request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    r = requests.get(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.diff"   # this header gets you raw diff
    })
    r.raise_for_status()
    return r.text

def post_pr_comment(owner: str, repo: str, pr_number: int, body: str, token: str):
    """Post a review comment on the PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    r = requests.post(url, json={"body": body}, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    })
    r.raise_for_status()
    return r.json()