#!/usr/bin/env python3
"""
sunolang - YouTube → Suno Upload → SP/송폼 추출 → DB 저장
agent-comm: sunolang/to_mukl/ 에서 요청 읽기 → sunolang/from_mukl/ 에 결과 push

요청 파일 형식 (JSON):
{
  "msg_id": "...",
  "from": "reklcli",
  "songs": [
    {"title": "원곡명", "youtube_url": "https://..."},
    ...
  ]
}
"""
from playwright.sync_api import sync_playwright
import json, os, sqlite3, subprocess, time, urllib.request, ssl
from datetime import datetime
from pathlib import Path

AGENT_COMM   = Path.home() / "projects/agent-comm"
TO_MUKL      = AGENT_COMM / "sunolang/to_mukl"
FROM_MUKL    = AGENT_COMM / "sunolang/from_mukl"
DB_PATH      = Path.home() / "projects/sunolang/sunolang.db"
RESULTS_DIR  = Path.home() / "projects/sunolang/results"
TMP_DIR      = Path("/tmp/sunolang")
TMP_DIR.mkdir(exist_ok=True)

def log(msg): print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def download_audio(youtube_url: str, out_path: str) -> bool:
    raw = out_path.replace(".mp3", "_raw.mp3")
    r = subprocess.run([
        "yt-dlp", "--no-playlist", "-x", "--audio-format", "mp3",
        "--audio-quality", "0", "--no-embed-thumbnail", "-o", raw, youtube_url
    ], capture_output=True, text=True)
    if not os.path.exists(raw):
        log(f"  다운로드 실패: {r.stderr[-200:]}")
        return False
    # 메타데이터 스트립
    subprocess.run(["ffmpeg", "-i", raw, "-map_metadata", "-1", "-c:a", "copy", out_path, "-y"],
                   capture_output=True)
    os.remove(raw)
    return os.path.exists(out_path)

def parse_prompt(prompt: str) -> tuple[str, str]:
    """prompt에서 song_form(섹션명 목록)과 song_form_desc(전체) 분리"""
    lines = [l.strip() for l in prompt.strip().split("\n") if l.strip()]
    form_sections = [l for l in lines if l.startswith("[") and not l.startswith("[[")]
    # 섹션 헤더만 (악기 설명 제외) → 대괄호 내용이 대문자로 시작하는 것
    import re
    section_headers = [l for l in form_sections
                       if re.match(r'^\[([A-Z][^\]]*)\]$', l)]
    song_form = " → ".join(h.strip("[]") for h in section_headers)
    return song_form, prompt.strip()

def upload_to_suno(page, file_path: str) -> dict | None:
    """Suno에 파일 업로드 후 UUID/tags/prompt 반환"""
    # + Audio 클릭
    page.mouse.click(269, 112)
    time.sleep(1.5)
    # Upload 클릭
    page.mouse.click(258, 208)
    time.sleep(1.5)

    # 파일 주입
    page.locator('input[type=file]').first.set_input_files(file_path)
    time.sleep(3)

    # Continue (약관, 첫 1회만)
    try:
        page.locator('button:has-text("Continue")').first.click(timeout=4000)
        time.sleep(2)
    except:
        pass

    # Save
    save_btns = page.evaluate("""
        () => Array.from(document.querySelectorAll('button'))
            .filter(el => el.offsetHeight > 0 && el.innerText.trim().startsWith('Save'))
            .map(el => ({text: el.innerText.trim(), rect: el.getBoundingClientRect()}))
    """)
    if not save_btns:
        log("  Save 버튼 없음")
        return None
    r = save_btns[0]['rect']
    page.mouse.click(r['x'] + r['width']/2, r['y'] + r['height']/2)
    time.sleep(8)

    # 피드에서 최신 클립 가져오기
    token = page.evaluate("async () => await window.Clerk.session.getToken()")
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        "https://studio-api.prod.suno.com/api/feed/v2/?page=0",
        headers={"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0"}
    )
    resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
    data = json.loads(resp.read())
    clips = [c for c in data.get("clips", []) if c.get("metadata", {}).get("type") == "upload"]
    if not clips:
        return None
    c = clips[0]
    meta = c.get("metadata", {})
    return {
        "uuid":   c["id"],
        "prompt": meta.get("prompt", ""),
        "tags":   meta.get("tags", ""),
    }

