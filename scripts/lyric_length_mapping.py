#!/usr/bin/env python3
"""가사 분량 ↔ 렌더 길이 매핑 — encore CM-2026-0001 §2 역산 요청.

물음: 150~180초를 담보하려면 가사·섹션 분량이 얼마여야 하는가.

★이 스크립트가 답할 수 있는 것 / 없는 것을 먼저 못 박는다:
  할 수 있음 = **내가 오디오와 가사를 동시에 보유한 곡**에 대해 (가사 분량, 실측 초) 쌍을 만들고
              회귀 경향을 낸다.
  못 함     = **인과·담보**. 분량을 통제한 A/B가 아니고, Duration 락 설정 여부도 배치마다 모른다.
              → 「이만큼 쓰면 이 길이가 나온다」는 **보장이 아니라 관측 경향**이다.

★모집단을 결과에 반드시 동봉한다(encore E-R7 요청).
"""
import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "exchange" / "lyric_length_mapping.json"

SECTION_RE = re.compile(r'^\s*\[[^\]]+\]\s*$')
PAREN_ONLY = re.compile(r'^\s*\(')


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 2)
    except ValueError:
        return None


def lyric_stats(text):
    """가사 분량 지표. ★한국어 기준 음절≈한글 글자 수."""
    lines = [l for l in text.splitlines()]
    sung, sections = [], 0
    for l in lines:
        s = l.strip()
        if not s:
            continue
        if SECTION_RE.match(s):
            sections += 1
            continue
        # (spoken) 등 괄호 지시는 지시어만 벗기고 본문은 센다
        body = re.sub(r'^\([^)]*\)\s*', '', s)
        if not body:
            continue
        sung.append(body)
    syll = sum(len(re.findall(r'[가-힣]', l)) for l in sung)
    chars = sum(len(l.replace(" ", "")) for l in sung)
    return {"섹션태그수": sections, "가창행수": len(sung), "한글음절수": syll, "공백제외글자수": chars}


rows = []

# --- ① AWARE05 10곡 (한국어, 장르 혼합) ---
songs = json.loads((REPO / "data/aware/AWARE05_songs.json").read_text())
res = json.loads((REPO / "data/aware/AWARE05_result.json").read_text())
by_id = {s["id"]: s for s in res["songs"]}
for i, sg in enumerate(songs):
    gid = 30199 + i
    f = REPO / "data/aware/audio" / f"{gid}_t1.mp3"
    lyr = sg.get("lyrics") or sg.get("lyric") or ""
    if f.exists() and lyr:
        rows.append({"배치": "AWARE05", "곡": by_id.get(gid, {}).get("title", str(gid)),
                     "언어": "ko", "초": dur(f), **lyric_stats(lyr)})

# --- ② VD 최종 8클립 (한국어 발라드/뮤지컬/가스펠 듀엣 — 본건과 가장 가까움) ---
VD = REPO / "data/vd_duet3"
rm_lyr = json.loads((VD / "VD_REMAKE_M_v1.json").read_text()).get("lyrics", "")
v3 = json.loads((VD / "VD_LYRICS_v3.json").read_text())
CLIP2LYR = {
    "70365338-0b63-4369-a5e3-83ad4de94bb0": ("RM1(포스트록발라드)", rm_lyr),
    "7a028e80-b6f7-47ce-846c-cb919ef55b5f": ("RM2(포스트록발라드)", rm_lyr),
}


def find_v3(name_hint):
    """v3 구조에서 곡별 가사 문자열 회수."""
    out = {}

    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + "/" + k)
        elif isinstance(o, str) and len(o) > 200 and "\n" in o:
            out[p] = o
    walk(v3)
    return out


v3_lyrics = find_v3(None)
for uuid, (label, lyr) in CLIP2LYR.items():
    f = VD / "audio_final" / f"{uuid}.mp3"
    if f.exists() and lyr:
        rows.append({"배치": "VD-RM", "곡": label, "언어": "ko",
                     "초": dur(f), **lyric_stats(lyr)})

result = {
    "생성": "scripts/lyric_length_mapping.py",
    "★이_수치의_지위": "관측 경향이지 담보가 아니다. 분량 통제 A/B 아님 · Duration 락 설정 여부 배치별 미확인.",
    "모집단": {},
    "쌍": rows,
    "v3_가사후보키": list(v3_lyrics.keys()),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
print(f"쌍 {len(rows)}건")
for r in rows:
    print(f"  {r['배치']:8} {r['초']:>7}s  섹션{r['섹션태그수']:>3} 행{r['가창행수']:>3} 음절{r['한글음절수']:>4}  {r['곡'][:24]}")
print("\nv3 가사 후보 키:", list(v3_lyrics.keys()))
