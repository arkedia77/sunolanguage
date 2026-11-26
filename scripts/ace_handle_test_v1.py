#!/usr/bin/env python3
"""ace_handle_test_v1.py — ACE 다음 시험: 느린 발라드 템포 손잡이(H1) · 보컬 성별 손잡이(H2) (encore 143538 ③ · 소리 시험 v0 뒤).
결정적 변환(난수·모델 0). SP·가사 = DB songs 축자에서 아래 규칙으로만 바꿈 · 손 입력 = 덧붙이는 틀 낱말뿐(아래 상수).
  H1 템포(41054 76 · 41058 72 · acemusic-v1):
    B 그대로(대조 · 41054 는 T1A_41054 1요청 있음 → 1요청만 더)
    W 캡션 낱말: SP 첫 «NNN BPM» → «a slow NNN BPM tempo with a half-time feel»
    L 가사 태그: 섹션 이름 태그([Intro]·[Verse]·[Chorus]·[Bridge]·[Outro] 등 · 지시 없는 것)마다 « - Slow NNN BPM» 덧붙임 · SP 그대로
  H2 성별(4079 여→남 · 41054 남→여 · acemusic-v1):
    G SP 성별 낱말 바꿈(= T5) + 섹션 이름 태그마다 « - Male Lead Vocal» / « - Female Lead Vocal» 덧붙임(ACE 가사 쓰기 꼴 · T6 «[섹션 - 지시]» 62/62)
    대조 = T1A(원래 성별) · T5(SP 만 바꿈 · 2/4)
쓰기 = agent-comm:projects/sunolanguage/exchange/ace_handle_test_v1/inputs/{run_id}.json + manifest.json
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from ace_sound_test_v0 import swap_gender

OUT = Path.home() / "agent-comm-sunolanguage/projects/sunolanguage/exchange/ace_handle_test_v1/inputs"
SECTION = re.compile(r"^\[((?:Intro|Verse|Pre-Chorus|Chorus|Post-Chorus|Hook|Bridge|Outro|Instrumental Break|Interlude)(?: \d)?)\]$", re.M)
W_TPL = r"a slow \1 BPM tempo with a half-time feel"
GENDER_TAG = {"male": "Male Lead Vocal", "female": "Female Lead Vocal"}
RC = "DB songs.status=generated · album_title 없음 · 다른 대장 못 봄"


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def tag_sections(ly, suffix):
    return SECTION.sub(lambda m: f"[{m.group(1)} - {suffix}]", ly)


def main():
    from json_to_db import get_conn
    cur = get_conn().cursor()
    gids = [41054, 41058, 4079]
    cur.execute("select global_id, style_prompt, lyrics, bpm, vocal_gender, title from songs where global_id = any(%s)", (gids,))
    S = {r[0]: dict(zip(("sp", "ly", "bpm", "vg", "title"), r[1:])) for r in cur.fetchall()}
    runs = []

    def add(rid, test, arm, g, sp, ly, rep, note="", expect_gender=None, first_in_ace=False):
        assert len(sp) <= 1000 and len(ly) <= 5000, rid
        runs.append({"run_id": rid, "test": test, "arm": arm, "gid": g, "design_bpm": S[g]["bpm"], "vocal_gender_db": S[g]["vg"],
                     "expect_gender": expect_gender or S[g]["vg"], "requests": rep, "model": "acemusic-v1", "mode": "custom", "lyricsMode": "own",
                     "style_influence": 80, "exclude_styles": "", "instrumental": False, "title_to_enter": rid,
                     "SP": sp, "SP_chars": len(sp), "SP_sha256": sha(sp), "lyrics": ly, "lyrics_sha256": sha(ly),
                     "sp_is_db_verbatim": sp == S[g]["sp"], "lyrics_is_db_verbatim": ly == S[g]["ly"],
                     "release_candidate_text": RC + (" · ★가사·SP 가 ACE 에 처음 — encore 약관 §5 확인 전엔 돌리지 말 것" if first_in_ace else " · 11-21 소리 시험 v0 때 이미 넣음"),
                     "note": note})

    for g in (41054, 41058):
        new = g == 41058
        add(f"H1B_{g}", "H1", "B 그대로(대조)", g, S[g]["sp"], S[g]["ly"], 1 if g == 41054 else 2,
            note="41054 는 T1A_41054(11-21) 1요청과 합쳐 4테이크" if g == 41054 else "", first_in_ace=new)
        w = re.sub(r"\b(\d{2,3}) ?BPM\b", W_TPL, S[g]["sp"], count=1)
        assert w != S[g]["sp"], g
        add(f"H1W_{g}", "H1", "W 캡션 «a slow NNN BPM tempo with a half-time feel»", g, w, S[g]["ly"], 2, first_in_ace=new)
        l = tag_sections(S[g]["ly"], f"Slow {S[g]['bpm']} BPM")
        assert l != S[g]["ly"], g
        add(f"H1L_{g}", "H1", "L 가사 섹션 태그 « - Slow NNN BPM»", g, S[g]["sp"], l, 2,
            note=f"태그 바꿈 {len(SECTION.findall(S[g]['ly']))}개", first_in_ace=new)
    for g in (4079, 41054):
        want = {"female": "male", "male": "female"}[S[g]["vg"]]
        sp = swap_gender(S[g]["sp"])
        ly = tag_sections(S[g]["ly"], GENDER_TAG[want])
        add(f"H2G_{g}", "H2", f"G SP 성별 바꿈 + 섹션 태그 « - {GENDER_TAG[want]}»", g, sp, ly, 2, expect_gender=want,
            note=f"대조 = T1A_{g}(원래) · T5_{g}(SP 만 바꿈) · 태그 바꿈 {len(SECTION.findall(S[g]['ly']))}개")
    OUT.mkdir(parents=True, exist_ok=True)
    for r in runs:
        (OUT / f"{r['run_id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    nreq = sum(r["requests"] for r in runs)
    man = {"script": "repo:sunolanguage scripts/ace_handle_test_v1.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "requests": nreq, "credits_expected": 4 * nreq, "takes": 2 * nreq,
           "results_to": "reklcli:~/encore_scratch/ace/ace_handle_test_v1/{run_id}_r{1,2}_t{1,2}.mp3",
           "runs": [{k: r[k] for k in r if k not in ("SP", "lyrics")} for r in runs]}
    (OUT.parent / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    for r in runs:
        print(r["run_id"], r["requests"], r["SP_chars"], r["sp_is_db_verbatim"], r["lyrics_is_db_verbatim"], r["note"])
    print("requests", nreq, "cr", 4 * nreq)


if __name__ == "__main__":
    main()
