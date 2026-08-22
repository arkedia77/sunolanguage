#!/usr/bin/env python3
"""metatag_b4_captions_v1.py — 블로커 B-4 「영상 자막 429 미회수」 재시도.

배경: 08-13에 A_demo 근거 영상의 자막을 받으려다 429(Too Many Requests)로 못 받았다.
     그래서 A등급 근거가 **「철자만 확인」** 상태로 남았다(계획서 §4 B-4).
★자막이 무엇을 증명하는가: 자막은 **영상 화자의 말**이지 **음원의 태그 반응**이 아니다.
  자막으로 올릴 수 있는 것은 「이 태그를 넣고 결과를 틀어 보였다고 **말했다**」까지이고,
  「그 태그가 실제로 작동했다」는 **여전히 미검증**이다. 이 한계를 산출에 박는다.

사용: .venv/bin/python scripts/metatag_b4_captions_v1.py
산출: data/metatag_external/yt/verify_v1/b4_captions_v1.json (+ *.vtt)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data/metatag_external/yt/verify_v1"
OUT = DEST / "b4_captions_v1.json"

# 08-13 A_demo 근거 영상 — verify_v1/*.description 로 이미 확보된 것들
VIDEOS = ["dxG9qPPpRnI", "sJnkHygvp6g", "Uy2jV0fqTPk", "zu7fhHtVAwU"]

DEMO_CUE = re.compile(
    r"(here'?s (what|how)|let'?s (listen|hear|play)|listen to (this|it)|"
    r"the result|what it sounds like|들어\s?보|결과(를|물)?\s?(들|보)|이렇게\s?나)", re.I)


def vtt_text(p: Path) -> str:
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if re.fullmatch(r"\d+", line):
            continue
        out.append(re.sub(r"<[^>]+>", "", line))
    # 자동자막은 같은 줄이 계단식으로 반복된다 — 연속 중복 제거
    ded = []
    for x in out:
        if not ded or ded[-1] != x:
            ded.append(x)
    return "\n".join(ded)


def main():
    import yt_dlp
    results = []
    for vid in VIDEOS:
        url = f"https://www.youtube.com/watch?v={vid}"
        rec = {"video_id": vid, "url": url}
        opts = {"quiet": True, "no_warnings": True, "skip_download": True,
                "writesubtitles": True, "writeautomaticsub": True,
                "subtitleslangs": ["en", "en-orig", "ko", "ko-orig"],
                "subtitlesformat": "vtt",
                "outtmpl": str(DEST / "%(id)s.%(ext)s")}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            rec["title"] = info.get("title")
            rec["channel"] = info.get("channel")
            rec["manual_sub_langs"] = sorted((info.get("subtitles") or {}).keys())
            rec["auto_sub_langs_n"] = len(info.get("automatic_captions") or {})
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"[:300]

        got = sorted(p.name for p in DEST.glob(f"{vid}*.vtt"))
        rec["vtt_files"] = got
        rec["★자막_회수"] = bool(got)
        if got:
            text = "\n".join(vtt_text(DEST / g) for g in got)
            rec["자막_문자수"] = len(text)
            brk = sorted(set(m.group(0) for m in re.finditer(r"\[[^\[\]\n]{2,50}\]", text)))
            rec["자막_내_브라켓표기"] = brk[:60]
            cues = [ln for ln in text.splitlines() if DEMO_CUE.search(ln)]
            rec["시연_발화_후보"] = cues[:20]
            rec["시연_발화_수"] = len(cues)
        results.append(rec)

    got_n = sum(1 for r in results if r.get("★자막_회수"))
    out = {
        "무엇": "블로커 B-4 재시도 — A_demo 근거 영상의 자막 회수",
        "재현": ".venv/bin/python scripts/metatag_b4_captions_v1.py",
        "★자막의_증명력_한계": ("자막은 영상 화자의 **말**이지 음원의 **태그 반응**이 아니다. "
                        "올릴 수 있는 최대치는 「태그를 넣고 결과를 틀어 보였다고 말했다」이고, "
                        "「그 태그가 작동했다」는 자막으로 증명되지 않는다. ⇒ A등급 승격 근거로 단독 사용 금지."),
        "대상": len(VIDEOS), "★자막_회수": got_n, "★여전히_못_봄": len(VIDEOS) - got_n,
        "결과": results,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"대상 {len(VIDEOS)} / 자막 회수 {got_n} / 못 봄 {len(VIDEOS)-got_n}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
