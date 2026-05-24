# github_auth.py
import time
import jwt
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = Path(os.getenv("GITHUB_PRIVATE_KEY_PATH")).read_text()

def get_jwt_token():
    """GitHub Apps authenticate with a short-lived JWT."""
    now = int(time.time())
    payload = {
        "iat": now - 60,   # issued at (60s ago to account for clock drift)
        "exp": now + 600,  # expires in 10 minutes
        "iss": APP_ID
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

def get_installation_token(installation_id: int) -> str:
    """Exchange JWT for an installation token (scoped to one repo)."""
    jwt_token = get_jwt_token()
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    r = requests.post(url, headers={
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    })
    r.raise_for_status()
    return r.json()["token"]