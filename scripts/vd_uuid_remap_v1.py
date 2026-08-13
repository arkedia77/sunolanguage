#!/usr/bin/env python3
"""B-1 해소 — `vd_duet3` uuid ↔ 원장 라벨 매핑 복원.

★설계 정본 = `docs/vd_uuid_remapping_preregistration.md` (커밋 bb1c84b, 값 보기 전 작성).
   방법·대조군·판정 마진을 여기서 바꾸지 않는다. 어긋나면 결과 파일에 그렇게 적는다.

실행: ~/leomusic3/.venv/bin/python scripts/vd_uuid_remap_v1.py
      (faster_whisper가 그 venv에만 있음 — 인터프리터만 읽기 사용, 타 슬롯 repo 무수정)
"""
import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path

from faster_whisper import WhisperModel

REPO = Path(__file__).resolve().parent.parent
VD = REPO / "data" / "vd_duet3"
OUT = REPO / "data" / "vd_duet3" / "VD_uuid_remap_v1.json"

# 사전등록 §1 — 리포에 기록이 있는 4건(대조군)
KNOWN = {
    "RM1": "70365338-0b63-4369-a5e3-83ad4de94bb0",
    "RM2": "7a028e80-b6f7-47ce-846c-cb919ef55b5f",
    "BL2": "28c2e16c-36e9-4e88-8bcf-aaf983f838f7",
    "G2": "35bec5aa-28b0-4d91-a4ba-b2be2bcca7af",
}
# 사전등록 §1 — 기록이 없는 4건(본 과제)
UNKNOWN_LABELS = ["M23a", "M23b", "BL1", "G1"]
UNKNOWN_UUIDS = [
    "2b33b2a6-b35d-490c-af60-b783186ad6ab",
    "3776c8d9-9c2c-4f44-ab17-9cf4cdef5ac4",
    "66621da8-7d04-4cea-b5c7-7808dbdc659c",
    "b6cb18a6-6212-4893-bbdc-5230b50c3d63",
]
MARGIN = 0.10  # 사전등록 §5


def duration(uuid):
    p = VD / "audio_final" / f"{uuid}.mp3"
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True)
    return round(float(out.stdout.strip()), 3)


def norm(s):
    return "".join(ch for ch in s if ch.isalnum())


def sim(a, b):
    """사전등록 §3 ③ — 영숫자 문자 다중집합 겹침 / min(len)."""
    ca, cb = Counter(a), Counter(b)
    if not ca or not cb:
        return 0.0
    return sum((ca & cb).values()) / min(len(a), len(b))


def transcribe(model, uuid, notes):
    """보컬 스템 우선. 없거나 전사가 비면 mp3로 재실행하고 그 사실을 남긴다(사전등록 §6 ⒞)."""
    stem = VD / "stems_final" / "htdemucs" / uuid / "vocals.wav"
    src, used = (stem, "stem") if stem.exists() else (VD / "audio_final" / f"{uuid}.mp3", "mp3(스템없음)")
    segs, _ = model.transcribe(str(src), language="ko", beam_size=5)
    segs = [{"s": round(x.start, 1), "e": round(x.end, 1), "t": x.text.strip()} for x in segs]
    if not segs and used == "stem":
        notes.append(f"{uuid[:8]}: 스템 전사 0건 → mp3 재실행")
        src, used = VD / "audio_final" / f"{uuid}.mp3", "mp3(스템전사0)"
        segs, _ = model.transcribe(str(src), language="ko", beam_size=5)
        segs = [{"s": round(x.start, 1), "e": round(x.end, 1), "t": x.text.strip()} for x in segs]
    return segs, used


