<div align="center">

# 🤖 SentinelCodeAI
### AI-Powered GitHub Pull Request Reviews — Fully Local

A GitHub App that automatically reviews every pull request using a **locally hosted LLM**.  
No API key. No cloud. No cost.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-qwen2.5--coder:7b-black?style=for-the-badge)
![GitHub](https://img.shields.io/badge/GitHub-App-181717?style=for-the-badge&logo=github&logoColor=white)

<img width="800" alt="SentinelCodeAI demo" src="https://raw.githubusercontent.com/aminabk99/SentinelCodeAI/master/SentinelCodeAI_Photo.png"/>

</div>

---

## How It Works

1. Developer opens a PR → GitHub fires a webhook to the FastAPI server
2. Server verifies the HMAC-SHA256 signature and fetches the diff
3. Diff is sent to a local LLM via Ollama
4. Bot posts a structured review comment on the PR automatically

**Review covers:** 🐛 Bugs · 🔒 Security · ⚡ Performance · 💡 Suggestions · ✅ Summary

---

## Setup

**Requirements:** Python 3.11+ · [Ollama](https://ollama.com) · [ngrok](https://ngrok.com) · GitHub account

**1. Clone & install**
```bash
git clone https://github.com/aminabk99/SentinelCodeAI
cd SentinelCodeAI
python -m venv venv && source venv/Scripts/activate  # Windows
pip install fastapi uvicorn requests PyJWT cryptography python-dotenv
```

**2. Pull the model** (~4.7GB)
```bash
ollama pull qwen2.5-coder:7b
```

**3. Create a GitHub App**
- GitHub → Settings → Developer Settings → GitHub Apps → **New GitHub App**
- Permissions: Pull Requests (Read & Write), Contents (Read)
- Subscribe to: Pull request events
- Save your **App ID**, **Webhook Secret**, and download your **Private Key** (.pem)
- Install the app on your repo

**4. Configure `.env`**
```env
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=private-key.pem
GITHUB_WEBHOOK_SECRET=your_secret
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

**5. Run** (3 terminals)
```bash
ollama serve                           # Terminal 1
uvicorn main:app --reload --port 8000  # Terminal 2
ngrok http 8000                        # Terminal 3
```
Set your GitHub App Webhook URL to `https://your-ngrok-url.ngrok-free.dev/webhook`

**6. Test** — open a PR on any repo the app is installed on. The bot reviews it automatically.

---

## Hardest Part
**GitHub App auth** — short-lived JWTs signed with RSA keys, exchanged for installation-scoped tokens. A silent `401` from a mismatched webhook secret took the most debugging to crack.

## Most Interesting
**Prompt engineering shapes everything.** Adding "never hallucinate issues not in the diff" and enforcing strict output sections turned vague responses into genuinely useful reviews.

---

## Security
- `.env` and `private-key.pem` are in `.gitignore` — never commit them
- Every webhook request verified with HMAC-SHA256

## Future Improvements
- Inline comments on specific changed lines
- Severity scoring with GitHub status checks
- Claude / GPT-4 API support
- Cloud deployment for 24/7 uptime

---

<div align="center">
  <sub>Built by <a href="https://github.com/aminabk99">Amina Bilal</a> · <a href="https://linkedin.com/in/amina-bilal-926340382">LinkedIn</a></sub>
</div>
