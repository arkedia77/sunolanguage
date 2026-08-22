#!/usr/bin/env python3
"""
merge_batch_reanalysis.py — Batch A/C(코퍼스셋 확장 2026Q2) 회신 → merged_4values.json 병합

merge_series_reanalysis.py(S시리즈 전용 일회성)의 일반화. 발주(2026-06-09):
  Batch C: 갭재선별 기존 생성곡 60 재분석 — 회신 항목당 gid + 4값(SP/가사/장르/제목)
  Batch A: 외부 악기/이펙트 40샘플 — 회신 항목당 sample id + 4값

원칙: 코퍼스 = Suno 자신의 재분석 출력만 합류. 병합 전 lyrics_sanitizer 적용
(노이즈 정규화 + 외국어혼입 등 검수 리포트 — 인제스트 게이트, Leo 지시).

회신 필드는 발주별 표기가 흔들릴 수 있어 별칭 허용:
  sp:     suno_sp | reanalysis_sp | sp
  lyrics: suno_lyrics | reanalysis_lyrics | lyrics
  genre:  suno_genre | reanalysis_genre | genre
  title:  suno_title | reanalysis_title | title
  uuid:   suno_uuid | reanalysis_uuid | uuid
  id:     gid(C) | sample_id | id

사용법:
  # 검증(기본, 쓰기 없음):
  python3 scripts/merge_batch_reanalysis.py <회신.json> --batch C
  # 실병합:
  python3 scripts/merge_batch_reanalysis.py <회신.json> --batch C --execute
이후: parse_slot_entities_v3 → incremental curated merge(사전) → 청크 재빌드
      → qdrant_incremental_upsert → 회귀 52종 → coverage_map 재산출
(build_dictionary_v3 재실행 금지 — v3.1 REGRESS)
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lyrics_sanitizer import sanitize_text

BASE = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE / "data/reanalysis_v2/merged_4values.json"
ORDER_MSG = (Path.home() / "projects/agent-comm/projects/sunomusic/messages/"
             "sunomusic_sunolanguage_20260609_143800_batchAC_발주.json")

SP_KEYS = ("suno_sp", "reanalysis_sp", "sp")
LYRICS_KEYS = ("suno_lyrics", "reanalysis_lyrics", "lyrics")
GENRE_KEYS = ("suno_genre", "reanalysis_genre", "genre")
TITLE_KEYS = ("suno_title", "reanalysis_title", "title")
UUID_KEYS = ("suno_uuid", "reanalysis_uuid", "uuid")
ID_KEYS = ("gid", "sample_id", "id", "track_id")
# ★입력층(우리가 넣은 원본) — Batch C에서 짝 대조군을 살리기 위한 확장(2026-08-22)
LEO_SP_KEYS = ("leomusic_sp", "input_sp", "prescribed_sp")
LEO_LYRICS_KEYS = ("leomusic_lyrics", "input_lyrics", "prescribed_lyrics")


def pick(item: dict, keys: tuple) -> str:
    for k in keys:
        v = item.get(k)
        if v not in (None, ""):
            return v
    return ""


def find_items(reply: dict | list, batch: str) -> list[dict]:
    """회신 JSON에서 결과 항목 리스트를 찾는다 (래핑 키 표기 흔들림 허용)."""
    if isinstance(reply, list):
        return reply
    if isinstance(reply.get("body"), dict):   # agent-comm 표준 봉투(body) 언래핑
        reply = reply["body"]
    for key in (f"batch_{batch}", f"batch_{batch.lower()}", "results", "songs",
                "items", "samples", "tracks"):
        v = reply.get(key)
        if isinstance(v, list):
            return v
        if isinstance(v, dict):   # 한 단계 중첩 (batch_C: {results: [...]})
            for kk in ("results", "songs", "items", "samples"):
                if isinstance(v.get(kk), list):
                    return v[kk]
    raise SystemExit("❌ 회신에서 결과 리스트를 찾지 못함 — 메시지 구조 확인 필요")


def load_order_index() -> dict:
    """발주 메시지의 Batch C 곡 메타(gid→title/batch_src/gap_areas) 인덱스."""
    if not ORDER_MSG.exists():
        return {}
    order = json.loads(ORDER_MSG.read_text())
    idx = {}
    for s in (order.get("batch_C") or {}).get("songs", []):
        idx[s["gid"]] = s
    return idx


def build_entry(item: dict, batch: str, order_idx: dict,
                captured_at: str) -> tuple[dict | None, list, str]:
    """회신 항목 → corpus entry. (entry, sanitize_issues, reject_reason)"""
    raw_id = pick(item, ID_KEYS)
    if raw_id in ("", None):
        return None, [], "id 없음"
    song_id = f"{batch}_{raw_id}"

    status = item.get("status", "ok")
    if status not in ("ok", "success", "generated"):
        return None, [], f"status={status}"

    sp = pick(item, SP_KEYS)
    if not sp:
        return None, [], "SP 비어있음 (4값 필수)"
    genre = pick(item, GENRE_KEYS)
    title = pick(item, TITLE_KEYS)

    lyrics_raw = pick(item, LYRICS_KEYS)
    lyrics, issues = sanitize_text(lyrics_raw) if lyrics_raw else ("", [])

    orig = order_idx.get(item.get("gid")) if batch == "C" else None

    entry = {
        "song_id": song_id,
        "title": title or (orig or {}).get("title", ""),
        "genre": genre,
        "subgenre": "",
        "bpm": item.get("bpm"),
        "key_signature": item.get("key", ""),
        "is_instrumental": bool(item.get("is_instrumental",
                                         batch == "A" and not lyrics)),
        "series": f"BATCH_{batch}",
        "leomusic_original": {
            # Batch C: 원곡은 leomusic 생성곡. 종전엔 참조 메타만 넣었으나(sp=""),
            #   그러면 그 곡이 **입력↔출력 짝 대조군에서 통째로 빠진다**(기존 BATCH_C 60건이
            #   전부 그렇게 들어가 있다). ★2026-08-22 확장: 회신이 입력층을 실어 보내면 그대로
            #   싣는다. source_gid로 나중에 DB 조인해서 채우는 길도 있으나, **조인이 필요하면
            #   그건 행 안이 아니라 밖**이고 읽는 쪽은 「없음」으로 본다. 하위호환 —
            #   회신에 필드가 없으면 종전과 동일하게 ""(기존 60건 영향 0).
            # Batch A: 외부 음원 — 원본 SP/가사 없음.
            "sp": pick(item, LEO_SP_KEYS),
            "lyrics": pick(item, LEO_LYRICS_KEYS),
            "source_gid": item.get("gid") if batch == "C" else None,
            "source_batch": (orig or {}).get("batch_src", "") if batch == "C"
                            else item.get("source", ""),
        },
        "suno_reanalysis": [{
            "uuid": pick(item, UUID_KEYS) or None,
            "sp": sp,
            "lyrics": lyrics,
            "genre": genre,
            "captured_at": captured_at,
        }],
    }
    if batch == "C" and orig:
        entry["gap_areas"] = orig.get("gap_areas", [])
    return entry, issues, ""


def main():
    ap = argparse.ArgumentParser(description="Batch A/C 재분석 회신 병합")
    ap.add_argument("reply", type=Path, help="sunomusic 회신 JSON")
    ap.add_argument("--batch", required=True, choices=["A", "C"])
    ap.add_argument("--execute", action="store_true",
                    help="실병합 (기본은 dry-run 검증)")
    args = ap.parse_args()

    reply = json.loads(args.reply.read_text())
    captured_at = (reply.get("created_at", "") if isinstance(reply, dict)
                   else "") or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    items = find_items(reply, args.batch)
    order_idx = load_order_index()

    corpus = json.loads(CORPUS_PATH.read_text())
    existing_ids = {str(r.get("song_id")) for r in corpus}
    print(f"[merge] 기존 corpus: {len(corpus)}곡 / 회신 항목: {len(items)}건 "
          f"/ batch {args.batch} {'EXECUTE' if args.execute else 'DRY-RUN'}")

    added, dup, rejected, review = 0, 0, [], 0
    for item in items:
        entry, issues, reason = build_entry(item, args.batch, order_idx, captured_at)
        if entry is None:
            rejected.append({"id": pick(item, ID_KEYS), "reason": reason})
            continue
        if entry["song_id"] in existing_ids:
            dup += 1
            continue
        for iss in issues:
            if iss["type"] != "normalized":
                review += 1
                print(f"  ⚠️ {entry['song_id']} sanitizer: {iss}")
        corpus.append(entry)
        existing_ids.add(entry["song_id"])
        added += 1

    for r in rejected:
        print(f"  ❌ reject {r['id']}: {r['reason']}")
    print(f"[merge] 추가 {added} / 중복 {dup} / 리젝트 {len(rejected)} "
          f"/ 가사 검수대상 {review}")

    if not args.execute:
        print(f"[merge] dry-run — 쓰기 없음. 병합 시 --execute")
        return
    if not added:
        print("[merge] 추가분 없음 — 쓰기 생략")
        return
    CORPUS_PATH.write_text(json.dumps(corpus, ensure_ascii=False, indent=2))
    print(f"[merge] 최종 corpus: {len(corpus)}곡 → {CORPUS_PATH}")
    print("[merge] 다음: parse_slot_entities_v3 → 청크 재빌드 → "
          "qdrant_incremental_upsert → 회귀 52종 → coverage_map")


if __name__ == "__main__":
    main()
