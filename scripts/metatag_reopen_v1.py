#!/usr/bin/env python3
"""metatag_reopen_v1.py — 2단계 ⑺ 「못 읽은 37건 재개방」 재현기.

★원칙 3개(값 보기 전에 고정한다)
 ⑴ **공개된 것만** — 오너 08-11 지시 문면. 유료벽·로그인벽은 **재시도 대상이 아니다**.
     우회 시도조차 하지 않고 `skipped_by_policy`로 분리한다. 「못 읽음」과 「안 읽기로 함」은 다른 칸.
 ⑵ **못 읽은 것은 「없음」이 아니라 「안 봄」** — 실패는 사유·상태코드·바이트까지 남긴다.
 ⑶ **경로를 바꿔서 다시 연다** — WebFetch가 403이면 curl(브라우저 UA)·리다이렉트 추적·
     유튜브는 yt-dlp. 도구를 바꾸면 열리는 자리가 실제로 있다(08-13 유튜브 선례).

사용: .venv/bin/python scripts/metatag_reopen_v1.py [--limit N]
산출: data/metatag_external/reopen_v1.json
"""
import json, subprocess, sys, time, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANES = sorted((ROOT / "data/metatag_external/v2_lanes").glob("*.json"))
OUT = ROOT / "data/metatag_external/reopen_v1.json"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0 Safari/537.36")

# ★정책 제외 — 유료벽·로그인벽. 우회 안 한다.
POLICY_SKIP = {
    "scribd.com":      "유료/가입벽 문서 뷰어 — 공개물이 아니다",
    "facebook.com":    "로그인벽 그룹 게시물 — 공개물이 아니다",
    "howtopromptsuno.com": "표 본문이 유료벽 — 무료로 보이는 범위만 이미 읽었다",
    "jackrighteous.com":   "보컬이펙트 표가 유료벽 — 무료 범위는 이미 읽었다",
}

def classify_skip(url: str):
    for host, why in POLICY_SKIP.items():
        if host in url:
            return why
    return None


def cache_path(url: str) -> Path:
    raw = ROOT / "data/metatag_external/reopen_raw"
    return raw / (re.sub(r"[^A-Za-z0-9]+", "_", url)[:90] + ".txt")


