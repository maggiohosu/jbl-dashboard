# -*- coding: utf-8 -*-
"""
JBL 대시보드 자동 업데이트
- 판매 데이터(데이터_마스터.xlsx)를 처리해서 클라우드 앱에 자동 반영
- config.json 에서 GitHub 설정을 읽음
"""

import os, sys, json, base64, urllib.request, urllib.error
from datetime import datetime

FOLDER    = os.path.dirname(os.path.abspath(__file__))
CFG_FILE  = os.path.join(FOLDER, "config.json")
DATA_FILE = os.path.join(FOLDER, "dash_data.json")
sys.path.insert(0, FOLDER)


def load_config():
    if not os.path.exists(CFG_FILE):
        print("[오류] config.json 이 없습니다. 설치_및_설정.bat 을 먼저 실행해주세요.")
        return None
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_data():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] 데이터 생성 중...")
    import data_engine as de
    data = de.generate_dash_data()
    if not data:
        print("  [오류] 데이터 생성 실패 — 데이터_마스터.xlsx 를 확인해주세요")
        return False
    print(f"  데이터 생성 완료")
    return True


def get_file_sha(token, repo, filename):
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("sha", "")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise


def upload_to_github(token, repo):
    print("  GitHub 업로드 중...")
    with open(DATA_FILE, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    sha     = get_file_sha(token, repo, "dash_data.json")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    payload = {
        "message": f"data: 자동 업데이트 {now_str}",
        "content": content_b64,
    }
    if sha:
        payload["sha"] = sha

    url  = f"https://api.github.com/repos/{repo}/contents/dash_data.json"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"  GitHub 업로드 완료!")
            return True
    except urllib.error.HTTPError as e:
        print(f"  [오류] GitHub 업로드 실패: {e.code} {e.read().decode()}")
        return False


def main():
    print("=" * 50)
    print("  JBL 대시보드 자동 업데이트")
    print(f"  실행 시각: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 50)

    cfg = load_config()
    if not cfg:
        input("\n엔터를 누르면 창이 닫힙니다...")
        return

    token = cfg.get("github_token", "")
    repo  = cfg.get("github_repo", "maggiohosu/jbl-dashboard")

    if not token:
        print("[오류] config.json 에 github_token 이 없습니다.")
        input("\n엔터를 누르면 창이 닫힙니다...")
        return

    ok = generate_data()
    if not ok:
        input("\n엔터를 누르면 창이 닫힙니다...")
        return

    upload_to_github(token, repo)

    print(f"\n완료! 클라우드 앱에서 새 데이터를 확인하세요.")
    print(f"https://jbl-dashboard-ejipjeuertrappe7z4pn9w.streamlit.app/")


if __name__ == "__main__":
    main()
