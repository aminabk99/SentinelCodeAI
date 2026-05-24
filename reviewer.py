# reviewer.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

SYSTEM_PROMPT = """You are an expert code reviewer. You will receive a git diff of a pull request.

Your job:
1. Identify real bugs or logic errors (not style preferences)
2. Flag security issues (SQL injection, hardcoded secrets, unsafe inputs)
3. Note performance concerns if significant
4. Suggest improvements only if they meaningfully change correctness or clarity

Format your response in markdown with these sections:
## 🐛 Bugs & Logic Errors
## 🔒 Security Issues  
## ⚡ Performance
## 💡 Suggestions
## ✅ Summary

Be concise. If a section has nothing to report, write "None found."
Never hallucinate issues that aren't in the diff.
"""

def review_diff(diff: str) -> str:
    # Truncate very large diffs to avoid token limits
    if len(diff) > 12000:
        diff = diff[:12000] + "\n\n[diff truncated — showing first 12000 chars]"

    prompt = f"Review this pull request diff:\n\n```diff\n{diff}\n```"

    r = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": MODEL,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.1,   # low temp = consistent, less hallucination
            "num_predict": 1000
        }
    }, timeout=600)

    r.raise_for_status()
    return r.json()["response"].strip()