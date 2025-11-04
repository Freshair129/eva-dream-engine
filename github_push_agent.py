import os, json, base64, requests, sys
from pathlib import Path
from dotenv import load_dotenv

# ใช้ .env
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
REPO  = os.getenv("GITHUB_REPO")  # รูปแบบ: username/repo-name
BRANCH = os.getenv("GITHUB_BRANCH", "main")

API_BASE = f"https://api.github.com/repos/{REPO}/contents/"

def _get_sha_if_exists(repo_path):
    url = API_BASE + repo_path + f"?ref={BRANCH}"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def push_file(local_path: str, repo_path: str, message: str = "EVA push"):
    if not TOKEN or not REPO:
        raise RuntimeError("Missing GITHUB_TOKEN or GITHUB_REPO in .env")

    content = Path(local_path).read_bytes()
    payload = {
        "message": message,
        "content": base64.b64encode(content).decode("utf-8"),
        "branch": BRANCH,
    }
    sha = _get_sha_if_exists(repo_path)
    if sha: payload["sha"] = sha  # อัปเดตไฟล์เดิม

    headers = {"Authorization": f"token {TOKEN}"}
    url = API_BASE + repo_path
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    if r.status_code in (200,201):
        print(f"OK: {repo_path}")
    else:
        print("FAIL", r.status_code, r.text)
        sys.exit(1)

def main():
    # โหมดใช้งาน:
    #  python github_push_agent.py local_path repo_path "Commit message"
    if len(sys.argv) < 3:
        print("Usage: python github_push_agent.py <local_path> <repo_path> [message]")
        sys.exit(1)
    local, remote = sys.argv[1], sys.argv[2]
    msg = sys.argv[3] if len(sys.argv) > 3 else "EVA push"
    push_file(local, remote, msg)

if __name__ == "__main__":
    main()