def save_to_db(conn, row: dict):
    conn.execute("""
        INSERT OR IGNORE INTO songs
        (suno_uuid, original_title, youtube_url, song_form, song_form_desc, style_prompt, created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (row["suno_uuid"], row["original_title"], row["youtube_url"],
          row["song_form"], row["song_form_desc"], row["style_prompt"],
          datetime.now().isoformat(timespec="seconds")))
    conn.commit()

def process_request_file(req_file: Path):
    with open(req_file) as f:
        req = json.load(f)

    songs = req.get("songs", [])
    msg_id = req.get("msg_id", req_file.stem)
    log(f"배치 시작: {msg_id} ({len(songs)}곡)")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    results = []

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        create_page = next((pg for pg in ctx.pages if 'suno.com/create' in pg.url), None)
        if not create_page:
            create_page = ctx.new_page()
            create_page.goto("https://suno.com/create")
            time.sleep(3)

        for i, song in enumerate(songs):
            title = song.get("title", f"unknown_{i}")
            url   = song.get("youtube_url", "")
            log(f"[{i+1}/{len(songs)}] {title}")

            # 이미 처리됐는지 확인 (같은 URL)
            exists = conn.execute("SELECT suno_uuid FROM songs WHERE youtube_url=?", (url,)).fetchone()
            if exists:
                log(f"  SKIP (이미 존재: {exists[0][:8]})")
                results.append({"title": title, "status": "skipped", "uuid": exists[0]})
                continue

            # 1. 다운로드
            mp3_path = str(TMP_DIR / f"{i:03d}.mp3")
            if not download_audio(url, mp3_path):
                results.append({"title": title, "status": "download_failed"})
                continue
            log(f"  다운로드 완료: {os.path.getsize(mp3_path)//1024}KB")

            # 2. 유튜브 탭 열어서 보여주기 (선택사항) → 탭 열고 닫기
            yt_page = ctx.new_page()
            yt_page.goto(url, timeout=10000)
            time.sleep(2)
            yt_page.close()
            log("  유튜브 탭 열고 닫음")

            # 3. Suno 업로드
            result = upload_to_suno(create_page, mp3_path)
            os.remove(mp3_path)

            if not result:
                results.append({"title": title, "status": "upload_failed"})
                continue

            song_form, song_form_desc = parse_prompt(result["prompt"])
            row = {
                "suno_uuid":      result["uuid"],
                "original_title": title,
                "youtube_url":    url,
                "song_form":      song_form,
                "song_form_desc": song_form_desc,
                "style_prompt":   result["tags"],
            }
            save_to_db(conn, row)
            results.append({"title": title, "status": "ok", "uuid": result["uuid"],
                            "song_form": song_form, "style_prompt": result["tags"][:100]})
            log(f"  완료 UUID={result['uuid'][:8]} form={song_form}")

        browser.close()

    conn.close()

    # 결과 저장
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = RESULTS_DIR / f"{now_str}_{msg_id}_result.json"
    out = {"msg_id": msg_id, "processed_at": now_str, "results": results}
    with open(result_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # agent-comm push
    from_path = FROM_MUKL / f"{now_str}_mukl_sunolang_result.json"
    with open(from_path, "w") as f:
        json.dump({
            "from": "mukl", "to": "reklcli",
            "type": "sunolang_result",
            "msg_id": msg_id,
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    subprocess.run(["git", "-C", str(AGENT_COMM), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(AGENT_COMM), "commit", "-m",
                    f"sunolang: mukl result {msg_id}"], capture_output=True)
    subprocess.run(["git", "-C", str(AGENT_COMM), "push"], capture_output=True)
    log(f"agent-comm push 완료 → {from_path.name}")

    # 처리 완료된 요청 파일 삭제
    req_file.unlink()
    log("배치 완료")

def main():
    """to_mukl/ 에서 미처리 요청 파일 확인 후 처리"""
    req_files = sorted(TO_MUKL.glob("*.json"))
    if not req_files:
        log("처리할 요청 없음")
        return
    for req_file in req_files:
        process_request_file(req_file)

if __name__ == "__main__":
    main()
