# main.py
import hashlib
import hmac
import os
import json

from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from github_auth import get_installation_token
from github_client import get_pr_diff, post_pr_comment
from reviewer import review_diff

load_dotenv()

app = FastAPI()
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()

# DEBUG: print secret on startup so we can confirm it loaded
print(f"[DEBUG] WEBHOOK_SECRET loaded as: {WEBHOOK_SECRET}")

def verify_signature(payload: bytes, sig_header: str) -> bool:
    """Verify the webhook is actually from GitHub."""
    if not sig_header or not sig_header.startswith("sha256="):
        print(f"[DEBUG] Bad sig_header: {sig_header!r}")
        return False
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
    print(f"[DEBUG] EXPECTED: {expected}")
    print(f"[DEBUG] RECEIVED: {sig_header}")
    match = hmac.compare_digest(expected, sig_header)
    print(f"[DEBUG] MATCH: {match}")
    return match

@app.post("/webhook")
async def webhook(request: Request):
    payload_bytes = await request.body()

    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload_bytes, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event")
    payload = json.loads(payload_bytes)

    print(f"[DEBUG] Event: {event}")
    print(f"[DEBUG] Action: {payload.get('action')}")

    if event != "pull_request":
        print("[DEBUG] Not a PR event, ignoring")
        return {"status": "ignored"}
    if payload["action"] not in ("opened", "synchronize"):
        print("[DEBUG] Action not opened/synchronize, ignoring")
        return {"status": "ignored"}

    print("[DEBUG] Getting installation token...")
    installation_id = payload["installation"]["id"]
    token = get_installation_token(installation_id)
    print(f"[DEBUG] Token received: {token[:10]}...")

    pr = payload["pull_request"]
    repo = payload["repository"]
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    pr_number = pr["number"]

    print(f"[DEBUG] Fetching diff for {owner}/{repo_name} PR#{pr_number}...")
    diff = get_pr_diff(owner, repo_name, pr_number, token)
    print(f"[DEBUG] Diff length: {len(diff)}")

    if not diff.strip():
        print("[DEBUG] Empty diff, skipping")
        return {"status": "empty diff, skipped"}

    print("[DEBUG] Sending to Ollama for review...")
    review = review_diff(diff)
    print(f"[DEBUG] Review received, length: {len(review)}")

    comment = f"## 🤖 AI Code Review\n\n{review}\n\n---\n*Reviewed by CodeSentinelAI — powered by {os.getenv('OLLAMA_MODEL')}*"

    print("[DEBUG] Posting comment to PR...")
    post_pr_comment(owner, repo_name, pr_number, comment, token)
    print("[DEBUG] Comment posted successfully!")

    return {"status": "review posted"}

@app.get("/health")
def health():
    return {"status": "ok"}