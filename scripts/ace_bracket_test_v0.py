#!/usr/bin/env python3
"""ace_bracket_test_v0.py — ACE 가사 칸 사건 줄 시험 S1(정적) · S2(드럼 빠짐/다시 들어옴) · S3(낭독) (encore 092456 결재 · brackets_v0.md ⑻).
결정적 변환(난수·모델 0). SP·가사 = DB songs 축자 · 손 입력 = 아래 사건 줄 상수 3개뿐(가사 줄 손댐 0 · 실행 때 검사).
  A  대조 = 가사 그대로(구간 이름표만 · 사건 줄 0) — S1·S2·S3 공유 대조
  S1 마지막 [Chorus] 이름표 바로 앞 줄에 SILENCE 1줄
  S2 첫 [Verse 1] 이름표 바로 뒤 DROP 1줄 + 첫 [Chorus] 이름표 바로 뒤 REENTER 1줄
곡 = 4079(126) · 71644(150) · 71016(88) — 가사에 사건 줄 0 · 셋 다 이미 ACE에 넣음(11-21 v0 · 71016 = T3S XL)
  ⛔41054·41058 뺌 = 가사에 이미 사건 줄 있음(«[one breath of silence]» 등 → 대조 오염)
쓰기 = agent-comm:projects/sunolanguage/exchange/ace_bracket_test_v0/inputs/{run_id}.json + manifest.json
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

OUT = Path.home() / "agent-comm-sunolanguage/projects/sunolanguage/exchange/ace_bracket_test_v0/inputs"
GIDS = [4079, 71644, 71016]
SILENCE = "[All instruments cut out into complete silence]"
DROP = "[Drums drop out]"
REENTER = "[Full drum kit re-enters]"
ADDED = {SILENCE, DROP, REENTER}
RC = "DB songs.status=generated · album_title 없음 · 다른 대장 못 봄 · 가사·SP 이미 ACE에 들어감(11-21 소리 시험 v0)"


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def is_label(l, name):
    return re.fullmatch(rf"\[{name}\]", l.strip()) is not None


def s1(ly):
    L = ly.split("\n")
    idx = [i for i, l in enumerate(L) if is_label(l, "Chorus")]
    assert idx, "Chorus 없음"
    i = idx[-1]
    j = i
    while j > 0 and not L[j - 1].strip():  # 빈 줄 건너 앞 구간 끝 줄 뒤에
        j -= 1
    return "\n".join(L[:j] + [SILENCE] + L[j:])


def s2(ly):
    L = ly.split("\n")
    v = next(i for i, l in enumerate(L) if is_label(l, "Verse 1"))
    L.insert(v + 1, DROP)
    c = next(i for i, l in enumerate(L) if is_label(l, "Chorus"))
    assert c > v, "Chorus 가 Verse 1 앞"
    L.insert(c + 1, REENTER)
    return "\n".join(L)


def lyric_lines_same(a, b):
    """덧붙인 사건 줄을 빼면 원문과 줄 단위로 같은가(가사 손댐 0 보증)."""
    return [l for l in b.split("\n") if l.strip() not in ADDED] == a.split("\n")


def main():
    from json_to_db import get_conn
    cur = get_conn().cursor()
    cur.execute("select global_id, style_prompt, lyrics, bpm, title from songs where global_id = any(%s)", (GIDS,))
    S = {r[0]: dict(zip(("sp", "ly", "bpm", "title"), r[1:])) for r in cur.fetchall()}
    runs = []
    for g in GIDS:
        ly0 = S[g]["ly"]
        ev0 = [l for l in ly0.split("\n") if l.strip().startswith("[") and not re.fullmatch(r"\[[A-Za-z -]+( \d)?\]", l.strip())]
        assert not ev0, f"{g} 가사에 이미 사건 줄: {ev0}"
        for arm, ly, test in (("A 대조(이름표만)", ly0, "S1·S2·S3 공유"), ("S1 정적 줄", s1(ly0), "S1·S3"), ("S2 드럼 빠짐/다시 들어옴", s2(ly0), "S2·S3")):
            assert lyric_lines_same(ly0, ly), (g, arm)
            rid = f"{arm.split()[0]}_{g}" if arm[0] != "A" else f"BA_{g}"
            assert len(S[g]["sp"]) <= 1000 and len(ly) <= 5000, rid
            added = [l.strip() for l in ly.split("\n") if l.strip() in ADDED]
            runs.append({"run_id": rid, "test": test, "arm": arm, "gid": g, "design_bpm": S[g]["bpm"], "requests": 2,
                         "model": "acemusic-v1", "mode": "custom", "lyricsMode": "own", "style_influence": 80, "exclude_styles": "",
                         "instrumental": False, "title_to_enter": rid, "SP": S[g]["sp"], "SP_chars": len(S[g]["sp"]), "SP_sha256": sha(S[g]["sp"]),
                         "lyrics": ly, "lyrics_sha256": sha(ly), "sp_is_db_verbatim": True, "lyrics_is_db_verbatim": ly == ly0,
                         "added_event_lines": added, "lyric_lines_unchanged": True, "release_candidate_text": RC})
    OUT.mkdir(parents=True, exist_ok=True)
    for r in runs:
        (OUT / f"{r['run_id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    nreq = sum(r["requests"] for r in runs)
    man = {"script": "repo:sunolanguage scripts/ace_bracket_test_v0.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "requests": nreq, "credits_expected": 4 * nreq, "takes": 2 * nreq, "event_lines": sorted(ADDED),
           "results_to": "reklcli:~/encore_scratch/ace/ace_bracket_test_v0/{run_id}_r{1,2}_t{1,2}.mp3",
           "runs": [{k: r[k] for k in r if k not in ("SP", "lyrics")} for r in runs]}
    (OUT.parent / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    for r in runs:
        print(r["run_id"], r["requests"], r["SP_chars"], len(r["lyrics"]), r["added_event_lines"])
    print("requests", nreq, "cr", 4 * nreq)


if __name__ == "__main__":
    main()
