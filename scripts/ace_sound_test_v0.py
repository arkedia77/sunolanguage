#!/usr/bin/env python3
"""ace_sound_test_v0.py — ACE 언어 팩 v0 소리 시험 T1~T5 입력 (encore 211821 승인 · 생성 = sunomusic · 측정 = encore).
결정적 변환(난수·모델 0). SP·가사 = DB songs 축자 · 손 입력 0.
  T1 우리 SP 그대로(A) vs 옮긴 판(B = acelang_reframe_v1.reframe · R1 BPM·조 장르 문장 안 · R2 믹스 문장 지움 · R4 칸 순서) — 4079·41054·71644
  T2 반영도 50 — 4079·41054 (대조 = T1-A · 반영도 80)
  T3 (고침 11-21 21:4x) 캡션 끝에 «No drums or percussion.» 1문장 — 41054·71644 (대조 = T1-A) · 제외 칸은 v1 에서 모델에 안 감(sunomusic 213501)
  T3S (덧 11-21 21:5x · encore 213648) ACE-Step 1.5(0cr) 같은 모델 짝: 제외 칸 빈 채 vs «drums, percussion» — 71016·71019(SP ≤512 · 가사 ≤2000 · drums 낱말 든 짧은 SP) · T1A와 비교 금지
  T4 가사 지시 태그 있음(A = 원문) vs 지시 태그 줄 뺌(B = 쉼표 든 [ ] 줄만 지움 · 섹션 태그는 둠) — 11645·11648 · SP 그대로 · 반영도 80
  T5 보컬 성별 바꿈(SP 안 female↔male · women↔men · girl↔boy · woman↔man) — 4079·41054 (대조 = T1-A)
쓰기 = agent-comm:projects/sunolanguage/exchange/ace_sound_test_v0/inputs/{run_id}.json + manifest.json
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from acelang_reframe_v1 import reframe

OUT = Path.home() / "agent-comm-sunolanguage/projects/sunolanguage/exchange/ace_sound_test_v0/inputs"
EXCLUDE = "drums, percussion"  # v1 에선 안 씀(모델에 안 감) · T3S(ACE-Step)에서만
NEG = "No drums or percussion."
SWAP = {"female": "male", "male": "female", "women": "men", "men": "women", "woman": "man", "man": "woman", "girl": "boy", "boy": "girl", "girls": "boys", "boys": "girls"}


RC_NOTE = "DB songs.status=generated · album_title 없음 ⇒ DB 기준 발매 후보 표시 0 (다른 대장은 못 봄) · SP 글은 11-14 ✦ 수집 v3 때 이미 ACE에 들어감 · 가사는 처음"
RC = {g: RC_NOTE for g in (4079, 41054, 71644, 11645, 11648)}
RC.update({g: "DB songs.status=generated · album_title 없음 · ★SP·가사 둘 다 ACE에 처음 — encore 약관 확인 전엔 돌리지 말 것" for g in (71016, 71019)})


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def swap_gender(sp):
    return re.sub(r"\b(" + "|".join(SWAP) + r")\b", lambda m: (SWAP[m.group(1).lower()].capitalize() if m.group(1)[0].isupper() else SWAP[m.group(1).lower()]), sp, flags=re.I)


def strip_directive_tags(ly):
    """쉼표 든 [ ] 지시 태그 줄만 지움 · 섹션 태그([Verse 1] 등)·가사 줄은 그대로."""
    out = [l for l in ly.split("\n") if not re.fullmatch(r"\s*\[[^\]]*,[^\]]*\]\s*", l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))


def main():
    from json_to_db import get_conn
    cur = get_conn().cursor()
    gids = [4079, 41054, 71644, 11645, 11648, 71016, 71019]
    cur.execute("select global_id, style_prompt, lyrics, bpm, key_signature, vocal_gender, title from songs where global_id = any(%s)", (gids,))
    S = {r[0]: dict(zip(("sp", "ly", "bpm", "key", "vg", "title"), r[1:])) for r in cur.fetchall()}
    runs = []

    def add(rid, test, arm, g, sp, ly, infl=80, excl="", note="", control_of=None, model="acemusic-v1"):
        lim = (512, 2000) if model.startswith("ace-step") else (1000, 5000)
        assert len(sp) <= lim[0] and len(ly) <= lim[1], (rid, len(sp), len(ly))
        runs.append({"run_id": rid, "test": test, "arm": arm, "gid": g, "title": S[g]["title"], "design_bpm": S[g]["bpm"], "design_key_db": S[g]["key"],
                     "vocal_gender_db": S[g]["vg"], "style_influence": infl, "exclude_styles": excl, "model": model, "mode": "custom", "lyricsMode": "own",
                     "title_to_enter": rid, "instrumental": False, "vocal_gender_field": "없음(칸 없음 · SP 문장으로만)", "release_candidate_text": RC[g],
                     "SP": sp, "SP_chars": len(sp), "SP_sha256": sha(sp), "lyrics": ly, "lyrics_sha256": sha(ly),
                     "sp_is_db_verbatim": sp == S[g]["sp"], "lyrics_is_db_verbatim": ly == S[g]["ly"], "note": note, "control_for": control_of or []})

    for g in (4079, 41054, 71644):
        ctl = {4079: ["T2", "T5"], 41054: ["T2", "T3", "T5"], 71644: ["T3"]}[g]
        add(f"T1A_{g}", "T1", "A 우리 SP 그대로", g, S[g]["sp"], S[g]["ly"], control_of=ctl)
        b, info = reframe(S[g]["sp"])
        add(f"T1B_{g}", "T1", "B 옮긴 판(R1·R2·R4)", g, b, S[g]["ly"], note=f"reframe bpm={info['bpm']} key={info['key']} 믹스 지움 {info['dropped_mix']}")
    for g in (4079, 41054):
        add(f"T2_{g}", "T2", "반영도 50", g, S[g]["sp"], S[g]["ly"], infl=50)
        sw = swap_gender(S[g]["sp"])
        assert sw != S[g]["sp"], g
        add(f"T5_{g}", "T5", "보컬 성별 바꿈", g, sw, S[g]["ly"], note=f"SP 성별 낱말 바꿈 · DB 성별 {S[g]['vg']} → 기대 {SWAP[S[g]['vg']]}")
    for g in (41054, 71644):
        add(f"T3_{g}", "T3", "캡션 끝 부정 문장(T3 고침 11-21 21:4x)", g, S[g]["sp"].rstrip() + " " + NEG, S[g]["ly"],
            note="v1 은 제외 칸을 모델에 안 보냄(sunomusic 213501 · 앱 주석) ⇒ 제외 칸 대신 캡션 끝에 부정 문장 1개")
    for g in (71016, 71019):  # T3S: ACE-Step 1.5(0cr · 제외 칸 받는 엔진) 같은 모델 안 짝 · encore 213648 · T1A와 비교 금지
        add(f"T3S_A_{g}", "T3S", "A 제외 칸 빈 채(ACE-Step 대조)", g, S[g]["sp"], S[g]["ly"], model="ace-step-1.5-xl", note="엔진 다름 · T1A와 비교 금지")
        add(f"T3S_B_{g}", "T3S", "B 제외할 스타일 «drums, percussion»(ACE-Step)", g, S[g]["sp"], S[g]["ly"], excl=EXCLUDE, model="ace-step-1.5-xl", note="엔진 다름 · T1A와 비교 금지")
    for g in (11645, 11648):
        add(f"T4A_{g}", "T4", "A 지시 태그 있음(원문)", g, S[g]["sp"], S[g]["ly"])
        st = strip_directive_tags(S[g]["ly"])
        removed = [l.strip() for l in S[g]["ly"].split("\n") if re.fullmatch(r"\s*\[[^\]]*,[^\]]*\]\s*", l)]
        add(f"T4B_{g}", "T4", "B 지시 태그 줄 뺌", g, S[g]["sp"], st, note=f"지운 태그 줄 {len(removed)}")
    OUT.mkdir(parents=True, exist_ok=True)
    for r in runs:
        (OUT / f"{r['run_id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    man = {"script": "repo:sunolanguage scripts/ace_sound_test_v0.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "requests": len(runs), "credits_expected": 4 * sum(r["model"] == "acemusic-v1" for r in runs),
           "results_to": "reklcli:~/encore_scratch/ace/ace_sound_test_v0/{run_id}_t{1,2}.mp3 (sunomusic 기본값)",
           "runs": [{k: r[k] for k in ("run_id", "test", "arm", "gid", "release_candidate_text", "design_bpm", "style_influence", "exclude_styles", "SP_chars", "SP_sha256", "lyrics_sha256", "sp_is_db_verbatim", "lyrics_is_db_verbatim", "note", "control_for")} for r in runs]}
    (OUT.parent / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
    for r in man["runs"]:
        print(r["run_id"], r["SP_chars"], r["style_influence"], r["exclude_styles"] or "-", r["sp_is_db_verbatim"], r["lyrics_is_db_verbatim"], r["note"])
    print("requests", man["requests"], "cr", man["credits_expected"])


if __name__ == "__main__":
    main()