def fetch_curl(url: str, timeout=25, use_cache=True):
    """브라우저 UA + 리다이렉트 추적. WebFetch와 다른 경로.
    ★캐시가 있으면 재타격하지 않는다 — 판정 기준을 고쳤다고 남의 서버를 다시 때릴 이유는 없다."""
    cp = cache_path(url)
    if use_cache and cp.exists():
        body = cp.read_text(encoding="utf-8", errors="replace")
        return {"method": "cache(curl)", "status": 200, "final_url": url,
                "bytes": len(body.encode()), "body": body}
    cmd = ["curl", "-sL", "--compressed", "--max-time", str(timeout),
           "-A", UA, "-H", "Accept-Language: en,ko;q=0.9,zh;q=0.8,ja;q=0.7",
           "-w", "\n___HTTP___%{http_code}___%{url_effective}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
    except subprocess.TimeoutExpired:
        return {"method": "curl", "status": None, "error": "timeout", "bytes": 0}
    body = r.stdout.decode("utf-8", "replace")
    m = re.search(r"\n___HTTP___(\d+)___(.*)$", body, re.S)
    code, eff = (m.group(1), m.group(2).strip()) if m else (None, url)
    if m:
        body = body[: m.start()]
    return {"method": "curl", "status": int(code) if code else None,
            "final_url": eff, "bytes": len(body.encode()), "body": body}


def fetch_ytdlp(url: str):
    """유튜브는 페이지가 아니라 메타데이터로 연다(08-13 선례)."""
    try:
        import yt_dlp
    except ImportError:
        return {"method": "yt-dlp", "status": None, "error": "yt_dlp 미설치", "bytes": 0}
    opts = {"quiet": True, "no_warnings": True, "skip_download": True,
            "writesubtitles": False, "extract_flat": False}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return {"method": "yt-dlp", "status": None, "error": f"{type(e).__name__}: {e}"[:300], "bytes": 0}
    text = "\n".join(filter(None, [info.get("title"), info.get("description")]))
    return {"method": "yt-dlp", "status": 200, "bytes": len(text.encode()), "body": text,
            "meta": {"title": info.get("title"), "channel": info.get("channel"),
                     "duration": info.get("duration"),
                     "subtitle_langs": sorted((info.get("subtitles") or {}).keys()),
                     "auto_caption_langs": sorted((info.get("automatic_captions") or {}).keys())[:8]}}


BRACKET = re.compile(r"\[([^\[\]\n]{1,60})\]")

# ★상태코드·바이트로 「열렸다」를 판정하면 안 된다 — 2026-08-22 실측으로 걸렸다.
# old.reddit search.json은 **HTTP 200에 320KB**를 주는데 본문은 「Welcome to Reddit」
# 인터스티셜이고 가시 텍스트가 38자다. suno.com SPA도 200에 136KB인데 본문 62자(nav뿐).
# 「존재하고·파싱되고·내용만 다른」 파손이 그대로 여기서 났다. ⇒ 판정은 **가시 본문**으로 한다.
INTERSTITIAL = [
    ("Welcome to Reddit", "reddit 인터스티셜(로그인 유도)"),
    ("<title>Reddit</title>", "reddit JS 셸"),
]
MIN_VISIBLE_CHARS = 800          # 이보다 짧으면 nav/셸로 본다
MIN_TOPIC_MENTIONS = 1           # 온토픽 판정: 본문에 대상 도메인 어휘가 있는가


def visible_text(body: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def verdict(body: str, status, method: str = "curl"):
    """실질 열림 판정. 반환=(열림?, 사유)

    ★도구별로 자를 다르게 쓴다. 가시본문 800자 문턱은 **HTML 셸을 걸러내려고** 둔 것이라
    yt-dlp 산출(제목+설명 구조화 메타데이터)에 대면 **엉뚱한 자**가 된다 — 설명이 짧은 것은
    셸이 아니라 그냥 짧은 설명이다. 도구가 셸을 반환할 수 없는 경로에는 셸 검사를 안 건다.
    """
    if status != 200:
        return False, f"HTTP {status}"
    if method.startswith("yt-dlp"):
        n = len(body.strip())
        return (n > 0), (f"yt-dlp 메타데이터 회수 — 제목+설명 {n}자"
                         if n else "yt-dlp 200이나 제목·설명 비어 있음")
    for needle, why in INTERSTITIAL:
        if needle in body:
            return False, f"200이지만 {why} — 가시 본문 없음"
    vis = visible_text(body)
    if len(vis) < MIN_VISIBLE_CHARS:
        return False, f"200이지만 가시 본문 {len(vis)}자 — JS 셸/nav만"
    if len(re.findall(r"suno", vis, re.I)) < MIN_TOPIC_MENTIONS:
        return False, f"200·본문 {len(vis)}자이나 대상 어휘(suno) 0회 — 온토픽 아님"
    return True, f"가시 본문 {len(vis)}자"

def harvest(body: str):
    """★수확은 「대괄호 표기」만 세지 않는다 — v0의 추출 결함(무괄호 출처 통째로 실명)을
    반복하지 않으려고 대괄호/소괄호/꺾쇠를 같이 본다. 판정이 아니라 회수다."""
    if not body:
        return {"bracket": [], "paren_tagish": [], "angle": []}
    txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    brk = [m.group(1).strip() for m in BRACKET.finditer(txt)]
    par = [m.group(1).strip() for m in re.finditer(r"\(([^()\n]{2,40})\)", txt)]
    ang = [m.group(1).strip() for m in re.finditer(r"&lt;([^&\n]{2,40})&gt;", txt)]
    return {"bracket": brk, "paren_tagish": par, "angle": ang}


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    targets = []
    for f in LANES:
        d = json.load(open(f))
        for item in d.get("not_accessed", []):
            targets.append({"lane": f.stem, "url": item.get("url", ""),
                            "prior_reason": item.get("reason", "")})

    results, skipped = [], []
    for i, t in enumerate(targets):
        if limit and len(results) >= limit:
            break
        url = t["url"]
        why = classify_skip(url)
        if why:
            skipped.append({**t, "policy": why})
            continue
        # URL이 아닌 서술(괄호 주석 포함)은 정규화
        clean = url.split(" ")[0].strip()
        if not clean.startswith("http"):
            skipped.append({**t, "policy": "URL 아님 — 서술 항목"})
            continue
        print(f"[{i+1}/{len(targets)}] {clean[:80]}", flush=True)
        r = fetch_ytdlp(clean) if "youtube.com/watch" in clean or "youtu.be/" in clean else fetch_curl(clean)
        body = r.pop("body", "")
        opened, why = verdict(body, r.get("status"), r.get("method", "curl"))
        h = harvest(body) if opened else {"bracket": [], "paren_tagish": [], "angle": []}
        rec = {**t, **r, "★실질열림": opened, "판정사유": why,
               "가시본문자수": len(visible_text(body)) if body else 0,
               "harvest_counts": {k: len(v) for k, v in h.items()},
               "harvest_sample": {k: v[:60] for k, v in h.items()}}
        # 본문은 따로 떨군다(대용량)
        if body and r.get("status") == 200 and len(body) > 200:
            raw = ROOT / "data/metatag_external/reopen_raw"
            raw.mkdir(exist_ok=True)
            name = re.sub(r"[^A-Za-z0-9]+", "_", clean)[:90] + ".txt"
            (raw / name).write_text(body, encoding="utf-8")
            rec["raw_saved"] = f"data/metatag_external/reopen_raw/{name}"
        results.append(rec)
        time.sleep(1.2)

    ok = [r for r in results if r.get("★실질열림")]
    out = {
        "무엇": "2단계 ⑺ 못 읽은 37건 재개방 — 경로를 바꿔 다시 열어 본 결과",
        "재현": ".venv/bin/python scripts/metatag_reopen_v1.py",
        "원자료": "data/metatag_external/v2_lanes/*.json 의 not_accessed",
        "★정책_제외": {"수": len(skipped), "사유": "유료벽·로그인벽은 공개물이 아니라 재시도 대상이 아니다(오너 08-11 「공개된 것만」). 우회 시도 자체를 안 했다.",
                    "목록": skipped},
        "시도": len(results), "★열림": len(ok), "★여전히_못_봄": len(results) - len(ok),
        "★판정_기준": ("상태코드·바이트가 아니라 **가시 본문**으로 판정한다. 첫 실행에서 상태·바이트로 세어 "
                    "「열림 17」이라 적었는데 실측하면 7이었다 — old.reddit은 **200에 320KB인데 가시 본문 38자**"
                    "(「Welcome to Reddit」 인터스티셜)이고 suno.com SPA는 **200에 136KB인데 62자**(nav뿐)였다. "
                    f"기준: 가시본문 ≥{MIN_VISIBLE_CHARS}자 · 인터스티셜 아님 · 본문에 대상 어휘 1회 이상."),
        "★여전히_주의": "'실질열림'도 **읽을 수 있다**는 뜻이지 **새 표기가 있다**는 뜻이 아니다. 수확·대조는 별도 공정.",
        "결과": results,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n시도 {len(results)} / 열림 {len(ok)} / 못 봄 {len(results)-len(ok)} / 정책제외 {len(skipped)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