def assign(labels, uuids, ledger_text, clip_text, durs, ledger_end):
    """사전등록 §3 ④ + §5. 길이 제약 위반 순열 제외 후 유사도 합 최대."""
    matrix = {u: {lb: round(sim(clip_text[u], ledger_text[lb]), 4) for lb in labels} for u in uuids}
    feasible = []
    for perm in itertools.permutations(labels):
        pair = dict(zip(uuids, perm))
        if all(durs[u] >= ledger_end[lb] for u, lb in pair.items()):
            feasible.append((sum(matrix[u][lb] for u, lb in pair.items()), pair))
    if not feasible:
        return matrix, None, "★길이 제약을 만족하는 순열이 0개 — 전체 미확정", None
    feasible.sort(key=lambda x: -x[0])
    best_score, best = feasible[0]
    runner = feasible[1] if len(feasible) > 1 else None
    verdict = {}
    for u, lb in best.items():
        ranked = sorted(matrix[u].items(), key=lambda kv: -kv[1])
        margin = round(ranked[0][1] - ranked[1][1], 4)
        ok = ranked[0][0] == lb and margin >= MARGIN
        verdict[u] = {
            "배정": lb, "1위": ranked[0], "2위": ranked[1], "마진": margin,
            "판정": "확정" if ok else f"★미확정 — 1위={ranked[0][0]}·마진 {margin} < {MARGIN}",
        }
    return matrix, best, None, {
        "최적_순열_점수": round(best_score, 4),
        "차순위_순열_점수": round(runner[0], 4) if runner else None,
        "순열_마진": round(best_score - runner[0], 4) if runner else None,
        "클립별": verdict,
    }


def main():
    ledger = json.loads((VD / "VD_final_asr.json").read_text())
    ledger_text = {k: norm("".join(s["t"] for s in v)) for k, v in ledger.items()}
    ledger_end = {k: v[-1]["e"] for k, v in ledger.items()}

    notes = []
    model = WhisperModel("medium", device="cpu", compute_type="int8")

    all_uuids = list(KNOWN.values()) + UNKNOWN_UUIDS
    durs = {u: duration(u) for u in all_uuids}
    clips, sources = {}, {}
    for u in all_uuids:
        print(f"[ASR] {u[:8]} …", flush=True)
        segs, used = transcribe(model, u, notes)
        clips[u] = {"segs": segs, "asr_end": segs[-1]["e"] if segs else None}
        sources[u] = used

    clip_text = {u: norm("".join(s["t"] for s in clips[u]["segs"])) for u in all_uuids}

    # --- 사전등록 §4 대조군: 기지 4클립을 같은 파이프라인으로 복원 ---
    ctrl_matrix, ctrl_best, ctrl_err, ctrl_v = assign(
        list(KNOWN.keys()), list(KNOWN.values()), ledger_text, clip_text, durs, ledger_end)
    truth = {v: k for k, v in KNOWN.items()}
    ctrl_hits = sum(1 for u, lb in (ctrl_best or {}).items() if lb == truth[u])
    ctrl_pass = ctrl_best is not None and ctrl_hits == 4

    result = {
        "사전등록": "docs/vd_uuid_remapping_preregistration.md (커밋 bb1c84b — 값 보기 전)",
        "블로커": "canonicalization_and_release_plan_v1.md §4 B-1",
        "크레딧": "0 — 신규 생성 없음(로컬 보존 오디오 재분석)",
        "실행환경": "~/leomusic3/.venv faster_whisper medium/cpu/int8, language=ko (타 슬롯 repo 무수정)",
        "입력_출처": sources,
        "길이_실측": durs,
        "★대조군_기지4클립": {
            "복원_정답": truth,
            "복원_결과": ctrl_best,
            "적중": f"{ctrl_hits}/4",
            "판정": "통과" if ctrl_pass else "★기각 — 방법이 기지 매핑을 복원 못 함",
            "유사도_행렬": ctrl_matrix,
            "세부": ctrl_v,
            "오류": ctrl_err,
        },
        "비고": notes,
    }

    if not ctrl_pass:
        result["본과제_미매핑4건"] = "★대조군 기각 → 사전등록 §4대로 미확정으로 남긴다(값 계산 안 함)"
    else:
        m, best, err, v = assign(UNKNOWN_LABELS, UNKNOWN_UUIDS, ledger_text, clip_text, durs, ledger_end)
        result["본과제_미매핑4건"] = {
            "배정": best, "유사도_행렬": m, "세부": v, "오류": err,
            "확정_건수": sum(1 for x in (v or {}).get("클립별", {}).values() if x["판정"] == "확정"),
        }
        result["★복원된_전체원장"] = {**truth, **{u: lb for u, lb in (best or {}).items()}}

    result["재실행_전사"] = {u: clips[u] for u in all_uuids}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k != "재실행_전사"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
