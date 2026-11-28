#!/usr/bin/env python3
"""ace_bracket_test_v0.py — ACE 가사 칸 사건 줄 시험 S1(정적) · S2(드럼 빠짐/다시 들어옴) · S3(낭독) (encore 092456 결재 · brackets_v0.md ⑻).
결정적 변환(난수·모델 0). ★고침 1(encore 093358 · LEO 11-05 «기존에꺼 쓰지 말고»): 적재곡 가사·SP 재사용 0
  가사 = mora 시험 가사 3벌(agent-comm:…/ace_bracket_test_v0/lyrics/ · LEO 예외 칸 = 시험 가사) 축자 · SP = 아래 SPS 상수(손 입력 · 결 꼴만 본뜸 · 셋 다 드럼 칸 있음 = S2 자)
  손 입력 = SPS 3개 + 사건 줄 상수 3개 · 가사 줄 손댐 0 · DB songs 가사·SP와 같지 않음 = 실행 때 검사
  A  대조 = 가사 그대로(구간 이름표만 · 사건 줄 0) — S1·S2·S3 공유 대조
  S1 마지막 [Chorus] 이름표 바로 앞 줄에 SILENCE 1줄
  S2 첫 [Verse 1] 이름표 바로 뒤 DROP 1줄 + 첫 [Chorus] 이름표 바로 뒤 REENTER 1줄
곡 = 시험 곡 3(발라드 68 · 미디엄 팝 100 · 댄스 팝 120) — 가사 = 이름표만 · 사건 줄 0(mora 꼴 · 실행 때 검사)
쓰기 = agent-comm:projects/sunolanguage/exchange/ace_bracket_test_v0/inputs/{run_id}.json + manifest.json
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

OUT = Path.home() / "agent-comm-sunolanguage/projects/sunolanguage/exchange/ace_bracket_test_v0/inputs"
LYR = OUT.parent / "lyrics"
KEYS = [("B68", 68, ("ballad",)), ("P100", 100, ("mid", "medium", "pop100", "_pop")), ("D120", 120, ("dance",))]
SPS = {
    "B68": "Korean piano ballad at 68 BPM in E-flat major, slow and tender with a gentle half-time pulse. "
           "Soft acoustic piano carries the chords while warm strings rise underneath, and a brushed acoustic drum kit with a soft kick and rim clicks keeps time. "
           "A deep electric bass holds sustained root notes below the piano. "
           "A warm, breathy female lead vocal sings close to the microphone with restrained phrasing that opens up in the chorus. "
           "The song moves from intimate verses to a fuller chorus with layered harmonies and ends on a quiet piano outro.",
    "P100": "Korean mid-tempo pop at 100 BPM in G major, warm and easygoing with a light bounce in the groove. "
            "Clean electric guitar plays muted rhythmic chords over a round electric bass, and a full acoustic drum kit with a crisp snare and tight hi-hats drives the beat. "
            "Soft synth pads and a bright electric piano fill the background. "
            "A clear, friendly male lead vocal sings in a conversational tone and lifts into a catchy chorus. "
            "Verses stay light and open before the chorus adds stacked backing vocals and handclaps.",
    "D120": "Korean dance pop at 120 BPM in A minor, energetic and glossy with a punchy four-on-the-floor groove. "
            "A tight electronic drum kit with a heavy kick, crisp claps and open hi-hats drives the track over a pulsing synth bass. "
            "Bright plucked synths and shimmering pads carry the melody between vocal lines. "
            "A confident, bright female lead vocal sings with rhythmic phrasing and stacked harmonies in the hook. "
            "The arrangement builds from sparse verses through a rising pre-chorus into a full, high-energy chorus.",
}
SILENCE = "[All instruments cut out into complete silence]"
DROP = "[Drums drop out]"
REENTER = "[Full drum kit re-enters]"
ADDED = {SILENCE, DROP, REENTER}
RC = "시험 가사(mora · LEO 예외 칸) + 시험 SP(sunolanguage 손 입력) · 적재곡 0 · 발매 후보 아님 · ★가사·SP 가 ACE 에 처음 — 약관 §5 는 encore 판단(시험 글 · 발매 후보 0)"


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


def load_lyrics():
    files = sorted(p for p in LYR.iterdir() if p.suffix in (".txt", ".md", ".json"))
    got = {}
    for k, bpm, words in KEYS:
        hit = [p for p in files if any(w in p.name.lower() for w in words) or str(bpm) in p.name]
        assert len(hit) == 1, f"{k} 가사 파일 못 고름: {[p.name for p in hit]} / 전체 {[p.name for p in files]}"
        t = hit[0].read_text()
        if hit[0].suffix == ".json":
            t = json.loads(t)["lyrics"]
        got[k] = (hit[0].name, t.strip("\n"))
    return got


def main():
    from json_to_db import get_conn
    cur = get_conn().cursor()
    L = load_lyrics()
    runs = []
    for k, bpm, _ in KEYS:
        fname, ly0 = L[k]
        sp = SPS[k]
        cur.execute("select count(*) from songs where lyrics = %s or style_prompt = %s", (ly0, sp))
        assert cur.fetchone()[0] == 0, f"{k} 적재곡 글과 같음"
        ev0 = [l for l in ly0.split("\n") if l.strip().startswith("[") and not re.fullmatch(r"\[[A-Za-z -]+( \d)?\]", l.strip())]
        assert not ev0, f"{k} 가사에 이미 사건 줄: {ev0}"
        for arm, ly, test in (("A 대조(이름표만)", ly0, "S1·S2·S3 공유"), ("S1 정적 줄", s1(ly0), "S1·S3"), ("S2 드럼 빠짐/다시 들어옴", s2(ly0), "S2·S3")):
            assert lyric_lines_same(ly0, ly), (k, arm)
            rid = f"{arm.split()[0]}_{k}" if arm[0] != "A" else f"BA_{k}"
            assert len(sp) <= 1000 and len(ly) <= 5000, rid
            added = [l.strip() for l in ly.split("\n") if l.strip() in ADDED]
            runs.append({"run_id": rid, "test": test, "arm": arm, "song": k, "design_bpm": bpm, "requests": 2,
                         "model": "acemusic-v1", "mode": "custom", "lyricsMode": "own", "style_influence": 80, "exclude_styles": "",
                         "instrumental": False, "title_to_enter": rid, "SP": sp, "SP_chars": len(sp), "SP_sha256": sha(sp), "SP_source": "sunolanguage 손 입력(SPS 상수)",
                         "lyrics": ly, "lyrics_sha256": sha(ly), "lyrics_source": f"mora 시험 가사 lyrics/{fname} 축자" + ("" if ly == ly0 else " + 사건 줄"),
                         "base_lyrics_sha256": sha(ly0), "added_event_lines": added, "lyric_lines_unchanged": True,
                         "not_in_db_songs": True, "release_candidate_text": RC})
    OUT.mkdir(parents=True, exist_ok=True)
    for r in runs:
        (OUT / f"{r['run_id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    nreq = sum(r["requests"] for r in runs)
    man = {"script": "repo:sunolanguage scripts/ace_bracket_test_v0.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "lyrics_files": {k: L[k][0] for k, _, _ in KEYS},
           "requests": nreq, "credits_expected": 4 * nreq, "takes": 2 * nreq, "event_lines": sorted(ADDED),
           "results_to": "reklcli:~/encore_scratch/ace/ace_bracket_test_v0/{run_id}_r{1,2}_t{1,2}.mp3",
           "runs": [{k: r[k] for k in r if k not in ("SP", "lyrics")} for r in runs]}
    (OUT.parent / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    for r in runs:
        print(r["run_id"], r["requests"], r["SP_chars"], len(r["lyrics"]), r["added_event_lines"])
    print("requests", nreq, "cr", 4 * nreq)


if __name__ == "__main__":
    main()
